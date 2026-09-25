# NVMe CC.EN benchmark candidate

This directory contains an isolated, finite TLA+ model for the normal-operation
CC.EN/CSTS.RDY requirement family in NVM Express Base Specification Revision 2.3.
The source scope is Figure 41 on printed page 62 / PDF page 86 and Figure 42 on
printed page 64 / PDF page 88.

`ccEn`, `cstsRdy`, and `adminConfig` abstract hardware/register state.
`processedCount` and `completedCount` are persistent ghost histories used to
check that no processing or completion posting occurs while disabled. `MaxWork`
is a finite exploration bound and is set to 2. The three Admin Queue properties
are represented together by one of two opaque values; no register encoding is
claimed. The legal reset-pending state `ccEn = 0 /\ cstsRdy = 1` is reachable.

The specification uses weak fairness for `BecomeReady` and `FinishReset` to
express eventual progress in normal operation. It does not model elapsed time
or CAP.TO. Shutdown, fatal-error behavior, transport behavior, full reset
effects, and source-defined undefined host writes are outside scope. A successful
TLC run establishes only the listed properties for this bounded abstraction; it
does not prove extraction completeness or conformance of an implementation.

## TLC execution

Run from this directory with Java and the specified tools JAR:

```text
java -cp C:/Users/aryan/.vscode/extensions/tlaplus.vscode-ide-2026.9.231551/tools/tla2tools.jar tlc2.TLC -workers 1 -config Candidate.cfg Candidate.tla
```

The complete output is retained in `tlc.log`. The actual exit status and model
checking result are recorded below after execution.

## Result

PASS. TLC exited with status 0 and reported `Model checking completed. No error
has been found.` The exhaustive breadth-first run generated 85 states, found 48
distinct states, left 0 states on the queue, and reached graph depth 11. TLC
checked `TypeOK` as an invariant and all five configured temporal properties:
`NoWorkWhileDisabled`, `AdminPreservedOnReset`, `AdminWritesOnlyDisabled`,
`EnableEventuallyReady`, and `ResetEventuallyDone`.

The successful run used TLC2 2026.09.23.154203 (revision 4260e47), OpenJDK
Temurin 25.0.2, Windows 11 amd64, one worker, complete breadth-first model
checking, and `MaxWork = 2`. The full successful-run console output is in
`tlc.log`.

SHA-256 evidence:

```text
Candidate.tla  2434e79bbea40bd83980446f1848fc89a1a801379c819f01c513fdb6ad857edd
Candidate.cfg  c3ec159dab69ca13344cd288c2611f1791a3cef0424ba3d0531f9fa7830d6a5e
source.json    e358febe5bafc56a63983dd2537b22a6fc4fc1e3c8962092da114d50e9c593a4
tlc.log        bcd1b48c8006bb73d5d343179d4c336ff41e9b8940c6095a73af834ffd965f6c
tla2tools.jar  32d64fbbc464559fc7192341b27b885fa4eb6b92d1648d2b49fb9cdcb7aacf81
```
