from __future__ import annotations

from pathlib import Path
from typing import Any


class ContentPublisher:
    """Publish content to markdown files for manual posting."""

    def __init__(self, output_dir: str | None = None):
        self._dir = Path(output_dir) if output_dir else Path(__file__).parent.parent / "vault" / "05-CONTENT"
        self._dir.mkdir(parents=True, exist_ok=True)

    def save_linkedin_post(self, title: str, content: str, hashtags: list[str] | None = None) -> str:
        """Save a LinkedIn post as markdown."""
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = "".join(c for c in title if c.isalnum() or c in " -").strip().replace(" ", "_")
        filename = f"linkedin_{date_str}_{safe_title}.md"

        tags = " ".join(f"#{t}" for t in (hashtags or []))
        md = f"# {title}\n\n{content}\n\n---\n{tags}\n"
        path = self._dir / filename
        path.write_text(md, encoding="utf-8")
        return str(path)

    def save_blog_post(self, title: str, content: str, tags: list[str] | None = None) -> str:
        """Save a blog post as markdown."""
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = "".join(c for c in title if c.isalnum() or c in " -").strip().replace(" ", "_")
        filename = f"blog_{date_str}_{safe_title}.md"

        tag_line = ", ".join(tags or [])
        md = f"---\ntitle: \"{title}\"\ndate: {date_str}\ntags: [{tag_line}]\n---\n\n# {title}\n\n{content}\n"
        path = self._dir / filename
        path.write_text(md, encoding="utf-8")
        return str(path)

    def save_email_template(self, name: str, subject: str, body: str) -> str:
        """Save an email template."""
        safe_name = "".join(c for c in name if c.isalnum() or c in " -").strip().replace(" ", "_")
        md = f"# Email Template: {name}\n\n**Subject:** {subject}\n\n---\n\n{body}\n"
        path = self._dir / f"email_{safe_name}.md"
        path.write_text(md, encoding="utf-8")
        return str(path)

    def list_content(self) -> list[str]:
        """List all content files."""
        return [str(f) for f in self._dir.glob("*.md")]
