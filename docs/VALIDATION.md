# Validation record

Executed September 24, 2026 (America/Phoenix; some machine timestamps are
September 25 UTC). This report distinguishes skill packaging, model checking,
fault sensitivity, and agent behavior.

## Website-repository publication check (2026-09-25)

The skill suite, example model, configuration, and automated checks were copied
to the `bsm288/LeGIT-AI-Website` repository and re-run from that repository
before publication.

- Result: **15 of 15 verification cases passed**.
- TLC toolchain: TLC `2026.09.23.154203` (via the VS Code TLA+ extension).
- Coverage: four valid finite configurations completed without an error; nine
  seeded model/configuration faults and two deliberately false properties were
  detected as expected.
- The licensed NVMe PDF is intentionally not stored in this public website
  repository. `examples/nvme-cc-enable/source.json` preserves its SHA-256,
  revision, and page/figure citations. Re-run source-hash validation only in an
  authorized workspace containing the original PDF.

This demonstrates the repository workflow and bounded example; it does not
replace engineering review of source interpretation, abstraction boundaries,
or requirement coverage.

## Environment and reproducibility

- Windows 11; Python 3.13.7; Eclipse Adoptium Java 25.0.2.
- TLC 2026.09.23.154203, revision 4260e47.
- JAR SHA256: 32d64fbbc464559fc7192341b27b885fa4eb6b92d1648d2b49fb9cdcb7aacf81.
- One worker, fixed seed/fingerprint selection for the main suite, 512 MB heap,
  breadth-first model checking, no simulation or state constraints.
- Default deadlock detection remains enabled.
- All five skills pass the skill frontmatter/name validator.
- Python sources compile; the standalone verify_model.py CLI was also executed
  successfully, separately from the integration harness.

Reproduction commands and the meeting sequence are in [SKILLS_DEMO.md](SKILLS_DEMO.md).
The raw acceptance summary is
[summary.json](../verification/acceptance-after-config-parser-fix/summary.json).
Each case directory retains the actual .tla/.cfg inputs, full TLC log, command,
tool/input hashes, exit code, checks, states, and timing. These input snapshots
are intentionally retained so a counterexample can be reproduced.

## Correct-model results

| Configuration | Generated | Distinct | Queue remaining | Result |
|---|---:|---:|---:|---|
| MaxOperations=1 | 47 | 28 | 0 | PASS |
| MaxOperations=2 | 103 | 60 | 0 | PASS |
| MaxOperations=3 | 181 | 104 | 0 | PASS |
| MaxOperations=2, alternative initial Admin configuration | 103 | 60 | 0 | PASS |

All four configurations checked TypeOK, CompleteCountBounded,
NoWorkWhileDisabled, AdminPreservedOnReset, AdminWritesOnlyDisabled,
EnableEventuallyReady, and ResetEventuallyDone.
The two liveness claims use explicitly stated weak fairness. They do not prove
NVMe wall-clock timeout requirements.

## Negative cases and non-vacuity

The following are intentionally faulty models, not hardware defects found in
the NVMe specification. All nine were rejected with the expected diagnostic.

| Injected change | Expected detection |
|---|---|
| Process while EN=0 | NoWorkWhileDisabled action violation |
| Post completion while EN=0 | NoWorkWhileDisabled action violation |
| Lose Admin configuration at reset initiation | AdminPreservedOnReset action violation |
| Lose Admin configuration at reset completion | AdminPreservedOnReset action violation |
| Increment a counter beyond its finite domain | TypeOK invariant violation |
| Refer to an undefined operator | Semantic analysis failure |
| Omit enable-response fairness | EnableEventuallyReady liveness violation |
| Omit reset-response fairness | ResetEventuallyDone liveness violation |
| Remove all enabled transitions | Deadlock |

Two additional false-invariant tests produced witness traces showing that
completion posting and the legal EN=0/RDY=1 reset-pending state are reachable.
Thus the safety checks did not pass merely because no work/reset occurred.

The dictionary consistency check covered all nine reference-model declarations
(three constants, six variables) and matched the original PDF hash in the
authorized acceptance workspace. Entries are model_checked, not
client_approved. This initial dictionary does not inventory the repository's
legacy models.

## Changes prompted by review and testing

1. Replaced incomplete action snippets with an executable reference.
2. Moved dictionary consultation before model generation; kept client approval
   separate from TLC success.
3. Corrected event-prohibition modeling and preserved the allowed reset-pending
   state.
4. Added transition checks and fault/witness tests.
5. A first harness run misclassified a genuine liveness counterexample because
   this TLC version reports a singular property name. Fixed the diagnostic
   parser; did not alter the model/property to suppress the failure.
6. Extended Admin preservation checking to reset completion as well as initiation,
   then tested both faulty transitions.
7. Verified liveness dependence on each stated fairness assumption.

Earlier local rehearsals are ignored by Git; the final acceptance directory
contains the evidence for the final model.

## What this does and does not establish

The skill text is independent of the LLM provider. Its native discovery format
targets Copilot; AGENTS.md and explicit file attachments provide other entry
points. No model-specific API is embedded in the instructions or scripts.

Executed here: Windows TLC runs and one independent same-provider skill trial.
Not executed here: Copilot Agent Mode, Claude, Gemini, other LLMs, macOS/Linux,
PlusCal translation, or whole-document NVMe/PCIe generation.

TLC checks model/configuration behavior, not Markdown compliance or semantic
completeness of extraction. A new agent must demonstrate its own real TLC run
and preserve the same source/property gates. Client review is still required
for the selected abstraction, source interpretation, and proposed identifiers.
The screenshot influenced readable source/comment organization; it did not
establish a particular plane-counter equation or threshold for this NVMe model.

## Cross-model benchmark

The fixed NVMe CC.EN benchmark was executed independently by gpt-5.6-sol and
gpt-6-sol. Each generated a fresh candidate after reading the skills and source
pages, then passed TLC and scored 100/100 on the automated artifact/source/TLC
rubric. The scorer initially failed to recognize valid block-form TLC PROPERTY
syntax; it was repaired, the 15-case suite was rerun, and both candidates were
rescored from clean final evidence directories. Full results, AI cross-reviews,
and limitations are in [RESULTS.md](../evaluation/cc-en-v1/RESULTS.md).

This is a two-model, one-case result. The 100/100 number is a benchmark
conformance score, not a claim of 100% semantic accuracy or universal LLM
reliability. Human semantic review fields remain unfilled.
