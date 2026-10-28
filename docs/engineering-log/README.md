# Engineering Log

This log records how the pipeline evolved: what each version could not do, how the problem showed up, how it was diagnosed and what the next version changed. Each entry links to the commits and pull requests that contain the evidence.

The log feeds the FYP 1 report (Chapter 4, Preliminary Work), the FYP 2 report (Section 5.5, Implementation Issues and Challenges; Section 6.3, Project Challenges) and interview preparation.

## How entries are produced

1. After a problem is resolved, and before the pull request is merged, the student answers four debrief questions: what was expected, what was observed (which check, which numbers), how the cause was found, and what the next version changed and why it works.
2. Claude drafts the entry in English from that debrief, the commits, the pull request and the check outputs.
3. The student reviews the entry and corrects anything inaccurate.

Every entry states this in its header ("Drafted by Claude from the student's debrief; reviewed by the student").

## Provenance of findings

Many data-source issues were catalogued during the October 2026 desk study, which was AI-assisted (see `docs/data-source/data-source-summary.md` and its git history). Entries therefore separate two things:

- **Catalogued**: the issue already had an ID (E01–E45) in the desk study.
- **Encountered in implementation**: the check that exposed it during development, the date and the measured numbers.

An issue with no prior catalogue entry is marked **New finding**.

## Index

| # | Date | Module | Version change | What the earlier version could not do | Evidence | Provenance |
|---|---|---|---|---|---|---|

Entry files are named `NNNN-short-title.md` (for example `0001-test-isolation.md`). The template is [`TEMPLATE.md`](TEMPLATE.md).
