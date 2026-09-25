# Cross-model benchmark: NVMe CC.EN v1

This benchmark measures whether an agent follows the LeGIT/AI workflow for one fixed NVMe requirement family. It is a conformance and verification score, not a claim that the source interpretation is fully correct.

## Inputs given to every tested model

- Repository AGENTS.md, .github/copilot-instructions.md, and all five local skills.
- NVMe Base 2.3 source PDF only, pages 86 and 88.
- This benchmark file and golden.json.
- Java/TLC access and the specified TLA+ tools JAR.

Do not show a candidate the existing reference model, source record, prior candidate outputs, validation logs, or other candidate runs.

## Required candidate output

Write an isolated directory:

~~~text
candidate/
  Candidate.tla
  Candidate.cfg
  source.json
  README.md
~~~

source.json must use the schema in golden.json. The model must use the required property names in the table below. This makes automated comparison possible; it is not a rule for production model naming.

| Requirement | Required check | Required source location |
|---|---|---|
| REQ-CC-EN | TypeOK | Figure 41, printed 62 / PDF 86 |
| REQ-NO-WORK | NoWorkWhileDisabled | Figure 41, printed 62 / PDF 86 |
| REQ-ADMIN-PRESERVE | AdminPreservedOnReset | Figure 41, printed 62 / PDF 86 |
| REQ-ADMIN-WRITE | AdminWritesOnlyDisabled | Figure 41, printed 62 / PDF 86 |
| REQ-RDY | EnableEventuallyReady, ResetEventuallyDone | Figure 42, printed 64 / PDF 88 |

Model only normal operation. Record shutdown, fatal-error, timeout, transport, full-reset, and undefined-host-write behavior as exclusions or assumptions. The legal reset-pending state has CC.EN = 0 and CSTS.RDY = 1; do not assert they always equal.

## Automated score: 100 points

| Category | Points |
|---|---:|
| Candidate artifacts and valid JSON schema | 10 |
| Correct source revision/hash and required locations | 20 |
| All five requirement IDs, mapped checks, assumptions/exclusions | 25 |
| TLC completes with all required checks enabled | 35 |
| TLC evidence and a clear bounded-model statement | 10 |

A non-passing TLC run scores zero in the TLC category. The scorer saves the complete run evidence. It does not award semantic correctness based on string matching alone.

## Required manual semantic review

Two reviewers independently inspect source locations, model comments, abstractions, properties, and counterexample handling. They record source-faithfulness (0-5), property correctness (0-5), abstraction disclosure (0-5), and identifier consistency (0-5). Report agreement/disagreement rather than averaging away a dispute.

## Reporting

For each run record the model name/version, prompt, agent host/version, source PDF hash, tool/JAR hash, platform, elapsed time, automation score, manual score, TLC evidence path, and limitations. A result from one provider does not generalize to all LLMs.
