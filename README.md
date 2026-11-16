# email-triage-agent

A learning project: an AI agent that helps triage an email inbox by sorting messages into important, needs-reply, junk, and other, with safety as a design goal from the start. I'm building it step by step to learn how LLM applications work: API calls, conversation state, structured output, tool use, evaluation, and guardrails.

**Status: early development.** Only the first building block exists so far (see below). Everything under "Planned" is not built yet.

## What exists now

A terminal chat loop built on the Anthropic Python SDK. It demonstrates:

- Calling the Messages API through a single `ask()` function that returns the reply text and token counts
- Conversation state: the model has no memory between calls, so the program keeps a `messages` list and resends the full history every turn
- Token usage per turn, which shows how the cost of a conversation grows as history accumulates

## Setup

Requires Python 3 and an Anthropic API key.

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install anthropic python-dotenv
```

Create a `.env` file in the project folder (it is gitignored) containing:

```
ANTHROPIC_API_KEY=your-key-here
```

Then run:

```bash
python main.py
```

Type `quit` or `exit` to stop. Never commit your `.env` file or share your key.

## Planned

- [ ] Email classification with a system prompt and structured (validated) JSON output
- [ ] An evaluation set: hand-labeled emails, with a held-out portion never used for tuning, and scoring that weights "missed an important email" as worse than "showed a junk email"
- [ ] A no-tools baseline, then measured comparisons as each capability is added
- [ ] Read-only mailbox access, run first in dry-run mode
- [ ] Agent tools (context lookup, similar-email retrieval) added only where they improve the measured score
- [ ] Prompt-injection test set: malicious emails that try to give the model instructions
- [ ] Logging and per-request cost tracking
- [ ] FastAPI wrapper, tests with the model call mocked, and deployment
- [ ] Exposing the triage tools through an MCP server

## Design principles

These are goals for the system, not yet implemented:

- **Never delete.** The agent can only label, archive, or draft. Anything beyond that requires my approval.
- **Email content is data, never instructions.** The model gets only the tools it needs (no send, forward, or delete), and every action is logged.
- **Measure before adding complexity.** Each added layer (retrieval, tools, multiple agents) has to improve the evaluation score to stay.

## Data and privacy

No real emails are stored in this repository. Evaluation uses synthetic or properly licensed public data. Anything run against my real inbox stays local and private.
