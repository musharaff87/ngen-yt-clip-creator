import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def connect_to_google_sheet(sheet_name):
    """
    Connect to the Google Sheet using the API credentials.
    """
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Replace 'path/to/your/credentials.json' with the path to your downloaded JSON key file.
    credentials = ServiceAccountCredentials.from_json_keyfile_name("google_service.json", scope)
    client = gspread.authorize(credentials)

    # Open the Google Sheet
    sheet = client.open(sheet_name).sheet1
    return sheet

def push_video_metadata_to_sheet(sheet, video_data):
    """
    Append video metadata to the Google Sheet.
    """
    sheet.append_row([
        video_data["video_id"],
        "",
        "",
        ""
    ])
    print("[INFO] Video metadata pushed to Google Sheet.")


if __name__ == "__main__":
    sheet = connect_to_google_sheet("Youtube Track")
    push_video_metadata_to_sheet(sheet, {"video_id": "2323"})