from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import Settings
from .models import CalendarBlock

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarWriterAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.tz = ZoneInfo(settings.timezone)
        self._service = None

    def authenticate(self) -> None:
        self._service = self._build_service()

    def create_block(self, block: CalendarBlock) -> dict[str, Any]:
        service = self._service or self._build_service()
        event = {
            "id": block.event_id,
            "summary": block.title,
            "description": block.description,
            "start": {"dateTime": block.start.isoformat(), "timeZone": self.settings.timezone},
            "end": {"dateTime": block.end.isoformat(), "timeZone": self.settings.timezone},
            "extendedProperties": {"private": {"obsidianTaskId": block.source_task_id}},
        }
        try:
            created = service.events().insert(calendarId=self.settings.google_calendar_id, body=event).execute()
            return {"status": "created", "id": created.get("id"), "htmlLink": created.get("htmlLink")}
        except HttpError as exc:
            if getattr(exc, "status_code", None) == 409 or getattr(exc.resp, "status", None) == 409:
                return {"status": "duplicate", "id": block.event_id}
            raise

    def list_events_for_day(self, target_date: date) -> list[dict[str, Any]]:
        service = self._service or self._build_service()
        start = datetime.combine(target_date, time.min, tzinfo=self.tz).isoformat()
        end = datetime.combine(target_date, time.max, tzinfo=self.tz).isoformat()
        response = (
            service.events()
            .list(
                calendarId=self.settings.google_calendar_id,
                timeMin=start,
                timeMax=end,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return response.get("items", [])

    def busy_intervals_for_day(self, target_date: date) -> list[tuple[datetime, datetime]]:
        events = self.list_events_for_day(target_date)
        intervals: list[tuple[datetime, datetime]] = []
        for event in events:
            start_raw = event.get("start", {}).get("dateTime")
            end_raw = event.get("end", {}).get("dateTime")
            if not start_raw or not end_raw:
                continue
            intervals.append((datetime.fromisoformat(start_raw), datetime.fromisoformat(end_raw)))
        return intervals

    def _build_service(self):
        creds = self._load_credentials()
        return build("calendar", "v3", credentials=creds)

    def _load_credentials(self) -> Credentials:
        token_file = self.settings.google_token_file
        credentials_file = self.settings.google_credentials_file
        creds = None
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not credentials_file.exists():
                    raise FileNotFoundError(f"Google credentials file not found: {credentials_file}")
                flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
                creds = flow.run_local_server(port=0)
            token_file.write_text(creds.to_json(), encoding="utf-8")
        return creds
