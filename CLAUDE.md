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
- Collector VM learning guide (how the VM, deployment and each collector work): `docs/learning/vm-collector-guide.md`.
- Data source facts and evidence: `docs/data-source/data-source-summary.md`.

## Language Rules (school-facing material)
- Everything under `reports/` must be written in English only (British English). No Chinese characters anywhere in school-facing material.
- Code that will be submitted (all source files, comments, log/print messages, configs, workflow files, README) must be English only. Write all new code in English; keep `ingestion/`, `.github/` and other code free of Chinese.
- Internal planning docs (`docs/fyp-design/`, `docs/data-source/`, `docs/context/my-context.md`, `docs/career/`, `docs/prompts/`, `docs/learning/`) may stay in Chinese, but must be excluded from or translated in any submission package. Before submitting, scan for CJK characters (e.g. `grep -rnP '[\x{4e00}-\x{9fff}]'`).

## Learning Guides (the student must understand every module)
- The student is learning while building and must be able to explain every part in reports, presentations and interviews. Code that works but is not understood does not count as done.
- **After each module is finished** (e.g. collector VM, bronze_sync, CI, local lakehouse, Spark jobs, dbt models, Airflow DAGs, streaming, dashboards, RQ experiments), remind the student and write or update a teaching guide in `docs/learning/` before moving on. Write it in Chinese, for a beginner: what each folder and file is for, the general logic and then the specifics, why each design choice was made, how to deploy, run and check it, common problems, what is not done yet, and hands-on exercises.
- Keep `docs/learning/README.md` as the index of guides, in recommended reading order.
- When explaining concepts in chat, assume no prior exposure: use plain language and concrete examples, and avoid unexplained jargon.
