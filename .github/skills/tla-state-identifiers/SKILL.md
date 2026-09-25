---
name: tla-state-identifiers
description: Define documented constants, variables, finite types, initialization, and complete atomic transitions for hardware TLA+ and PlusCal models.
---

# TLA+ state and identifier contract

## Input and output

Input: sourced requirement records, approved/candidate dictionary entries, finite test bounds.
Output: a .tla module, matching .cfg, and identifier records. Use the repository's canonical names; naming preferences never justify silently renaming existing public identifiers.

## Declaration contract

For every CONSTANT record meaning, units, legal domain, source or assumption, and .cfg assignment.
For every VARIABLE record meaning, owner, domain, initial value, reset/persistence behavior, and source or assumption.
Distinguish hardware state, environment state, and observer/ghost state. Ghost state records events for checking; it is not a hardware register.

Use lowerCamelCase variables, PascalCase domain/action names, and the existing project's constant conventions. Model values for distinct categories should not accidentally collide. Document sentinel disjointness and test it.

Fixed encodings may be zero-argument operators; configurable exploration bounds are CONSTANTS.
EXTENDS Naturals or Integers is allowed. What must be finite is every enumerated domain and reachable state: no unbounded counters, sequence growth, clocks, or quantification over Nat/Int. Never prune violations with an undocumented state constraint.

## Module order and style

Use MODULE matching the filename, overview/source/scope, EXTENDS, CONSTANTS with comments, ASSUME, VARIABLES with comments, vars, helpers, TypeOK, Init, actions, Next, Spec, and named properties.
Use the client's readable block-comment style: identifier, plain-language meaning, source location, and equation together. Preserve source-defined threshold bounds; a screenshot is a style reference, not sufficient normative evidence for a numerical threshold.

Every Init choice must have a source or assumption; nondeterministic initialization is permitted and useful.
TypeOK covers every variable and function/record component.
Every action constrains every primed variable, either through an update or UNCHANGED. Do not change atomicity to fix a trace without a source/abstraction justification.

## Worked action (complete within the executable example)

~~~tla
(* REQ-CC-EN: host enables only from the ready-to-enable state.
 * Source: NVMe Base 2.3, Figure 41, p.62 / PDF p.86.
 * ASSUME-NORMAL: no shutdown, fatal error, or invalid host write. *)
HostEnable ==
    /\ ccEn = 0
    /\ cstsRdy = 0
    /\ ccEn' = 1
    /\ UNCHANGED <<cstsRdy, adminConfig, commandPhase,
                    processedCount, completedCount>>
~~~

The full module, including all declarations and the six-variable tuple, is
[the tested NVMe example](../../../examples/nvme-cc-enable/NVMeCCEnable.tla).

For registers, preserve bit ranges, access semantics (RO/RW/RWC/RWS), reset conditions and reserved-value handling from the selected revision. A width w gives 0..(2^w-1), but a smaller abstraction needs justification.
For queues, verify the chosen transport's capacity convention; do not universally apply a one-slot-empty Full predicate to phase-tagged queues or Fabrics.
For command models, distinguish submission, processing, completion, and abort/reset effects; do not infer SQE/CQE layouts apply to every transport.
For hierarchy models, define finite sets and ownership mappings explicitly.

## PlusCal

When sequential processes clarify the requirement, retain the PlusCal source and regenerate TLA+ with the translator after each algorithm change. Check the translated module with TLC; never patch only the generated translation. Include pc and all translator-generated variables in type/frame reasoning. Mark PlusCal as untested if no translated example was run.

## Gate

Check each action's write/frame set, reset persistence, all Init states, and all constant assignments (including constants used only by properties or ASSUME). Send the result to requirement-to-property and tlc-verification-loop.
