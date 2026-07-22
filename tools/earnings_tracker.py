from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).parent.parent / "vault" / "02-PROJECTS"


class EarningsTracker:
    """Track earnings across platforms with CSV persistence."""

    def __init__(self, tracker_dir: str | None = None):
        self._dir = Path(tracker_dir) if tracker_dir else DATA_DIR / "earnings"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._csv_path = self._dir / "earnings.csv"
        self._json_path = self._dir / "earnings.json"
        self._init_csv()

    def _init_csv(self):
        if not self._csv_path.exists():
            with open(self._csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "platform", "task_type", "amount", "currency", "hourly_rate", "notes"])

    def log(self, platform: str, task_type: str, amount: float, currency: str = "USD", hourly_rate: float = 0, notes: str = "") -> None:
        """Log an earnings entry."""
        row = [datetime.now().isoformat(), platform, task_type, f"{amount:.2f}", currency, f"{hourly_rate:.2f}", notes]
        with open(self._csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def get_all(self) -> list[dict]:
        """Read all entries."""
        entries = []
        if self._csv_path.exists():
            with open(self._csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                entries = list(reader)
        return entries

    def get_summary(self, period: str = "all") -> dict:
        """Get summary stats."""
        entries = self.get_all()
        total = sum(float(e.get("amount", 0)) for e in entries)
        by_platform = {}
        for e in entries:
            p = e.get("platform", "unknown")
            by_platform[p] = by_platform.get(p, 0) + float(e.get("amount", 0))
        return {
            "total_earned": round(total, 2),
            "entry_count": len(entries),
            "by_platform": by_platform,
            "period": period,
        }

    def daily_target_progress(self, daily_target: float = 35.71) -> dict:
        """Check progress toward daily target."""
        today = datetime.now().strftime("%Y-%m-%d")
        entries = [e for e in self.get_all() if e.get("date", "").startswith(today)]
        today_total = sum(float(e.get("amount", 0)) for e in entries)
        return {
            "date": today,
            "earned": round(today_total, 2),
            "target": daily_target,
            "progress_pct": round((today_total / daily_target) * 100, 1) if daily_target > 0 else 0,
            "remaining": round(max(0, daily_target - today_total), 2),
        }
