import base64
import json
import random
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import time 
from googleapiclient.errors import HttpError

from gmail_client import get_service

QUERY = "newer_than:60d -in:sent -in:drafts -in:spam -in:trash"
SAMPLE_SIZE = 200
DEV_SIZE = 130
MAX_BODY = 4000
SEED = 42
OUT = Path(__file__).parent / "data" / "real_emails.json"


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def _html_to_text(html: str) -> str:
    p = _TextExtractor()
    p.feed(html)
    return " ".join(p.parts)


def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="replace")


def _find_part(payload: dict, mime: str):
    if payload.get("mimeType") == mime and payload.get("body", {}).get("data"):
        return _decode(payload["body"]["data"])
    for part in payload.get("parts") or []:
        found = _find_part(part, mime)
        if found:
            return found
    return None


def _body(payload: dict) -> str:
    text = _find_part(payload, "text/plain")
    if text is None:
        html = _find_part(payload, "text/html")
        text = _html_to_text(html) if html else ""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    return text[:MAX_BODY]


def list_ids(service) -> list[str]:
    ids, token = [], None
    while True:
        resp = service.users().messages().list(
            userId="me", q=QUERY, pageToken=token, maxResults=500
        ).execute()
        ids += [m["id"] for m in resp.get("messages", [])]
        token = resp.get("nextPageToken")
        if not token:
            return ids


def fetch_one(service, msg_id: str) -> dict:
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
    received = (
        datetime.fromtimestamp(int(msg["internalDate"]) / 1000, tz=timezone.utc)
        .astimezone()
        .isoformat(timespec="seconds")
    )
    return {
        "id": msg_id,
        "from": headers.get("from", ""),
        "received": received,
        "subject": headers.get("subject", ""),
        "body": _body(msg["payload"]),
    }
    
def fetch_with_retry(service, msg_id: str, tries: int = 7) -> dict:
    delay = 2
    for attempt in range(tries):
        try:
            return fetch_one(service, msg_id)
        except HttpError as e:
            rate_limited = e.resp.status in (429, 500, 502, 503, 504) or (
                e.resp.status == 403 and "rateLimitExceeded" in str(e)
            )
            if not rate_limited or attempt == tries - 1:
                raise
            print(f"  rate limited, waiting {delay}s...")
            time.sleep(delay)
            delay *= 2


def main() -> None:
    service = get_service()
    ids = list_ids(service)
    print(f"{len(ids)} messages match the query")

    sample = random.Random(SEED).sample(ids, min(SAMPLE_SIZE, len(ids)))
    emails = []
    for i, msg_id in enumerate(sample):
        e = fetch_with_retry(service, msg_id)
        e["split"] = "dev" if i < DEV_SIZE else "heldout"
        emails.append(e)
        time.sleep(0.2)
        if (i + 1) % 25 == 0:
            print(f"  fetched {i + 1}/{len(sample)}")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(emails, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved {len(emails)} emails to {OUT}")


if __name__ == "__main__":
    main()