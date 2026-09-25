---
name: tlc-verification-loop
description: Execute TLC on finite hardware models, diagnose syntax, safety, deadlock and liveness failures, and retain reproducible evidence without weakening requirements.
---

# TLC verification and remediation

## Input and output

Input: .tla, matching .cfg, source/property record, Java and tla2tools.jar, run budget.
Output: complete log, tool/config/model hashes, status, state counts, checked properties, and an iteration record. Tool unavailability or interrupted exploration means NOT VERIFIED.

## Run

Use the platform-independent Python runner in this repository from its root:

~~~text
python scripts/verify_model.py --jar "/path/to/tla2tools.jar" --model examples/nvme-cc-enable/NVMeCCEnable.tla --config examples/nvme-cc-enable/NVMeCCEnable.cfg --output verification/local-nvme
~~~

Use python3 if that is the installed command. Java and the JAR are external prerequisites; the runner does not install software, invoke an LLM, or change the model. It passes arguments without a shell, runs on an isolated copy, and records results.
For another project without this runner, use equivalent Java invocation:
java -cp "/path/to/tla2tools.jar" tlc2.TLC -workers 1 -config Model.cfg Model.tla
Save the complete command and log. Use model checking, not random simulation, for the exhaustive result.

Before running:
- Assign all constants needed by the specification, assumptions and properties.
- Include TypeOK and every claimed check in .cfg.
- Use SPECIFICATION Spec for temporal/fairness checks; do not also set INIT/NEXT.
- Translate PlusCal first if used.
- Default to deadlock checking. Do not add unconditional self-loops merely to hide a deadlock.
- Do not use symmetry reduction with liveness without establishing tool support and soundness.

## Diagnose and iterate

| Result | Response |
|---|---|
| Parse/semantic/config error | Repair syntax, resolution or assignments; this is not a counterexample. |
| TypeOK violation | Inspect the first invalid state and responsible update. |
| Safety/property violation | Preserve the trace; compare the first forbidden transition with the independent source claim. |
| Deadlock | Determine whether a source-permitted step is missing or termination is intentional. Disable checking only for a documented terminal abstraction. |
| Liveness failure | Inspect the cycle, enabling conditions and assumptions; fairness must have a reason beyond making TLC green. |
| Timeout/state explosion | Report inconclusive. Reduce only justified abstraction dimensions and identify the new bounds. |

Rerun after each repair. Retain property definitions and negative-test evidence.
Default to at most five repair attempts per requirement and 120 seconds per TLC run unless the user sets a different budget. Stop with an actionable unresolved report on repeated same-cause failures or an ambiguous source; never announce success because the budget ended.

Record iteration number, observed diagnostic, trace path, source comparison, changed artifact, reason, and rerun result. Do not label a deliberately injected test bug as an independently discovered hardware defect.

## Acceptance

Require a zero process exit code, TLC's completed/no-error marker, exhausted queue, and actual enabled check list. A missing log, aborted search, disabled property, or simulation does not pass.
Report temporal checks separately from invariant checks, plus fairness and bounds.
Promote dictionary candidates to model_checked only after checking; human approval is separate.
Re-run after any declaration, property, action, translation or configuration change.
