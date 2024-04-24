import os.path
from pymarc import MARCReader
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from acc_lcsh_check.lcsh import LCTerm


def write_delete_sheet(
    spreadsheet_id, range_name, value_input_option, insert_data_option, values
):
    """
    A function to append data to a google sheet
    """
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

    try:
        service = build("sheets", "v4", credentials=creds)

        body = {
            "majorDimension": "ROWS",
            "range": range_name,
            "values": values,
        }
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                insertDataOption=insert_data_option,
                body=body,
            )
            .execute()
        )
        return result
    except HttpError as error:
        return error


if __name__ in "__main__":
    file_list = [
        "NAME-Q-230627DEL.MRC",
        "NAME.DEL-Q-231226.MRC",
        "NAME-DEL-Q-230926.MRC",
        "SUBJ.DEL-Q-231226.MRC",
        "SUBJDEL-Q-230926.MRC",
        "SUBJ-Q-230627DEL.MRC",
    ]
    id_list = []
    for file in file_list:
        print(file)
        with open(f"data/backstage/{file}", "rb") as fh:
            reader = MARCReader(fh)
            for record in reader:
                control_no = record["001"].data
                record_id = control_no.replace(" ", "")
                heading_fields = []
                for field in record.fields:
                    if field.tag[0:1] == "1":
                        heading_fields.append(field.tag)
                if len(heading_fields) == 1:
                    tag = str(heading_fields[0])
                    record_heading = record[tag].value()
                id_list.append(
                    (
                        record_id,
                        record_heading,
                        file,
                    )
                )
    print(len(id_list))
    for item in id_list:
        term = LCTerm(item[0], item[1])
        out_data = [
            [
                item[2],
                term.id,
                term.old_heading,
                term.is_deprecated,
                term.status_code,
                term.current_heading,
            ]
        ]
        print(out_data)
        write_delete_sheet(
            "1ljT9VxzdhuKHuYp9MhfOLcPxqfF6VgstKMSQgRELm-M",
            "Headings!A1:D100000",
            "USER_ENTERED",
            "INSERT_ROWS",
            out_data,
        )
