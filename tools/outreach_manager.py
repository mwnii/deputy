from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).parent.parent / "vault" / "02-PROJECTS"


class OutreachManager:
    """Track cold outreach campaigns and responses."""

    def __init__(self, data_dir: str | None = None):
        self._dir = Path(data_dir) if data_dir else DATA_DIR / "outreach"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._prospects_file = self._dir / "prospects.json"
        self._campaigns_file = self._dir / "campaigns.json"

    def _load(self, path: Path) -> list[dict]:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return []

    def _save(self, path: Path, data: list[dict]) -> None:
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def add_prospect(self, name: str, company: str, email: str, platform: str = "email", notes: str = "") -> None:
        """Add a prospect to the database."""
        prospects = self._load(self._prospects_file)
        prospects.append({
            "name": name,
            "company": company,
            "email": email,
            "platform": platform,
            "notes": notes,
            "status": "new",
            "added": datetime.now().isoformat(),
            "last_contact": None,
            "contact_count": 0,
        })
        self._save(self._prospects_file, prospects)

    def update_prospect(self, email: str, status: str, notes: str = "") -> None:
        """Update prospect status."""
        prospects = self._load(self._prospects_file)
        for p in prospects:
            if p.get("email") == email:
                p["status"] = status
                p["last_contact"] = datetime.now().isoformat()
                p["contact_count"] = p.get("contact_count", 0) + 1
                if notes:
                    p["notes"] = notes
                break
        self._save(self._prospects_file, prospects)

    def get_stats(self) -> dict:
        """Get outreach statistics."""
        prospects = self._load(self._prospects_file)
        status_counts = {}
        for p in prospects:
            s = p.get("status", "new")
            status_counts[s] = status_counts.get(s, 0) + 1
        return {
            "total": len(prospects),
            "by_status": status_counts,
            "response_rate": round(
                (status_counts.get("replied", 0) + status_counts.get("interested", 0))
                / max(len(prospects), 1) * 100, 1
            ),
        }

    def get_followups_needed(self) -> list[dict]:
        """Get prospects needing follow-up (contacted 3+ days ago with no reply)."""
        from datetime import timedelta
        prospects = self._load(self._prospects_file)
        cutoff = (datetime.now() - timedelta(days=3)).isoformat()
        return [
            p for p in prospects
            if p.get("status") in ("contacted", "follow_up")
            and (p.get("last_contact") or "") < cutoff
        ]
