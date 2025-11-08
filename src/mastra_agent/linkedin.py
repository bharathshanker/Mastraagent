"""LinkedIn data acquisition and enrichment utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Iterable, Iterator

from .models import LinkedInPost, LinkedInProfile


@dataclass(slots=True)
class LocalSnapshotSource:
    """Load LinkedIn posts from local JSON snapshots.

    The JSON file should contain a mapping from profile URLs to a list of post
    dictionaries. Each post dictionary must include a ``content`` field and a
    ``published_at`` ISO timestamp. Optional keys such as ``url``,
    ``reactions``, and ``comments`` are also supported.
    """

    snapshot_path: Path

    def load_posts(self, profile: LinkedInProfile) -> Iterable[LinkedInPost]:
        data = self._load_snapshot()
        profile_posts = data.get(profile.url, [])
        for entry in profile_posts:
            yield self._convert_entry(profile, entry)

    def iter_recent_posts(
        self, profile: LinkedInProfile, lookback_days: int
    ) -> Iterator[LinkedInPost]:
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        for post in self.load_posts(profile):
            if post.published_at >= cutoff:
                yield post

    def _load_snapshot(self) -> dict:
        if not self.snapshot_path.exists():
            raise FileNotFoundError(
                "Snapshot file not found. Please generate sample data using the"
                " provided template in data/sample_posts.json"
            )
        with self.snapshot_path.open("r", encoding="utf-8") as fp:
            return json.load(fp)

    @staticmethod
    def _convert_entry(profile: LinkedInProfile, entry: dict) -> LinkedInPost:
        published_raw = entry["published_at"]
        published_at = datetime.fromisoformat(published_raw)
        return LinkedInPost(
            profile=profile,
            content=entry["content"],
            published_at=published_at,
            url=entry.get("url"),
            reactions=entry.get("reactions"),
            comments=entry.get("comments"),
            extra_metadata=entry.get("metadata", {}),
        )


def summarize_posts(posts: Iterable[LinkedInPost]) -> str:
    """Create a natural language summary from a collection of posts."""

    posts_list = list(posts)
    if not posts_list:
        return "No public signals identified during the selected period."

    lines: list[str] = []
    for post in posts_list:
        profile = post.profile
        timestamp = post.published_at.strftime("%d %b %Y")
        headline = post.content.strip().split("\n", 1)[0][:120]
        lines.append(
            f"{profile.company or 'Unknown company'} · {profile.name} ({timestamp}): {headline}"
        )
    return "\n".join(lines)
