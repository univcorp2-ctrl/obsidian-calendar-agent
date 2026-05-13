from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from .config import load_settings
from .orchestrator import ObsidianCalendarOrchestrator

settings = load_settings()
orchestrator = ObsidianCalendarOrchestrator(settings)
app = FastAPI(
    title="Obsidian Calendar Agent",
    version="0.1.0",
    description="Sync Obsidian Markdown tasks to Google Calendar hourly blocks and Telegram daily digests.",
)
scheduler: Optional[AsyncIOScheduler] = None


class SyncRequest(BaseModel):
    date: Optional[str] = None
    dry_run: bool = False


class DigestRequest(BaseModel):
    date: Optional[str] = None


def _now_date() -> date:
    return datetime.now(ZoneInfo(settings.timezone)).date()


def _target_date(value: Optional[str]) -> date:
    if value:
        return datetime.strptime(value, "%Y-%m-%d").date()
    return _now_date()


def require_api_key(x_api_key: str = Header(default="")) -> None:
    if settings.agent_api_key and x_api_key != settings.agent_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/sync/today", dependencies=[Depends(require_api_key)])
def sync_today(request: SyncRequest) -> dict:
    return orchestrator.sync_day(_target_date(request.date), dry_run=request.dry_run)


@app.get("/digest/today", dependencies=[Depends(require_api_key)])
def digest_today(date: Optional[str] = None) -> dict:
    return orchestrator.build_digest_text(_target_date(date))


@app.post("/telegram/send-today", dependencies=[Depends(require_api_key)])
async def telegram_today(request: DigestRequest) -> dict:
    return await orchestrator.send_today_digest(_target_date(request.date))


async def scheduled_telegram_digest() -> None:
    await orchestrator.send_today_digest(_now_date())


def scheduled_calendar_sync() -> None:
    orchestrator.sync_day(_now_date(), dry_run=False)


@app.on_event("startup")
async def start_scheduler() -> None:
    global scheduler
    if not settings.enable_scheduler:
        return
    scheduler = AsyncIOScheduler(timezone=settings.timezone)
    scheduler.add_job(scheduled_calendar_sync, "interval", hours=1)
    hour, minute = [int(part) for part in settings.daily_digest_time.split(":", 1)]
    scheduler.add_job(scheduled_telegram_digest, "cron", hour=hour, minute=minute)
    scheduler.start()


@app.on_event("shutdown")
async def stop_scheduler() -> None:
    if scheduler:
        scheduler.shutdown()
