# Cross-model evaluation results: NVMe CC.EN v1

Date: September 24, 2026, America/Phoenix. Platform: Windows 11, Java 25.0.2,
TLC 2026.09.23.154203. Both agents received the same benchmark, skills,
AGENTS.md, source PDF pages 86 and 88, and the benchmark golden record. They
were isolated from the existing reference implementation and from each other.

The benchmark measures source/configuration conformance plus real TLC execution.
It is not a claim of general LLM accuracy or full NVMe semantic correctness.

| Model | Automated score | TLC result | Generated / distinct / queued | AI cross-review |
|---|---:|---|---:|---:|
| gpt-5.6-sol | 100 / 100 | PASS | 85 / 48 / 0 | 17 / 20 |
| gpt-6-sol | 100 / 100 | PASS | 36 / 18 / 0 | 19 / 20 |

Both final candidates enabled TypeOK, NoWorkWhileDisabled,
AdminPreservedOnReset, AdminWritesOnlyDisabled, EnableEventuallyReady, and
ResetEventuallyDone. The scorer reran TLC on an isolated copy and retained the
model/configuration, complete log, command, JAR hash, input hashes and score.

## GPT-5.6 result

[gpt-5.6 score record](../../verification/cross-llm-final/gpt-5.6-sol-2026-09-24/score.json)

GPT-5.6 first produced a parse-only error caused by a comment terminator or
transcription typo. It repaired the candidate, then TLC completed with no error.
Its final generated model is a finite normal-operation abstraction. GPT-6's AI
cross-review rated source faithfulness 4/5, property correctness 4/5,
abstraction disclosure 4/5, and identifier consistency 5/5. The reviewer found
no client-demo blocker. It noted that the cumulative two-command bound stops
new processing in later enable cycles, which must remain stated as a benchmark
limitation.

## GPT-6 result

[gpt-6 score record](../../verification/cross-llm-final/gpt-6-sol-2026-09-24/score.json)

GPT-6's final candidate passed TLC. GPT-5.6's AI cross-review rated source
faithfulness 5/5, property correctness 4/5, abstraction disclosure 5/5, and
identifier consistency 5/5. The reviewer found no client-demo blocker. It noted
that resettable per-interval ghost counters make the disabled-work property less
robust for certain future mutations than persistent histories or explicit event
flags. This does not invalidate the disclosed bounded demo, but it is a reason
to retain fault-injection testing for production baseline models.

## Interpretation for the client

Say:

> “We ran the same NVMe benchmark through GPT-5.6 and GPT-6. Both generated
> source-traceable finite TLA+ models that independently passed TLC and scored
> 100/100 on our automated conformance rubric. Their semantic AI cross-reviews
> found no demo blocker. The test is limited to one requirement family and still
> requires client review.”

Do not say “100% LLM accuracy.” The 100/100 score is the defined automated
benchmark score. The manual-review section of each score record remains blank
until two human reviewers inspect it. AI cross-review is useful additional
evidence, not client approval.

## Next benchmark expansion

Run the same protocol for at least:
- an NVMe queue/doorbell case;
- an NVMe shutdown/reset case;
- a PCIe state or transport case;
- Copilot Agent Mode and any external LLM host the client requires.

Report the model/host version, prompt, tool version, source revision, exact
bounds, raw TLC log, and both automated and human review results for every run.
