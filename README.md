# Klang Valley Bus Service Reliability Data Platform

A Final Year Project (UTAR FICT) that turns Malaysia's open GTFS Realtime bus feeds (data.gov.my) into trustworthy, traceable service-reliability metrics: on-time performance, headway regularity, excess wait time and bus bunching.

**Planned stack** (zero cost, open source): Python, Apache Kafka, MinIO (S3 API), Apache Iceberg + Polaris, Apache Spark, ClickHouse, dbt, Apache Airflow, PostgreSQL, Metabase, Prometheus/Grafana, Docker Compose.

## Status (2026-10)

| Component | Status |
|---|---|
| GTFS Static archive (daily check, per-file content-addressed deduplication) | Live — GitHub Actions |
| Weather forecast/warning archive (every 3 hours, temporary) | Live — GitHub Actions |
| GTFS Realtime 24/7 collector | Prototype tested locally; cloud VM deployment pending |
| Lakehouse pipeline, dashboards, experiments | Not started (see roadmap in the design doc) |

## Repository layout

| Path | Contents |
|---|---|
| `ingestion/` | Long-running collectors and deployment files |
| `scripts/` | Archive jobs and one-off probes |
| `.github/workflows/` | Scheduled archive jobs |
| `data/raw/` | Raw landing data (realtime `.pb` files are not committed) |
| `docs/fyp-design/` | Design document (current: v0.4) |
| `docs/data-source/` | Data source profiling, evidence catalogue, official API docs |
| `docs/evidence/` | Probe outputs cited as evidence |
| `docs/context/` | University guidelines, templates and academic calendar |
| `reports/` | Report drafts (Proposal, FYP 1, FYP 2) |
| `docs/career/`, `docs/prompts/` | Personal notes and AI task prompts |
