# ADR-0001: Record architecture decisions

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-10-27 |
| Related | Design document v0.5 §14.1; `docs/engineering-log/` |

## Context
The design baseline (`docs/fyp-design/`) states what the system should be, but it is revised as the literature review and implementation evidence arrive. The FYP reports and interviews require the reason behind each design choice, the alternatives that were rejected, and the evidence that supported the decision at the time it was made. A single, continuously edited design document loses that history.

## Options considered
1. Rely on the design document's change log only. Little extra effort, but the change log records what changed, not the alternatives or the reasoning.
2. Record decisions in GitHub Issues. Searchable, but the reasoning lives outside the repository and is not versioned with the code.
3. Keep Architecture Decision Records as short Markdown files in the repository, following the format proposed by Nygard [1].

## Decision
Option 3. Each significant decision gets one numbered ADR under `docs/adr/`, written in English, citing the literature or the observed data that supports it. A changed decision is recorded as a new ADR that supersedes the old one.

## Consequences
- Report chapters on methodology and design can reference ADRs directly.
- The design document stays the description of the current target; ADRs explain how it got there.
- Small overhead per decision; only decisions that affect the architecture, data model, metrics or evaluation are recorded.

## References
[1] M. Nygard, "Documenting architecture decisions," Cognitect Blog, Nov. 2011. [Online]. Available: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
