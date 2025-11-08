"""Domain models used by the LinkedIn tracking agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List


@dataclass(slots=True)
class LinkedInProfile:
    """Represents a LinkedIn profile to monitor."""

    name: str
    url: str
    title: str | None = None
    company: str | None = None

    def __post_init__(self) -> None:
        if not self.url.startswith("http"):
            raise ValueError(f"LinkedIn URL must be absolute: {self.url!r}")


@dataclass(slots=True)
class LinkedInPost:
    """A single LinkedIn post."""

    profile: LinkedInProfile
    content: str
    published_at: datetime
    url: str | None = None
    reactions: int | None = None
    comments: int | None = None
    extra_metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class HiringSignal:
    """Represents hiring or capability signal extracted from a post."""

    summary: str
    source_post: LinkedInPost


@dataclass(slots=True)
class WeeklyBrief:
    """Aggregate weekly brief for a company."""

    company: str
    profiles: List[LinkedInProfile]
    posts: List[LinkedInPost]
    hiring_signals: List[HiringSignal]
    summary: str

    @property
    def report_lines(self) -> Iterable[str]:
        """Yield lines for a textual report."""

        yield f"Weekly brief for {self.company}"
        yield "=" * (len(self.company) + 14)
        yield ""

        if not self.posts:
            yield "No posts captured for the selected period."
            return

        yield "Key profiles monitored:"
        for profile in self.profiles:
            descriptor = f"- {profile.name}"
            if profile.title:
                descriptor += f", {profile.title}"
            yield descriptor
        yield ""

        yield "Highlighted posts:"
        for post in self.posts:
            timestamp = post.published_at.strftime("%Y-%m-%d")
            yield f"- {timestamp}: {post.profile.name}"
            snippet = post.content.strip().replace("\n", " ")
            yield f"  {snippet[:180]}{'…' if len(snippet) > 180 else ''}"
            if post.url:
                yield f"  Link: {post.url}"
            if post.reactions is not None or post.comments is not None:
                metrics = []
                if post.reactions is not None:
                    metrics.append(f"{post.reactions} reactions")
                if post.comments is not None:
                    metrics.append(f"{post.comments} comments")
                yield "  Metrics: " + ", ".join(metrics)
            if post.extra_metadata:
                metadata_str = ", ".join(
                    f"{key}={value}" for key, value in post.extra_metadata.items()
                )
                yield f"  Metadata: {metadata_str}"
            yield ""

        if self.hiring_signals:
            yield "Hiring and capability signals:"
            for signal in self.hiring_signals:
                yield f"- {signal.summary}"
            yield ""

        yield "Summary:"
        yield self.summary
