# LeGIT/AI skills: client demonstration

The deliverable is five reusable agent skills, an NVMe reference model, a shared
identifier dictionary, and a repeatable TLC test harness. The skill bodies are
plain Markdown and do not call a specific LLM API.

## Open the project

Open the repository root in VS Code (the folder containing AGENTS.md and .github).
The .github/skills directory is hidden in some file explorers; VS Code can display
it normally. Each skill has its own SKILL.md, lowercase name and description.

| Stage | Instruction file |
|---|---|
| Requirements and exact source locations | [.github/skills/hardware-requirement-intake/SKILL.md](../.github/skills/hardware-requirement-intake/SKILL.md) |
| Constant/variable definitions and actions | [.github/skills/tla-state-identifiers/SKILL.md](../.github/skills/tla-state-identifiers/SKILL.md) |
| Requirement-to-property translation | [.github/skills/requirement-to-property/SKILL.md](../.github/skills/requirement-to-property/SKILL.md) |
| TLC execution and repairs | [.github/skills/tlc-verification-loop/SKILL.md](../.github/skills/tlc-verification-loop/SKILL.md) |
| Shared identifier management | [.github/skills/global-identifier-dictionary/SKILL.md](../.github/skills/global-identifier-dictionary/SKILL.md) |

## Reproduce the test

Prerequisites: Python 3.10+, Java compatible with your TLA+ tools JAR, and
tla2tools.jar. The scripts use only Python's standard library. They work without
Copilot or another LLM once a model exists. This separates model generation from
model checking.

From the repository root, replace the JAR path with its location on your machine.
Use python3 if that is your Python command. Each output directory must be new or
empty so earlier evidence is preserved.

~~~text
python scripts/verify_model.py --jar "/path/to/tla2tools.jar" --model examples/nvme-cc-enable/NVMeCCEnable.tla --config examples/nvme-cc-enable/NVMeCCEnable.cfg --output verification/local-demo-1
~~~

Expected reference result: PASS, 103 states generated, 60 distinct, 0 remaining,
depth 16 for the recorded tool version. Full logs and JSON evidence are saved in
the output directory. Counts may differ if the model/config/tool version changes.

To run all integration tests:

~~~text
python tests/test_skill_workflow.py --jar "/path/to/tla2tools.jar" --output verification/local-suite-1
~~~

Expected: 15 test cases pass. Nine cases deliberately inject faults and expect
TLC to reject them. Two cases use false invariants to obtain reachability
witnesses. Four cases are correct models/configurations that must pass TLC.
Do not present an expected negative-case TLC error as a failure of the final model.

## Six-minute meeting walkthrough

1. Show the PDF: NVMe Base 2.3, Figure 41, printed page 62 / PDF page 86.
   Point out the CC.EN work prohibition and Admin Queue preservation rule.
   Show Figure 42, printed page 64 / PDF page 88, for RDY.
2. Open the state/identifier skill. Explain the required declaration comments,
   domains, reset semantics, and separation of constants from changing state.
3. Open [NVMeCCEnable.tla](../examples/nvme-cc-enable/NVMeCCEnable.tla).
   Show CONSTANTS, VARIABLES, TypeOK, HostDisable, and the S1-S4/L1-L2 comments.
   These source-linked comments follow the readable style of the client's example.
4. Show [source.json](../examples/nvme-cc-enable/source.json) and
   [identifiers.json](../dictionary/identifiers.json). Explain that finite test
   bounds and ghost counters are modeling choices, not NVMe registers.
5. Run the single-model command above. Show the actual TLC completion message.
6. Open the saved disabled-processing counterexample from the acceptance tests,
   then its passing reference run. Explain that the property remained intact:
   the illegal behavior is what the model must exclude.

Say: "These skills guide extraction and model construction. TLC checks the
resulting finite model. We also inject faults to demonstrate that the checks
detect the behavior they prohibit."

## Fresh agent trial

Start a new Copilot Agent session, or another agent with workspace and terminal
access. If its host does not discover skills automatically, attach all five
SKILL.md files and explicitly ask it to read them. Naming a folder alone is not
proof the host loaded it.

Use this prompt:

~~~text
Read AGENTS.md, .github/copilot-instructions.md and the five .github/skills/*/SKILL.md
files. List the files you actually read.
Using the NVMe Base 2.3 PDF, model CC.EN and CSTS.RDY normal-operation handshake,
no processing/completion posting while disabled, and Admin Queue property
preservation. Read PDF pages 86 and 88 and retain exact source references.
Use dictionary/identifiers.json before choosing names.
Create a fresh model/config/source record under examples/my-nvme-trial.
Define every constant and variable with domain, owner, reset and meaning.
Record assumptions and excluded behavior; do not claim full reset coverage.
Run TLC with a finite configuration and save the complete log. Preserve the
requirements when fixing errors. Add one temporary fault-injection check to show
the forbidden event is detected.
Report actual results and unresolved issues. Do not commit or push.
~~~

If PDF extraction tools are unavailable, provide the selected page text plus
page images. The skill does not silently supply OCR or terminal access.

## Portability and limits

The instructions are provider-neutral; the tested command uses platform-neutral
Python subprocess calls and Java. Actual validation environments and skill
trials are listed in [VALIDATION.md](VALIDATION.md).

The first fixed cross-model comparison is recorded in
[the NVMe CC.EN results](../evaluation/cc-en-v1/RESULTS.md). It includes final
TLC evidence for GPT-5.6 and GPT-6, but it is one bounded NVMe case rather than
a general accuracy claim.

This is not a guarantee that every LLM follows the skills or produces a correct
interpretation. A new LLM/agent host must repeat the same source, property,
dictionary and TLC acceptance checks. Windows was executed here; macOS/Linux
remain untested. PlusCal translation, other NVMe domains, PCIe, and the entire
784-page specification are outside this example's test coverage.

TLC checks .tla/.cfg, not Markdown. A passing TLC run cannot establish that a
missing requirement was extracted, that an assumption matches hardware, or that
the chosen finite bounds prove arbitrary device sizes. Client semantic review
remains necessary.

## Review and publish

Suggested commit subject: "Add portable formal-modeling skills and TLC-tested NVMe example".
Review the .github/, AGENTS.md, dictionary/, examples/nvme-cc-enable/, scripts/,
tests/, docs/, .gitignore, and selected verification/ evidence together. Do not
bulk-stage unrelated existing models or PDFs. No credentials, JAR or PDF copy
is required by this change.
