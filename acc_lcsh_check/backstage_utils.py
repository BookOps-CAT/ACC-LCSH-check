import datetime
import json
import os

import pandas as pd
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore


def configure_sheet() -> Credentials:
    """
    Get or refresh token for Google Sheets API.

    Args:
        None

    Returns:
        google.oauth2.credentials.Credentials: Credentials object for google sheet API.
    """
    load_creds()
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    token_dict = {
        "token": os.getenv("token"),
        "refresh_token": os.getenv("refresh_token"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": os.getenv("client_id"),
        "client_secret": os.getenv("client_secret"),
        "scopes": scopes,
        "universe_domain": "googleapis.com",
        "account": "",
        "expiry": "2024-11-06T15:15:43.146164Z",
    }
    flow_dict = {
        "installed": {
            "client_id": os.getenv("client_id"),
            "client_secret": os.getenv("client_secret"),
            "project_id": "LCSH-check",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost"],
        }
    }

    try:
        creds = Credentials.from_authorized_user_info(token_dict)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_config(flow_dict, scopes)
            creds = flow.run_local_server()
        return creds
    except (ValueError, RefreshError):
        raise


def get_date() -> str:
    today = datetime.datetime.now(tz=datetime.timezone.utc)
    return datetime.datetime.strftime(today, "%y%m%d")


def get_batches(dataframe: pd.DataFrame, start: int = 0) -> list:
    ranges = [(i + 1, i + 100) for i in range(start, len(dataframe), 100)]
    ranges.pop(-1)
    ranges.append((ranges[-1][1], len(dataframe) + 1))
    return ranges


def load_creds() -> None:
    """Load Google Sheet API credentials from JSON file and set as env vars"""
    token_file = os.path.join(
        os.environ["USERPROFILE"], ".cred/.google/lcsh-token.json"
    )

    with open(token_file, "r") as fh:
        for k, v in json.load(fh).items():
            os.environ[k] = v


def process_csv(filename: str) -> pd.DataFrame:
    out_file = f"{filename.rsplit('/', maxsplit=1)[0]}/BPLAuth_Verify{get_date()}.txt"
    if os.path.exists(out_file):
        return pd.read_csv(out_file, header=0, index_col=0)
    cols = ["RECORD_NUMBER", "LCCN", "heading1", "heading2", "heading3"]
    df = pd.read_csv(filename, sep="|", names=cols, header=0)
    df = df.fillna("")
    df["NORMALIZED_LCCN"] = df["LCCN"].str.replace(" ", "")
    df["HEADING_FROM_MARC_FILE"] = df[["heading1", "heading2", "heading3"]].apply(
        lambda row: " ".join(row).strip(), axis=1
    )
    df.drop(["heading1", "heading2", "heading3"], axis=1, inplace=True)
    df.index += 1
    df.to_csv(out_file)
    return df


def write_delete_sheet(data: pd.DataFrame, spreadsheet_id: str) -> dict:
    """
    A function to append data to a google sheet
    """
    range = f"BPLAuth_Verify{get_date()}!A2:D100000"
    spreadsheet = spreadsheet_id
    try:
        creds = configure_sheet()
        service = build("sheets", "v4", credentials=creds)

        body = {
            "majorDimension": "ROWS",
            "range": range,
            "values": data.values.tolist(),
        }
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet,
                range=range,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
                includeValuesInResponse=True,
            )
            .execute()
        )
        return result
    except (HttpError, TimeoutError):
        raise
