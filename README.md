# Mastra LinkedIn Intelligence Starter

This repository provides a starter Mastra project designed for building an agent
that monitors LinkedIn activity from chief digital officers and digital
transformation leaders at gold loan companies in India. It ships with a minimal
standard-library-only toolkit so that you can run exploratory workflows without a
Mastra runtime, while leaving clear extension points for when you plug into the
Mastra platform and its command suite.

## Project layout

```
.
├── config/
│   └── profiles.toml          # Company and profile configuration
├── data/
│   └── sample_posts.json      # Offline sample data for experimentation
├── src/
│   └── mastra_agent/
│       ├── __init__.py        # Package entry point
│       ├── analysis.py        # Heuristic signal extraction & briefing helpers
│       ├── cli.py             # Command-line interface and orchestration
│       ├── config.py          # TOML configuration loader
│       ├── linkedin.py        # Snapshot data source & summarisation helpers
│       └── models.py          # Core dataclasses for posts, profiles and briefs
└── README.md
```

You can run the CLI locally via:

```bash
PYTHONPATH=src python -m mastra_agent.cli list-profiles
PYTHONPATH=src python -m mastra_agent.cli generate-weekly-brief --output weekly_brief.txt
```

This will use the sample data included in `data/sample_posts.json` to create a
weekly brief. Replace the configuration and snapshot data with real sources when
moving to production.

## Working with the Mastra CLI

Once you install the [Mastra](https://docs.mastra.com/) toolchain in your
environment you can hook the project into the official command suite. The most
common commands you will use are:

```bash
# Scaffold a new Mastra workspace (already reflected in this repo)
mastra init

# Run an individual agent defined in your flows directory
mastra agent run linkedin-weekly-brief

# Execute an orchestrated flow or workflow
mastra flow run weekly-brief

# Inspect logs and execution traces
mastra logs tail
```

The Python package in `src/mastra_agent` is designed so that you can plug these
components into Mastra flows. For example, you can wrap `build_weekly_brief`
inside a Mastra task or tool, and expose `LocalSnapshotSource` as a data loader
node. Update the README with concrete command references as you wire the package
into your Mastra runtime.

## Extending the project

1. **Replace the snapshot loader** – Swap out `LocalSnapshotSource` with a real
   LinkedIn ingestion layer. This could be a first-party connector, a vendor API
   or a headless browser workflow orchestrated via Mastra.
2. **Upgrade signal extraction** – The default keyword heuristics live in
   `HiringSignalExtractor`. Replace them with an LLM chain or a Mastra tool once
   you have access to your preferred foundation models.
3. **Persist historical data** – Add a persistence layer (e.g. PostgreSQL or
   Airtable) and track week-over-week changes for each company.
4. **Automate reporting** – Wrap the CLI in a scheduled Mastra flow that runs
   weekly, stores artefacts and sends out summaries through Slack or email.

## Example workflow

1. Update `config/profiles.toml` with the real LinkedIn profile URLs for the
   companies you want to monitor.
2. Implement a data ingestion task (within Mastra) that pulls the latest posts
   and writes them to `data/latest_posts.json`.
3. Run the CLI or orchestrate a Mastra flow to generate the brief:

   ```bash
   PYTHONPATH=src python -m mastra_agent.cli generate-weekly-brief --snapshot data/latest_posts.json \
     --output reports/muthoot_finance_weekly.txt --company "Muthoot Finance"
   ```

4. Feed the generated report into downstream analytics, dashboards or summary
   agents.

With this structure you have an opinionated foundation for building a LinkedIn
intelligence agent on the Mastra platform while retaining the flexibility to
swap in production-grade components as you iterate.
