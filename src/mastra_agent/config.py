"""Configuration utilities for the Mastra LinkedIn tracking project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import tomllib

from .models import LinkedInProfile


@dataclass(slots=True)
class CompanyConfig:
    """Configuration entry describing a monitored company."""

    name: str
    profiles: List[LinkedInProfile]


@dataclass(slots=True)
class ProjectConfig:
    """Top-level configuration for the project."""

    companies: List[CompanyConfig]
    lookback_days: int = 7

    def iter_profiles(self) -> Iterable[LinkedInProfile]:
        for company in self.companies:
            yield from company.profiles


def load_config(path: str | Path) -> ProjectConfig:
    """Load configuration from a TOML file."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("rb") as fp:
        raw = tomllib.load(fp)

    lookback_days = int(raw.get("lookback_days", 7))
    companies_data = raw.get("company", [])
    if not isinstance(companies_data, list):
        raise ValueError("Expected 'company' to be a list in the configuration file")

    companies: List[CompanyConfig] = []
    for entry in companies_data:
        name = entry.get("name")
        if not name:
            raise ValueError("Each company entry must include a 'name'")
        profiles_data = entry.get("profile", [])
        profiles: List[LinkedInProfile] = []
        for profile_entry in profiles_data:
            profiles.append(
                LinkedInProfile(
                    name=profile_entry["name"],
                    url=profile_entry["url"],
                    title=profile_entry.get("title"),
                    company=name,
                )
            )
        companies.append(CompanyConfig(name=name, profiles=profiles))

    return ProjectConfig(companies=companies, lookback_days=lookback_days)
