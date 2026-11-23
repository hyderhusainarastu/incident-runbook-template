# incident-runbook-template

A fill-in Markdown runbook template for one recurring service failure, plus a guide and script for turning an incident cause into a static check.

## Using this in your project

- Copy `TEMPLATE.md` to `docs/runbooks/<service>-failure-response.md` in the target repo.
- Replace every `[[PLACEHOLDER]]` with a real value taken from the project's own incident history. Do not invent failure signatures, commands or caveats; ask the user when unsure.
- Order failure signatures by how often each occurred, not by severity.
- Every signature needs a "This is not evidence that ..." caveat. Never ship a signature without one.
- Keep sections 1 (classify first), 4 (escalation and closure) and 5 (do not) intact.
- Read `examples/` first; they are fictional and must not be copied as facts.
- To add a regression guard, follow `docs/incident-to-static-check.md` and adapt `examples/check_skeleton.py`. Exit codes: 0 pass, 1 check failed, 2 input missing.
- Never write real hostnames, credentials or customer data into a runbook.
- A paste version for chat tools is in `PROMPT.md`.

## Working on this repo

- Setup: none. Python 3 standard library only.
- Test: `python3 examples/test_check_skeleton.py` (runs offline).
- Keep examples fictional. Do not edit `LICENSE`; it is the canonical CC BY 4.0 text.
