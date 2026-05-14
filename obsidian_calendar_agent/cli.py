from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime

from .config import load_settings
from .crm.roadmap import ExternalCliReviewAgent, ObsidianRoadmapWriter, RoadmapPlannerAgent, commands_from_env
from .google_calendar import GoogleCalendarWriterAgent
from .orchestrator import ObsidianCalendarOrchestrator


def _parse_date(value: str | None):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else datetime.now().date()


def main() -> None:
    parser = argparse.ArgumentParser(description="Obsidian to Google Calendar agent")
    sub = parser.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("auth-google", help="Run Google OAuth flow and create token.json")
    auth.set_defaults(func=cmd_auth_google)

    sync = sub.add_parser("sync", help="Sync Obsidian tasks to Google Calendar")
    sync.add_argument("--date", help="Target date YYYY-MM-DD")
    sync.add_argument("--dry-run", action="store_true")
    sync.set_defaults(func=cmd_sync)

    telegram = sub.add_parser("telegram-today", help="Send today's digest to Telegram")
    telegram.add_argument("--date", help="Target date YYYY-MM-DD")
    telegram.set_defaults(func=cmd_telegram_today)

    roadmap = sub.add_parser("roadmap-weekly", help="Create weekly Friday targets from the 10-year roadmap")
    roadmap.add_argument("--start-date", help="Start date YYYY-MM-DD. Defaults to today.")
    roadmap.add_argument("--weeks", type=int, default=4, help="Number of Friday targets to generate. Default: 4")
    roadmap.add_argument("--write", action="store_true", help="Write generated targets into Obsidian Daily Friday notes")
    roadmap.add_argument("--review", action="store_true", help="Run local CLI AI review commands before writing")
    roadmap.add_argument(
        "--review-command",
        action="append",
        default=[],
        help="Local CLI command. Use {input} placeholder for the generated prompt file. Can be repeated.",
    )
    roadmap.add_argument("--json", action="store_true", help="Print machine-readable JSON instead of markdown")
    roadmap.set_defaults(func=cmd_roadmap_weekly)

    args = parser.parse_args()
    args.func(args)


def cmd_auth_google(args) -> None:
    settings = load_settings()
    GoogleCalendarWriterAgent(settings).authenticate()
    print("Google OAuth token created or refreshed.")


def cmd_sync(args) -> None:
    settings = load_settings()
    result = ObsidianCalendarOrchestrator(settings).sync_day(_parse_date(args.date), dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_telegram_today(args) -> None:
    settings = load_settings()
    result = asyncio.run(ObsidianCalendarOrchestrator(settings).send_today_digest(_parse_date(args.date)))
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_roadmap_weekly(args) -> None:
    settings = load_settings()
    planner = RoadmapPlannerAgent.from_json()
    weekly_targets = planner.weekly_targets(_parse_date(args.start_date), weeks=args.weeks)

    review_text = None
    if args.review:
        commands = args.review_command or commands_from_env()
        review_text = ExternalCliReviewAgent(commands).review(planner.render_markdown(weekly_targets))

    markdown = planner.render_markdown(weekly_targets, review_text=review_text)
    written_files: list[str] = []
    monthly_summary = None
    if args.write:
        writer = ObsidianRoadmapWriter(settings)
        written_files = [str(path) for path in writer.write_daily_friday_targets(weekly_targets, planner)]
        monthly_summary = str(writer.write_monthly_summary(weekly_targets, planner))

    if args.json:
        print(
            json.dumps(
                {
                    "weekly_targets": [target.to_dict() for target in weekly_targets],
                    "written_files": written_files,
                    "monthly_summary": monthly_summary,
                    "markdown": markdown,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(markdown)
        if written_files:
            print("\nWritten files:")
            for path in written_files:
                print(f"- {path}")
            if monthly_summary:
                print(f"- {monthly_summary}")


if __name__ == "__main__":
    main()
