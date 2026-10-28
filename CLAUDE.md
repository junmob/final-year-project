## FYP Academic Guidelines & Documentation Rules
- When drafting or structuring reports/chapters, STRICTLY comply with the guidelines and templates located in `docs/`:
  - Preliminary Proposal: Read `docs/context/proposal/guidelines.md` and `docs/context/proposal/template.md`
  - FYP 1: Read `docs/context/fyp1/guidelines.md` and `docs/context/fyp1/template.md`
  - FYP 2: Read `docs/context/fyp2/guidelines.md` and `docs/context/fyp2/template.md`
- Always verify chapter structure against the corresponding template before generating final text.
- Report drafts live in `reports/<phase>/` (`reports/proposal/`, later `reports/fyp1/`, `reports/fyp2/`); `docs/context/` holds only school reference material.
- Each phase follows its own guideline; `docs/context/fyp-index.md` is an index only. Submission dates: `docs/context/academic-calendar.md`.

## Project Baseline
- Current design baseline: `docs/fyp-design/fyp_project_design_v0.5.md` (v0.2/v0.3/v0.4 are archived in `docs/fyp-design/archive/`). Plain-language RQ explanations: `docs/fyp-design/rq-explained.md`. Literature gates G1–G3 and the design change protocol: v0.5 §10.7.
- Collector VM learning guide (how the VM, deployment and each collector work): `docs/learning/vm-collector-guide.md`.
- Data source facts and evidence: `docs/data-source/data-source-summary.md`.

## Language Rules (school-facing material)
- Everything under `reports/` must be written in English only (British English). No Chinese characters anywhere in school-facing material.
- Code that will be submitted (all source files, comments, log/print messages, configs, workflow files, README) must be English only. Write all new code in English; keep `ingestion/`, `.github/` and other code free of Chinese.
- Internal planning docs (`docs/fyp-design/`, `docs/data-source/`, `docs/context/my-context.md`, `docs/career/`, `docs/prompts/`, `docs/learning/`, `docs/tickets/`) may stay in Chinese, but must be excluded from or translated in any submission package. Before submitting, scan for CJK characters (e.g. `grep -rnP '[\x{4e00}-\x{9fff}]'`).
- `docs/engineering-log/` and `docs/adr/` are read by the supervisor and interviewers: English only (British English).

## Learning Guides (the student must understand every module)
- The student is learning while building and must be able to explain every part in reports, presentations and interviews. Code that works but is not understood does not count as done.
- **Working mode (agreed 2026-10-23): the student writes the core code; Claude acts as tech lead.**
  - Student writes (from Claude's tickets): the S1 profiling scripts, Spark Bronze → Silver jobs, DQ rules, dbt models, Airflow DAGs, the arrival-inference algorithm, KPI SQL, and the pytest tests for the collectors. For these, Claude writes the ticket (format: `docs/tickets/TEMPLATE.md`), answers library questions with small standalone examples, gives graded hints when asked (see "Learning route" below), and reviews the diff with `file:line` comments. Claude does not write or edit the student's task code.
  - Claude writes, student reviews and must be able to explain every line: infrastructure and boilerplate (docker compose, deploy scripts, CI workflow YAML, service configs).
  - Claude drafts report chapters; the student reads and revises them.
  - Claude drafts the English engineering log entries and ADRs (see below); the student reviews them.

## Learning Route (agreed 2026-10-27; rules only)
- Public rules: `docs/learning/curriculum.md` (stages S0–S6, hint ladder, spoiler zones, records). Ticket index and branch workflow: `docs/tickets/README.md`.
- The detailed plan (progress, ticket drafts, what each ticket will run into, hint texts, reproduction checks) lives outside the repository in `~/fyp-curriculum/`. The student has promised not to open it. Its `README.md` is the protocol.
- **Session start**: when the student starts ticket work (names a ticket, asks for a hint or a review, or says "开工"), read `~/fyp-curriculum/STATE.md` first, then only the needed part of the relevant card.
- **Session end**: when the student says "收工", update `STATE.md` and commit in `~/fyp-curriculum/`; in chat say only that progress was updated.
- **Never reveal hidden content** in chat, commit messages, PR comments or any repository file before the problem is resolved: no "watch out for X", no "you will find". Ticket titles describe goals only. Do not point the student to the spoiler zones listed in `curriculum.md` §10 before the stage that unlocks them.
- **Tickets** may omit information but must never state anything false or forbid the correct approach. Each ticket has a prediction box and generic checks (row counts, uniqueness, ranges, distributions, reconciliation). All library documentation the student needs is written into the ticket as Chinese mini-docs with runnable examples; official documentation links are optional further reading only.
- **Hints**: the student first writes a symptom note; then L1 where to look → L2 what to compute → L3 the concept's name → L4 full explanation and fix direction (the code is still the student's). Give a level only when asked; after about 90 minutes or two sessions stuck on the same symptom, offer the next level. When a problem is missed in review, point only to the check that disagrees with the prediction.
- Before issuing a ticket that depends on a property of the data, run the matching check in `~/fyp-curriculum/checks/` with the project `.venv` (read-only on `~/fyp-data/bronze/`).
- **After a problem is resolved**: explain it, ask a transfer question, ask the four debrief questions (expected / observed / how found / what v2 changed and why), then draft the engineering log entry in `docs/engineering-log/`. Keep provenance honest: "catalogued in the October desk study (Exx)" versus "encountered in implementation (check, numbers)" versus "new finding".
- Student code reads `~/fyp-data/bronze/` but never writes to it and never touches the VM; tests never call the network.
- Closed-book drills every two weeks (15–20 minutes); weak points are tracked in `STATE.md`.
- Effort: xhigh for stage transitions, gates, design revisions and report structure; high for tickets, reviews, hints and explanations.
- **After each module is finished** (e.g. collector VM, bronze_sync, CI, local lakehouse, Spark jobs, dbt models, Airflow DAGs, streaming, dashboards, RQ experiments), remind the student and write or update a teaching guide in `docs/learning/` before moving on (covering only problems that are already resolved). Write it in Chinese, for a beginner: what each folder and file is for, the general logic and then the specifics, why each design choice was made, how to deploy, run and check it, common problems, what is not done yet, and hands-on exercises.
- Keep `docs/learning/README.md` as the index of guides, in recommended reading order.
- When explaining concepts in chat, assume no prior exposure: use plain language and concrete examples, and avoid unexplained jargon.
