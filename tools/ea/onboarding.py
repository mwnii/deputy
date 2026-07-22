#!/usr/bin/env python3
"""
EA Onboarding Orchestrator

Checks system state, detects already-configured services,
and tracks onboarding progress. Designed to be called by the
EA agent during onboarding flow.

Usage:
    python -m tools.ea.onboarding status    # Show what's configured
    python -m tools.ea.onboarding check     # Check onboarding completion
    python -m tools.ea.onboarding mark <step>  # Mark a step complete
    python -m tools.ea.onboarding log <message> # Append to onboarding log
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent.parent
ENV_FILE = ROOT / "config" / ".env"
STATUS_FILE = ROOT / "vault" / "02-EA" / "onboarding-status.json"
LOG_FILE = ROOT / "vault" / "02-EA" / "onboarding-log.md"
PREFS_FILE = ROOT / "vault" / "05-DATA" / "user-preferences.json"

ONBOARDING_STEPS = [
    "user_identity",
    "groq_api",
    "google_workspace",
    "ntfy_notifications",
    "platform_accounts",
    "email_preferences",
    "calendar_preferences",
    "notification_preferences",
    "system_verification",
    "finalize",
]

STEP_DESCRIPTIONS = {
    "user_identity": "User identity (name, timezone, working hours)",
    "groq_api": "Groq API key for LLM inference",
    "google_workspace": "Google Workspace OAuth for Gmail/Calendar/Tasks",
    "ntfy_notifications": "ntfy.sh phone push notifications",
    "platform_accounts": "Platform accounts (Fiverr, Upwork, Outlier, etc.)",
    "email_preferences": "Email signature and draft preferences",
    "calendar_preferences": "Calendar defaults and event settings",
    "notification_preferences": "Notification priority and quiet hours",
    "system_verification": "Verify all services work correctly",
    "finalize": "Finalize onboarding and send confirmation",
}

ENV_CHECKS = {
    "groq_api": ["GROQ_API_KEY"],
    "google_workspace": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"],
    "ntfy_notifications": ["NTFY_TOPIC"],
    "platform_accounts": ["FIVERR_USERNAME", "UPWORK_USERNAME", "OUTLIER_EMAIL"],
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_env() -> dict[str, str]:
    """Read .env file and return key-value pairs (excluding comments and empty values)."""
    env: dict[str, str] = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if value and not value.startswith("your_") and value != "":
                env[key] = value
    return env


def _read_status() -> dict[str, Any]:
    """Read onboarding status file."""
    if not STATUS_FILE.exists():
        return {
            "onboarding_complete": False,
            "completed_at": None,
            "version": "1.0",
            "steps": {},
        }
    return json.loads(STATUS_FILE.read_text(encoding="utf-8"))


def _write_status(status: dict[str, Any]) -> None:
    """Write onboarding status file."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(
        json.dumps(status, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _read_prefs() -> dict[str, Any]:
    """Read user preferences."""
    if not PREFS_FILE.exists():
        return {}
    return json.loads(PREFS_FILE.read_text(encoding="utf-8"))


def _write_prefs(prefs: dict[str, Any]) -> None:
    """Write user preferences."""
    PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PREFS_FILE.write_text(
        json.dumps(prefs, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _append_log(message: str) -> None:
    """Append a message to the onboarding log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    if not LOG_FILE.exists():
        LOG_FILE.write_text(
            "# Onboarding Log\n\n"
            f"**Started:** {timestamp}\n\n"
            "---\n\n",
            encoding="utf-8",
        )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"## [{timestamp}]\n\n{message}\n\n---\n\n")


def get_env_status() -> dict[str, dict[str, Any]]:
    """Check which environment variables are configured."""
    env = _read_env()
    result = {}
    for step, keys in ENV_CHECKS.items():
        configured = []
        missing = []
        for key in keys:
            if key in env:
                configured.append(key)
            else:
                missing.append(key)
        result[step] = {
            "configured_keys": configured,
            "missing_keys": missing,
            "fully_configured": len(missing) == 0,
        }
    return result


def get_onboarding_status() -> dict[str, Any]:
    """Get full onboarding status."""
    status = _read_status()
    env_status = get_env_status()

    steps_report = {}
    for step in ONBOARDING_STEPS:
        step_done = status.get("steps", {}).get(step, {}).get("complete", False)
        env_info = env_status.get(step)
        steps_report[step] = {
            "description": STEP_DESCRIPTIONS[step],
            "onboarding_marked_complete": step_done,
            "env_configured": env_info["fully_configured"] if env_info else None,
            "missing_env_keys": env_info["missing_keys"] if env_info else [],
        }

    return {
        "onboarding_complete": status.get("onboarding_complete", False),
        "completed_at": status.get("completed_at"),
        "steps": steps_report,
    }


def mark_step(step: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    """Mark an onboarding step as complete."""
    if step not in ONBOARDING_STEPS:
        return {"error": f"Unknown step: {step}. Valid steps: {ONBOARDING_STEPS}"}

    status = _read_status()
    if "steps" not in status:
        status["steps"] = {}

    status["steps"][step] = {
        "complete": True,
        "timestamp": _now_iso(),
        "details": details or {},
    }

    # Check if all steps are complete
    all_done = all(
        status["steps"].get(s, {}).get("complete", False)
        for s in ONBOARDING_STEPS
    )
    if all_done:
        status["onboarding_complete"] = True
        status["completed_at"] = _now_iso()

    _write_status(status)
    _append_log(f"**Step completed:** {STEP_DESCRIPTIONS.get(step, step)}")

    return {
        "step": step,
        "marked_complete": True,
        "onboarding_complete": all_done,
    }


def save_user_identity(
    name: str,
    timezone_str: str,
    working_hours: str,
    communication_style: str = "semi-formal",
) -> dict[str, Any]:
    """Save user identity information."""
    prefs = _read_prefs()
    prefs["user"] = {
        "name": name,
        "timezone": timezone_str,
        "working_hours": working_hours,
        "communication_style": communication_style,
        "configured_at": _now_iso(),
    }
    _write_prefs(prefs)
    _append_log(
        f"**User identity saved:**\n"
        f"- Name: {name}\n"
        f"- Timezone: {timezone_str}\n"
        f"- Working hours: {working_hours}\n"
        f"- Communication style: {communication_style}"
    )
    return {"saved": True}


def save_email_preferences(
    signature: str,
    tone: str = "semi-formal",
    templates: list[str] | None = None,
) -> dict[str, Any]:
    """Save email preferences."""
    prefs = _read_prefs()
    prefs["email"] = {
        "signature": signature,
        "tone": tone,
        "templates": templates or [],
        "configured_at": _now_iso(),
    }
    _write_prefs(prefs)
    _append_log(
        f"**Email preferences saved:**\n"
        f"- Signature: {signature}\n"
        f"- Tone: {tone}\n"
        f"- Templates: {len(templates or [])} templates"
    )
    return {"saved": True}


def save_calendar_preferences(
    calendar_name: str = "primary",
    default_duration_min: int = 30,
    default_reminder_min: int = 30,
    auto_decline_conflicts: bool = False,
) -> dict[str, Any]:
    """Save calendar preferences."""
    prefs = _read_prefs()
    prefs["calendar"] = {
        "calendar_name": calendar_name,
        "default_duration_minutes": default_duration_min,
        "default_reminder_minutes": default_reminder_min,
        "auto_decline_conflicts": auto_decline_conflicts,
        "configured_at": _now_iso(),
    }
    _write_prefs(prefs)
    _append_log(
        f"**Calendar preferences saved:**\n"
        f"- Calendar: {calendar_name}\n"
        f"- Default duration: {default_duration_min}min\n"
        f"- Default reminder: {default_reminder_min}min before\n"
        f"- Auto-decline conflicts: {auto_decline_conflicts}"
    )
    return {"saved": True}


def save_notification_preferences(
    urgent_senders: list[str] | None = None,
    briefing_time: str = "08:00",
    calendar_reminders: bool = True,
    quiet_hours_start: str = "22:00",
    quiet_hours_end: str = "07:00",
) -> dict[str, Any]:
    """Save notification preferences."""
    prefs = _read_prefs()
    prefs["notifications"] = {
        "urgent_senders": urgent_senders or [],
        "briefing_time": briefing_time,
        "calendar_reminders": calendar_reminders,
        "quiet_hours_start": quiet_hours_start,
        "quiet_hours_end": quiet_hours_end,
        "configured_at": _now_iso(),
    }
    _write_prefs(prefs)
    _append_log(
        f"**Notification preferences saved:**\n"
        f"- Urgent senders: {urgent_senders or 'none specified'}\n"
        f"- Daily briefing: {briefing_time}\n"
        f"- Calendar reminders: {calendar_reminders}\n"
        f"- Quiet hours: {quiet_hours_start} - {quiet_hours_end}"
    )
    return {"saved": True}


def save_platform_accounts(
    fiverr_username: str = "",
    upwork_username: str = "",
    outlier_email: str = "",
    dataannotation_email: str = "",
) -> dict[str, Any]:
    """Save platform account info to .env (non-sensitive usernames/emails only)."""
    updates = []
    if fiverr_username:
        updates.append(f"FIVERR_USERNAME={fiverr_username}")
    if upwork_username:
        updates.append(f"UPWORK_USERNAME={upwork_username}")
    if outlier_email:
        updates.append(f"OUTLIER_EMAIL={outlier_email}")
    if dataannotation_email:
        updates.append(f"DATAANNOTATION_EMAIL={dataannotation_email}")

    if updates:
        # Append to .env
        ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ENV_FILE, "a", encoding="utf-8") as f:
            f.write("\n# --- Platform Accounts ---\n")
            for update in updates:
                f.write(f"{update}\n")

    _append_log(
        f"**Platform accounts saved:**\n"
        f"- Fiverr: {fiverr_username or 'not configured'}\n"
        f"- Upwork: {upwork_username or 'not configured'}\n"
        f"- Outlier: {outlier_email or 'not configured'}\n"
        f"- DataAnnotation: {dataannotation_email or 'not configured'}"
    )
    return {"saved": True, "updates": updates}


def finalize_onboarding() -> dict[str, Any]:
    """Finalize onboarding — mark complete and log summary."""
    status = _read_status()
    all_done = all(
        status.get("steps", {}).get(s, {}).get("complete", False)
        for s in ONBOARDING_STEPS
    )

    if not all_done:
        incomplete = [
            s for s in ONBOARDING_STEPS
            if not status.get("steps", {}).get(s, {}).get("complete", False)
        ]
        return {
            "error": "Not all steps complete",
            "incomplete_steps": incomplete,
        }

    status["onboarding_complete"] = True
    status["completed_at"] = _now_iso()
    _write_status(status)

    _append_log(
        "## Onboarding Complete\n\n"
        "All 10 phases completed successfully.\n"
        "System is ready for normal operations."
    )

    return {
        "onboarding_complete": True,
        "completed_at": status["completed_at"],
    }


def print_status() -> None:
    """Print a human-readable status report."""
    report = get_onboarding_status()
    status = "COMPLETE" if report["onboarding_complete"] else "IN PROGRESS"
    print(f"\n=== Onboarding Status: {status} ===")
    if report["completed_at"]:
        print(f"Completed at: {report['completed_at']}")
    print()

    for step, info in report["steps"].items():
        icon = "  [DONE]" if info["onboarding_marked_complete"] else "  [TODO]"
        print(f"{icon} {info['description']}")
        if info["missing_env_keys"]:
            print(f"         Missing env: {', '.join(info['missing_env_keys'])}")
    print()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m tools.ea.onboarding <command>")
        print("Commands: status, check, mark <step>, log <message>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        print_status()
    elif cmd == "check":
        report = get_onboarding_status()
        print(json.dumps(report, indent=2))
    elif cmd == "mark":
        if len(sys.argv) < 3:
            print("Usage: mark <step_name>")
            sys.exit(1)
        result = mark_step(sys.argv[2])
        print(json.dumps(result, indent=2))
    elif cmd == "log":
        message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Log entry"
        _append_log(message)
        print(f"Logged: {message}")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
