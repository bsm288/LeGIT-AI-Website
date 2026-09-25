---
name: hardware-requirement-intake
description: Extract scoped, source-traceable requirements from NVMe, PCIe, or hardware design documents before generating TLA+ or PlusCal models.
---

# Hardware requirement intake

## Input and output

Input: source document plus revision, selected behavior/section, existing dictionary, and output directory.
Output: a source record, requirements-to-properties table, assumptions, exclusions, and unresolved dependencies. If the PDF cannot be read, report that fact and request/extract the relevant text; never infer its contents from its filename.

Record this schema (JSON or YAML) before modeling:

~~~yaml
source:
  document: "<title>"
  revision: "<revision>"
  sha256: "<actual source file hash>"
requirements:
  - id: "<stable ID>"
    location: {section: "<section>", figure: "<figure>", printed_page: 0, pdf_page: 0}
    statement: "<precise paraphrase or short exact quote>"
    class: "normative"
    actor: "<host/controller/environment>"
    preconditions: []
    model_actions: []
    checks: []
    status: "modeled"
assumptions: []
exclusions: []
unresolved_dependencies: []
~~~

The placeholders above describe a schema, not extracted evidence. Populate them; never invent page numbers or quotes. Track every in-scope normative statement as modeled, deferred, or blocked.

## Procedure

1. Read the complete relevant table row, footnotes, conditions, and referenced clauses needed for the chosen claim. Inspect a rendered page when table extraction is ambiguous.
2. Preserve must/shall, may, should, reset scope, actor, optional-feature conditions, and undefined behavior. A recommended host behavior may become a labeled environment assumption; it is not a controller guarantee.
3. Classify the domain: registers/properties, queues/transports, lifecycle, commands, or storage hierarchy. Route state definitions to tla-state-identifiers and claims to requirement-to-property. Record cross-domain dependencies; do not invent a domain-specific rule from a familiar name.
4. Consult global-identifier-dictionary before naming state. Separate fixed source values from finite exploration choices.
5. Limit the first model to a coherent requirement family. A full-document request needs an explicit coverage inventory and staged models; a passing excerpt model does not cover the PDF.

## Worked source example

NVMe Base 2.3 (2025-08-01), section 3.1.4.5, Figure 41, printed p.62 / PDF p.86:
- CC.EN is bit 0, RW, reset 0.
- While CC.EN is zero, command processing and completion posting are prohibited.
- Controller Reset preserves Admin Queue properties.
- RDY may remain one while reset completes; do not infer CC.EN = CSTS.RDY.
The RDY definition is in section 3.1.4.6, Figure 42, printed p.64 / PDF p.88.
Normal-operation modeling must exclude or handle the shutdown exceptions on those pages.

An event prohibition belongs to an action property, not a claim that all historical completion counts become zero when disabled.
The [executable example's source record](../../../examples/nvme-cc-enable/source.json) documents that distinction. Read it when using the example.

## Completion gate

Report the exact scope, coverage gaps, and assumptions. If a necessary referenced source is missing, stop that claim and retain a blocked entry; continue independent claims when useful.
