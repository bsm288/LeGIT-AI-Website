# AI cross-review: GPT-6 Sol NVMe CC.EN candidate

Reviewer: GPT-5.6 Sol
Review type: independent AI cross-review, not human approval
Candidate: `verification/cross-llm-final/gpt-6-sol-2026-09-24/candidate/`
Source scope: NVM Express Base Specification 2.3 (2025-08-01), Figure 41,
printed page 62 / PDF page 86, and Figure 42, printed page 64 / PDF page 88
Benchmark: `evaluation/cc-en-v1/BENCHMARK.md`

## Scores

| Dimension | Score | Assessment |
|---|---:|---|
| Source faithfulness | 5/5 | The model and source record accurately capture CC.EN reset/access behavior, the prohibition on processing and completion posting while disabled, Admin Queue property preservation and write restriction, and both RDY directions. The legal `ccEn = 0 /\ cstsRdy = 1` reset-pending state is explicit. Undefined writes and shutdown/fatal/timing exceptions are correctly separated from normal operation. |
| Property correctness | 4/5 | All required checks are independently stated rather than merely repeating action guards. The edge-based Admin preservation property, disabled-state write property, and fairness-qualified RDY leads-to properties match the abstraction. The deduction is for the no-work oracle: `processedCount` and `completedCount` are described as ghost histories but are reset in `HostDisable`. The property remains correct for the current transition system, yet per-interval reset makes it less mutation-resistant than monotonic persistent histories because a future disable action could erase evidence rather than expose it. No negative/mutant evidence is supplied in the reviewed artifacts. |
| Abstraction disclosure | 5/5 | Bounds, opaque Admin tokens, ghost-state role, nondeterministic Admin initialization, fairness, untimed interpretation, exclusions, unresolved referenced sections, and the limited meaning of a passing finite run are all clearly disclosed and mutually consistent. |
| Identifier consistency | 5/5 | Names are internally consistent, use suitable lower-camel/Pascal conventions, distinguish hardware and ghost state, and align across the module, source record, and README. The README correctly labels the names as local drafts pending the intentionally unavailable dictionary review. |

**Total: 19/20.** This total is only a concise summary of this review; the
benchmark requires reviewers' individual scores to remain visible rather than
averaging away disagreements.

## Semantic findings

No material source-faithfulness error was found in the reviewed candidate.
In particular:

- `HostDisable` leaves `cstsRdy` unchanged, and `ControllerResetDone` clears it
  later, so the model does not incorrectly equate CC.EN and CSTS.RDY.
- Processing and completion posting require both enabled and ready state. That
  is compatible with the page-88 host recommendation and is explicitly recorded
  as a normal-operation environment assumption rather than a new controller
  guarantee.
- Admin Queue property preservation covers both reset initiation and completion
  edges, while host modification is allowed only from a disabled pre-state.
- Weak fairness is limited to the controller's two readiness transitions and is
  disclosed as an assumption; no host fairness is silently introduced.

The one substantive review caveat is the reset of the two ghost counts on the
same transition that initiates Controller Reset. This is disclosed as
per-enable-interval accounting and does not falsify any current checked claim.
However, it weakens the stated rationale that the counts are histories and makes
`NoWorkWhileDisabled` a less durable fault detector: it verifies that transitions
whose pre-state is disabled leave the counters unchanged, but the histories do
not persist across reset initiation. A production-strength demonstration could
use monotonic lifetime event counters (with a justified finite saturation
scheme) or explicit process/post event flags, plus a deliberate mutant showing
that the property fails when disabled work is introduced.

## Client-demo suitability

The caveat does **not** block client demo use for this fixed benchmark. The
candidate is suitable as a bounded normal-operation workflow demonstration,
provided it is presented exactly as the README presents it: finite model-checking
evidence, not proof of complete NVMe extraction or implementation conformance.
It should not be represented as human-approved, dictionary-approved, or as
covering the referenced full-reset and timing clauses. Before reuse as a
production baseline, strengthen the no-work observer and add the required
non-vacuity/mutant evidence.
