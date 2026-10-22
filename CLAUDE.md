## FYP Academic Guidelines & Documentation Rules
- When drafting or structuring reports/chapters, STRICTLY comply with the guidelines and templates located in `docs/`:
  - Preliminary Proposal: Read `docs/context/proposal/guidelines.md` and `docs/context/proposal/template.md`
  - FYP 1: Read `docs/context/fyp1/guidelines.md` and `docs/context/fyp1/template.md`
  - FYP 2: Read `docs/context/fyp2/guidelines.md` and `docs/context/fyp2/template.md`
- Always verify chapter structure against the corresponding template before generating final text.
- Report drafts live in `reports/<phase>/` (`reports/proposal/`, later `reports/fyp1/`, `reports/fyp2/`); `docs/context/` holds only school reference material.
- Each phase follows its own guideline; `docs/context/fyp-index.md` is an index only. Submission dates: `docs/context/academic-calendar.md`.

## Project Baseline
- Current design baseline: `docs/fyp-design/fyp_project_design_v0.4.md` (v0.2/v0.3 are archived in `docs/fyp-design/archive/`). Plain-language RQ explanations: `docs/fyp-design/rq-explained.md`.
- Data source facts and evidence: `docs/data-source/data-source-summary.md`.

## Language Rules (school-facing material)
- Everything under `reports/` must be written in English only (British English). No Chinese characters anywhere in school-facing material.
- Code that will be submitted (all source files, comments, log/print messages, configs, workflow files, README) must be English only. Write all new code in English; existing Chinese comments/messages in `ingestion/`, `scripts/`, `.github/` must be translated before any code submission.
- Internal planning docs (`docs/fyp-design/`, `docs/data-source/`, `docs/context/my-context.md`, `docs/career/`, `docs/prompts/`) may stay in Chinese, but must be excluded from or translated in any submission package. Before submitting, scan for CJK characters (e.g. `grep -rnP '[\x{4e00}-\x{9fff}]'`).
