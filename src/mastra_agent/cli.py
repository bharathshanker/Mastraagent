"""Command line interface for the Mastra LinkedIn tracking project."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from .analysis import build_weekly_brief, filter_posts_for_window
from .config import ProjectConfig, load_config
from .linkedin import LocalSnapshotSource
from .models import LinkedInPost, WeeklyBrief


DEFAULT_CONFIG_PATH = Path("config/profiles.toml")
DEFAULT_SNAPSHOT_PATH = Path("data/sample_posts.json")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["list-profiles", "generate-weekly-brief"],
        help="Action to perform",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the configuration TOML file",
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=DEFAULT_SNAPSHOT_PATH,
        help="Path to the JSON snapshot with sample posts",
    )
    parser.add_argument(
        "--company",
        help="Optional company name for generating a specific brief",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the generated brief to a text file",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        help="Override the lookback window defined in the configuration",
    )
    return parser.parse_args(argv)


def _print_profiles(config: ProjectConfig) -> None:
    for company in config.companies:
        print(f"Company: {company.name}")
        for profile in company.profiles:
            title_suffix = f" ({profile.title})" if profile.title else ""
            print(f"  - {profile.name}{title_suffix}: {profile.url}")


def _generate_brief(
    config: ProjectConfig, snapshot_path: Path, company_filter: str | None, lookback: int
) -> Iterable[WeeklyBrief]:
    source = LocalSnapshotSource(snapshot_path=snapshot_path)

    for company in config.companies:
        if company_filter and company.name.lower() != company_filter.lower():
            continue

        company_posts: list[LinkedInPost] = []
        for profile in company.profiles:
            posts = source.iter_recent_posts(profile, lookback)
            filtered = filter_posts_for_window(posts, lookback)
            company_posts.extend(filtered)

        brief = build_weekly_brief(
            company=company.name,
            profiles=company.profiles,
            posts=company_posts,
            lookback_days=lookback,
        )
        yield brief


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config)
    lookback = args.lookback_days or config.lookback_days

    if args.command == "list-profiles":
        _print_profiles(config)
        return 0

    briefs = list(
        _generate_brief(
            config=config,
            snapshot_path=args.snapshot,
            company_filter=args.company,
            lookback=lookback,
        )
    )
    if not briefs:
        print("No companies matched the provided filters.")
        return 1

    for brief in briefs:
        if args.output:
            args.output.write_text("\n".join(brief.report_lines), encoding="utf-8")
            print(f"Brief written to {args.output}")
        else:
            print("\n".join(brief.report_lines))
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
