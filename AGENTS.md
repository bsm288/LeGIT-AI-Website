# LeGIT/AI agent entry point

For hardware specification extraction or TLA+/PlusCal modeling, read
[the workflow instructions](.github/copilot-instructions.md) and the applicable
SKILL.md files they link before acting. These are ordinary Markdown instructions;
they do not require a particular LLM provider.

Consult dictionary/identifiers.json before introducing variables or constants.
Use scripts/verify_model.py to execute TLC and retain evidence when available.
For setup, a runnable reference, and the client demonstration, read
[docs/SKILLS_DEMO.md](docs/SKILLS_DEMO.md).

If the agent host does not automatically load AGENTS.md or skills, the user must
attach these files or explicitly ask the agent to read them. Model-only chat
without file and terminal tools cannot run TLC.
