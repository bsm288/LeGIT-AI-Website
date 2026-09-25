---
name: global-identifier-dictionary
description: Consult and update the shared LeGIT/AI dictionary before and after modeling to keep variables and constants semantically consistent across specifications.
---

# Global identifier dictionary

## Input and output

Input: existing dictionary, source requirements, module declarations/configurations.
Output: sorted entries, a model-to-dictionary coverage report, and explicit conflicts.
Use dictionary/identifiers.json in this repository. A different canonical dictionary supplied by the user takes precedence; do not create a competing "global" file.

## Before modeling

Read the dictionary before choosing identifiers. Reuse a canonical name only when kind, meaning, units, ownership, domain and reset semantics agree.
Same spelling with different semantics is a conflict, not an alias. Preserve existing entries and present a proposed rename or namespace.
Use draft candidates while modeling; do not require a TLC pass before consulting existing entries.
If the canonical dictionary is absent, record that fact. In an authorized modeling
task, initialize draft entries at the designated path; in a read-only or isolated
test, retain local candidates and report the pending merge. Never label either
set client-approved without client review.

## Entry schema

~~~json
{
  "canonical": "ccEn",
  "kind": "VARIABLE",
  "role": "hardware",
  "meaning": "Controller Configuration Enable bit",
  "domain": "{0, 1}",
  "units": "bit",
  "owner": "host write, controller reset",
  "initial": "0",
  "reset": "0 for the modeled reset scope",
  "sources": [{"requirement_id": "REQ-CC-EN", "source_record": "examples/nvme-cc-enable/source.json"}],
  "model_refs": ["examples/nvme-cc-enable/NVMeCCEnable.tla:ccEn"],
  "aliases": [],
  "status": "draft"
}
~~~

Constants additionally record legal_domain, tested_values and abstraction_reason.
Ghost identifiers cite a model-assumption ID, not a fabricated hardware register source.
Opaque configuration tokens are abstraction values, not real register encodings.

## After modeling

1. Scan CONSTANTS and VARIABLES; use SANY success plus explicit declaration review for unfamiliar syntax. A regex inventory is only a consistency aid.
2. Ensure each declaration has exactly one matching entry and accurate reset/domain/source metadata. Separately document named operators; do not misclassify a zero-argument operator as a configurable CONSTANT.
3. Preserve other modules' entries and aliases. Sort by canonical name. Do not remove old entries merely because a new model omits them.
4. After a real TLC pass, record model_checked and the evidence location. Never automatically mark client_approved.
5. Re-run TLC after renames, and update .cfg and property/source references together.
6. Do not merge concurrent conflicting edits by silently taking one version.

## Gate

Unresolved collisions, missing source references, mismatched declarations, or outdated verification keep the affected entries in draft.
The supplied dictionary is a starting set for the demo, not a claim that every existing client model has already been inventoried.
