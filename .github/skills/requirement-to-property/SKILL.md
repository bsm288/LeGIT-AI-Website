---
name: requirement-to-property
description: Turn hardware requirements into independently stated TLA+ invariants, action safety properties, and qualified liveness properties; check for vacuous success.
---

# Requirement to property

Input: requirements, model state/actions, assumptions.
Output: named checked properties with a source-to-property table and at least one meaningful fault-detection test for the demonstrated behavior.

## Choose the temporal class

- State invariant P: true initially and in every reachable state; list with INVARIANT.
- Transition safety A: relation between current and next state; use a temporal property such as [][A]_vars and list with PROPERTY. Explain the permitted stuttering.
- Liveness P ~> Q: eventual progress under explicitly documented fairness/environment assumptions; list with PROPERTY and use a SPECIFICATION that includes those assumptions.

An action's guard alone is not an independently checked requirement. Do not define a property as "if this exact correct action occurs, then its own postcondition holds"; a bad alternate Next branch could escape that check.

## Worked NVMe checks

~~~tla
(* REQ-NO-WORK: NVMe Base 2.3, Figure 41, p.62 / PDF p.86.
 * Counts are persistent ghost histories; ccEn is the pre-state bit. *)
NoWorkWhileDisabled ==
    [][ccEn = 0 =>
        UNCHANGED <<processedCount, completedCount>>]_vars

(* REQ-ADMIN-PRESERVE: same source. Detect reset initiation/completion
 * by their bit edges, independently of the action implementations. *)
AdminPreservedOnReset ==
    [][((ccEn = 1 /\ ccEn' = 0) \/ (cstsRdy = 1 /\ cstsRdy' = 0)) =>
        adminConfig' = adminConfig]_vars
~~~

The full model also checks CompleteCountBounded as a state invariant and
EnableEventuallyReady under weak fairness. These are different claims.

## Match source meaning, not plausible formulas

For a plane counter, "counter <= THR2" and "counter <= number of qualifying blocks" are different properties. Resolve which is required from the actual source and client review; do not choose from the screenshot's diff direction or because one passes TLC.
If both are required, name and check both with their own source records.

For each fairness assumption, name the action and why the selected environment
permits eventual progress. Remove it in a temporary test and inspect the resulting
cycle; this tests whether the claim depends on the assumption, not whether real
hardware satisfies it.

Do not turn RDY's eventual clearing into ccEn = 0 => cstsRdy = 0. The reset-pending state is legal in the selected abstraction.
A violated property may reveal a wrong model, a wrong translation, missing assumptions, or a real design issue. Preserve the trace; do not automatically weaken the property or add fairness.

## Evidence and non-vacuity

For each check record its name, class, requirement ID or assumption ID, .cfg entry, dependencies, and result.
Use a temporary mutant that introduces the forbidden behavior and verify the intended property fails. A parser failure is not evidence that an invariant catches a bug.
Check reachability of relevant actions/states using a witness trace or coverage. In the supplied regression harness, deliberately false invariants yield witness traces for completion and reset-pending states. These expected failures are tests, not production requirements.

A passing small model is evidence for that finite abstraction, not proof of source completeness or all implementations.
