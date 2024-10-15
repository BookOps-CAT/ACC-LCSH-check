import os
import time
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from acc_lcsh_check.lcsh import LCTerm


def configure_sheet() -> Credentials:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    cred_path = os.path.join(
        os.environ["USERPROFILE"], ".cred/.google/lcsh-checker.json"
    )
    token_path = os.path.join(
        os.environ["USERPROFILE"], ".cred/.google/lcsh-token.json"
    )

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server()
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds


def write_delete_sheet(values: list, creds: Credentials) -> None:
    """
    A function to append data to a google sheet
    """
    if not creds or not creds.valid:
        creds = configure_sheet()
    try:
        service = build("sheets", "v4", credentials=creds)

        body = {
            "majorDimension": "ROWS",
            "range": "BPLAuth_Verify240930!A2:D100000",
            "values": values,
        }
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId="1ljT9VxzdhuKHuYp9MhfOLcPxqfF6VgstKMSQgRELm-M",
                range="BPLAuth_Verify240930!A2:D100000",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
        return result
    except HttpError as error:
        return error


def get_lc_results(row) -> list:
    term = LCTerm(row.iloc[2], row.iloc[3])
    out_data = [
        row.iloc[0],
        row.iloc[1],
        term.id,
        term.old_heading,
        term.is_deprecated,
        term.status_code,
        term.current_heading,
    ]
    return out_data


if __name__ in "__main__":
    """open a csv file to and yield the next row"""
    df = pd.read_csv(
        "data/backstage/BPLAuth_Verify240930.txt",
        sep=",",
        names=["RECORD_NUMBER", "LCCN", "heading1", "heading2", "heading3"],
        header=0,
    )
    df.fillna("", inplace=True)
    df["NORMALIZED_LCCN"] = df["LCCN"].str.replace(" ", "")
    df["HEADING_FROM_MARC_FILE"] = df.apply(
        lambda row: " ".join(
            (str(row["heading1"]), str(row["heading2"]), str(row["heading3"]))
        ).strip(),
        axis=1,
    )
    df.drop(["heading1", "heading2", "heading3"], axis=1, inplace=True)
    df.index += 1
    ranges = [(i + 1, i + 100) for i in range(9528, len(df), 100)]
    ranges.pop(-1)
    ranges.append((ranges[-1][1], len(df) + 1))
    for item in ranges:
        chunk = df.loc[item[0] : item[1]]  # noqa: E203
        start = time.time()
        out_data = pd.DataFrame(
            data=None,
            columns=[
                "RECORD_NUMBER",
                "LCCN",
                "NORMALIZED_LCCN",
                "HEADING_FROM_MARC_FILE",
                "DEPRECATED",
                "STATUS_CODE",
                "HEADING_FROM_LC",
            ],
        )
        out_data = chunk.apply(get_lc_results, axis=1).apply(pd.Series)
        out_data["COUNT"] = out_data.index.to_series().apply(
            lambda x: f"{x} of {len(df)}"
        )
        record_count = out_data.pop("COUNT")
        out_data.insert(0, "COUNT", record_count)
        end = time.time()
        df.fillna("", inplace=True)
        creds = configure_sheet()
        write_delete_sheet(out_data.values.tolist(), creds)
        print(f"Records {item[0]} to {item[1]} took {end - start} seconds to run.")
