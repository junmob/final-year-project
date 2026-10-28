# Klang Valley Bus Service Reliability Data Platform

A Final Year Project (UTAR FICT) that turns Malaysia's open GTFS Realtime bus feeds (data.gov.my) into trustworthy, traceable service-reliability metrics: on-time performance, headway regularity, excess wait time and bus bunching.

**Planned stack** (zero cost, open source): Python, Apache Kafka, MinIO (S3 API), Apache Iceberg + Polaris, Apache Spark, ClickHouse, dbt, Apache Airflow, PostgreSQL, Metabase, Prometheus/Grafana, Docker Compose.

## Status (2026-10)

| Component | Status |
|---|---|
| Collector VM (AWS EC2): GTFS Realtime every 30 s per feed, daily `tar.zst` packs with manifests | Live since 2026-10-22 |
| Collector VM: GTFS Static (daily), weather forecast (3-hourly) and warnings (hourly), Rapid Rail OD ridership (every version) | Live since 2026-10-23 |
| Off-site backup of GTFS Static (and, temporarily, weather) | Live — GitHub Actions |
| `bronze_sync` (VM to local copy with manifest verification) | In progress |
| Lakehouse pipeline, dashboards, experiments | Not started (see roadmap in the design doc) |

## Repository layout

| Path | Contents |
|---|---|
| `ingestion/` | Collectors, packing and sync jobs, and their systemd deployment files |
| `.github/workflows/` | Off-site backup jobs |
| `data/github-backup/` | Data committed by the GitHub Actions backup jobs |
| `docs/fyp-design/` | Design document (current: v0.5) |
| `docs/engineering-log/` | How each module evolved: what a version could not do, how it showed up, what the next version changed |
| `docs/adr/` | Architecture Decision Records |
| `docs/tickets/`, `docs/learning/` | Work tickets and learning guides (internal, in Chinese) |
| `docs/data-source/` | Data source profiling, evidence catalogue, official API docs |
| `docs/evidence/` | Probe outputs cited as evidence |
| `docs/context/` | University guidelines, templates and academic calendar |
| `reports/` | Report drafts (Proposal, FYP 1, FYP 2) |
| `docs/career/`, `docs/prompts/` | Personal notes and AI task prompts |
