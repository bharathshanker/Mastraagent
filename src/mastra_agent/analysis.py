"""Signal extraction and brief generation logic."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, List

from .models import HiringSignal, LinkedInPost, LinkedInProfile, WeeklyBrief
from .linkedin import summarize_posts


class HiringSignalExtractor:
    """Extract high level hiring and capability signals from LinkedIn posts.

    This implementation uses simple keyword heuristics so that the project can
    run without external dependencies. The heuristics can be replaced with
    LLM-powered analysis once the Mastra runtime is available.
    """

    KEYWORDS = {
        "hiring": "Hiring alert",
        "recruit": "Recruitment activity",
        "open role": "Open role announcement",
        "expanding": "Expansion initiative",
        "digital": "Digital transformation update",
        "technology": "Technology focus",
    }

    def extract(self, posts: Iterable[LinkedInPost]) -> List[HiringSignal]:
        signals: List[HiringSignal] = []
        for post in posts:
            content_lower = post.content.lower()
            matched_labels: List[str] = []
            for keyword, label in self.KEYWORDS.items():
                if keyword in content_lower:
                    matched_labels.append(label)
            if matched_labels:
                summary = f"{'; '.join(matched_labels)} from {post.profile.name}'s post"
                signals.append(HiringSignal(summary=summary, source_post=post))
        return signals


def build_weekly_brief(
    company: str,
    profiles: Iterable[LinkedInProfile],
    posts: Iterable[LinkedInPost],
    lookback_days: int,
) -> WeeklyBrief:
    posts_list = list(posts)
    signals = HiringSignalExtractor().extract(posts_list)
    summary = summarize_posts(posts_list)
    return WeeklyBrief(
        company=company,
        profiles=list(profiles),
        posts=posts_list,
        hiring_signals=signals,
        summary=summary,
    )


def filter_posts_for_window(
    posts: Iterable[LinkedInPost], lookback_days: int, reference: datetime | None = None
) -> List[LinkedInPost]:
    """Filter posts within the lookback window."""

    posts_list = list(posts)
    reference = reference or datetime.utcnow()
    cutoff = reference - timedelta(days=lookback_days)
    return [post for post in posts_list if post.published_at >= cutoff]
