#!/usr/bin/env python3
import os
import pickle
import logging
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SOURCE_PATH = "/Users/elyons/Google Drive/My Drive/othertrax/"
SHEET_ID = "1P_bYUH3_G0U9BHfLenUMP6jnlUqYctFgUZOd-6hzt1o"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_FILE = "token.pickle"
CREDS_FILE = "/Users/elyons/projects/kf-offmenu/credentials.json"

logging.basicConfig(
    filename="/var/tmp/kf-offmenu.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_creds():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return creds


def list_tracks():
    rows = []
    for fname in sorted(os.listdir(SOURCE_PATH)):
        if fname.endswith(".mp4"):
            name = fname[:-4]
            parts = name.split(" - ", 1)
            artist, title = (parts[0], parts[1]) if len(parts) == 2 else (parts[0], "")
            rows.append([artist, title])
    return rows


def update_sheet(rows):
    service = build("sheets", "v4", credentials=get_creds())
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="A:A").execute()
    before = len(result.get("values", []))
    sheet.values().update(
        spreadsheetId=SHEET_ID,
        range="A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()
    after = len(rows)
    logging.info(f"Updated sheet: {before} -> {after} records (change: {after - before:+d})")


if __name__ == "__main__":
    try:
        update_sheet(list_tracks())
    except Exception as e:
        logging.error(f"Failed: {e}")
