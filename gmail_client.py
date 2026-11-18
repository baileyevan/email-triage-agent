from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
SECRETS = Path(__file__).parent / "secrets"
CLIENT_SECRET = SECRETS / "client_secret.json"
TOKEN = SECRETS / "token.json"


def get_service():
    creds = None
    if TOKEN.exists() and TOKEN.stat().st_size > 0:
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
        except ValueError:
            creds = None  # unreadable token file: sign in again

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            creds = None  # token expired or revoked: sign in again

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
        creds = flow.run_local_server(port=0)

    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds)


if __name__ == "__main__":
    service = get_service()
    profile = service.users().getProfile(userId="me").execute()
    print("Signed in as:", profile["emailAddress"])
    print("Messages in mailbox:", profile["messagesTotal"])