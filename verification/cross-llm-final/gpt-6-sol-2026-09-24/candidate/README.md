# NVMe CC.EN benchmark candidate

This isolated model covers normal CC.EN enable, command processing and CQ posting, Controller Reset initiation, Admin Queue property preservation and writes, and eventual CSTS.RDY transitions. The source is NVM Express Base Specification 2.3, 2025-08-01 Ratified, Figure 41 at printed page 62/PDF page 86 and Figure 42 at printed page 64/PDF page 88. `source.json` records the actual PDF SHA-256 and the source-to-check mapping.

The state has CC.EN and CSTS.RDY bits, an opaque Admin Queue configuration for AQA/ASQ/ACQ, and two bounded ghost event counts. The reset-pending state `ccEn = 0 /\ cstsRdy = 1` is reachable. A legal host clear resets the ghost counts and preserves Admin Queue configuration. The model does not enumerate real queue entries, command payloads, real register encodings, or elapsed time. A passing run is evidence only for this finite abstraction and its listed checks, not full hardware conformance or complete specification extraction.

Weak fairness on `ControllerReady` and `ControllerResetDone` supplies the normal-operation progress assumption for the two temporal checks. Host actions are not fair. Shutdown, fatal error, timeout, transport-specific state, full Controller Level Reset effects, and undefined host writes are outside scope; see `source.json` for the precise assumptions and exclusions. The source pages refer detailed reset and timing behavior to clauses not supplied to this candidate.

Run from this directory with:

```text
java -cp "C:/Users/aryan/.vscode/extensions/tlaplus.vscode-ide-2026.9.231551/tools/tla2tools.jar" tlc2.TLC -workers 1 -config Candidate.cfg Candidate.tla
```

`Candidate.cfg` enables `TypeOK`, `NoWorkWhileDisabled`, `AdminPreservedOnReset`, `AdminWritesOnlyDisabled`, `EnableEventuallyReady`, and `ResetEventuallyDone`. The full direct TLC run is saved as `tlc.log`.

Actual result (2026-09-24, Windows 11, Java 25.0.2): exit code 0; `Model checking completed. No error has been found.` TLC generated 36 states, found 18 distinct states, left zero on the queue, and checked two temporal-property branches. The finite state graph had depth 7. The model is exhaustive only within the disclosed two-token, two-event bounds. `tlc.log` preserves the complete output. The TLA+ tools JAR SHA-256 is `32d64fbbc464559fc7192341b27b885fa4eb6b92d1648d2b49fb9cdcb7aacf81`.

The repository dictionary was not consulted or edited because this isolated benchmark permits reading only the listed inputs. The names here are local draft candidates pending a dictionary consistency review; no entry is labeled client-approved.
