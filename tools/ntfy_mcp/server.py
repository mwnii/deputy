#!/usr/bin/env python3
"""
ntfy.sh MCP Server — Push notifications to phone via ntfy.sh

Setup:
1. Install ntfy.sh app on your phone
2. Subscribe to a unique topic (e.g., "my-agent-notifications-abc123")
3. Set NTFY_TOPIC environment variable to that topic
4. Set NTFY_SERVER to https://ntfy.sh (default) or your self-hosted instance
"""

import os
import sys
import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ntfy-notifications")

NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")


def _validate_config():
    if not NTFY_TOPIC:
        raise ValueError(
            "NTFY_TOPIC environment variable is not set. "
            "Create a unique topic at https://ntfy.sh and set it."
        )


@mcp.tool()
def send_notification(
    message: str,
    title: str = "Agent Notification",
    priority: int = 3,
    tags: str = "",
    click_url: str = "",
) -> str:
    """
    Send a push notification to the user's phone via ntfy.sh.

    Args:
        message: Notification body text (required)
        title: Notification title (default: "Agent Notification")
        priority: Priority level 1-5 (1=min, 3=default, 5=urgent)
        tags: Comma-separated tags for emoji icons (e.g., "robot,white_check_mark,warning")
        click_url: URL to open when notification is tapped

    Returns:
        Confirmation message with delivery status
    """
    _validate_config()

    headers = {
        "Title": title,
        "Priority": str(priority),
    }
    if tags:
        headers["Tags"] = tags
    if click_url:
        headers["Click"] = click_url

    url = f"{NTFY_SERVER}/{NTFY_TOPIC}"

    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(url, content=message.encode("utf-8"), headers=headers)
            response.raise_for_status()
            return json.dumps({
                "status": "delivered",
                "topic": NTFY_TOPIC,
                "server": NTFY_SERVER,
                "title": title,
                "priority": priority,
                "message_length": len(message),
            })
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "failed",
            "error": f"HTTP {e.response.status_code}: {e.response.text}",
        })
    except Exception as e:
        return json.dumps({
            "status": "failed",
            "error": str(e),
        })


@mcp.tool()
def send_email_alert(
    sender: str,
    subject: str,
    summary: str,
    urgency: str = "normal",
) -> str:
    """
    Send a notification about an important email that needs attention.

    Args:
        sender: Who sent the email
        subject: Email subject line
        summary: Brief summary of what the email needs
        urgency: "low", "normal", "high", or "urgent"

    Returns:
        Delivery confirmation
    """
    priority_map = {"low": 1, "normal": 3, "high": 4, "urgent": 5}
    tag_map = {"low": "incoming_envelope", "normal": "incoming_envelope", "high": "warning", "urgent": "rotating_light"}

    priority = priority_map.get(urgency, 3)
    tags = tag_map.get(urgency, "incoming_envelope")

    message = f"From: {sender}\nSubject: {subject}\n\n{summary}"
    title = f"📧 Email from {sender}" if urgency != "urgent" else f"🚨 URGENT from {sender}"

    return send_notification(message=message, title=title, priority=priority, tags=tags)


@mcp.tool()
def send_calendar_alert(
    event_name: str,
    event_time: str,
    location: str = "",
    minutes_until: int = 30,
) -> str:
    """
    Send a notification about an upcoming calendar event.

    Args:
        event_name: Name of the event
        event_time: When the event starts (e.g., "2:00 PM")
        location: Where the event is (optional)
        minutes_until: Minutes until the event starts

    Returns:
        Delivery confirmation
    """
    location_text = f"\nLocation: {location}" if location else ""
    message = f"Event: {event_name}\nTime: {event_time}{location_text}\n\nStarting in {minutes_until} minutes."
    title = f"📅 {event_name} in {minutes_until}min"
    priority = 4 if minutes_until <= 15 else 3
    tags = "calendar"

    return send_notification(message=message, title=title, priority=priority, tags=tags)


@mcp.tool()
def send_task_alert(
    task_name: str,
    due_info: str,
    status: str = "due_soon",
) -> str:
    """
    Send a notification about a task that needs attention.

    Args:
        task_name: Name/description of the task
        due_info: When it's due or how overdue it is
        status: "due_soon", "overdue", "completed", or "needs_review"

    Returns:
        Delivery confirmation
    """
    status_config = {
        "due_soon": ("📋 Task Due Soon", 3, "alarm_clock"),
        "overdue": ("🚨 Task Overdue", 5, "rotating_light"),
        "completed": ("✅ Task Completed", 2, "white_check_mark"),
        "needs_review": ("👀 Task Needs Review", 3, "eyes"),
    }

    title, priority, tags = status_config.get(status, ("📋 Task Update", 3, "memo"))
    message = f"Task: {task_name}\nStatus: {due_info}"

    return send_notification(message=message, title=title, priority=priority, tags=tags)


@mcp.tool()
def check_config() -> str:
    """
    Check if ntfy.sh is configured correctly.

    Returns:
        Configuration status and setup instructions if not configured
    """
    if not NTFY_TOPIC:
        return json.dumps({
            "configured": False,
            "instructions": [
                "1. Install ntfy.sh on your phone (App Store / Play Store)",
                "2. Open the app and tap 'Add subscription'",
                "3. Enter a unique topic name (e.g., 'my-income-agent-xyz')",
                "4. Set NTFY_TOPIC to that topic name in config/.env",
                "5. Optionally set NTFY_SERVER if self-hosting",
            ],
        })

    return json.dumps({
        "configured": True,
        "topic": NTFY_TOPIC,
        "server": NTFY_SERVER,
        "test_command": f'curl -d "Test notification" {NTFY_SERVER}/{NTFY_TOPIC}',
    })


if __name__ == "__main__":
    mcp.run(transport="stdio")
