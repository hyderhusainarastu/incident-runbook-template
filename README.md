# Incident Runbook Template

A fill-in Markdown runbook for one recurring class of service failure (a background worker, a webhook consumer, a scheduled job). It makes the responder classify the failure before reading logs, and attaches a "not evidence of" caveat to every failure signature.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](LICENSE)

## Works with

| Surface | How | Status |
|---|---|---|
| By hand / any editor | copy `TEMPLATE.md` and fill the placeholders | not tested |
| ChatGPT / Claude.ai / Gemini (chat) | paste `PROMPT.md` plus the template | not tested |
| Claude Code, Codex, Cursor, Gemini CLI, Copilot | read `AGENTS.md` | not tested |

## What it encodes

1. **Classify before you read logs.** Cheap checks (deploy status, upstream status page) run first.
2. **Ranked failure signatures, each with a non-evidence caveat.** Each entry says what the failure is and what it does not prove, such as a stack trace after a deploy that is not caused by the deploy.
3. **A "Do not" section** listing remediations already tried on this failure class that made things worse.
4. **Separate escalation and closure criteria**, so "I think it is fixed" and "the incident is closed" are checked separately.

## Quick start

1. Copy `TEMPLATE.md` into your repo, for example `docs/runbooks/<service>-failure-response.md`.
2. Read the two examples in `examples/` to see a filled-in runbook.
3. Fill every `[[PLACEHOLDER]]`: identity (`[[SERVICE_NAME]]`, `[[HOSTING_PROVIDER]]`), commands (`[[DEPLOY_STATUS_COMMAND]]`, `[[LOG_RETRIEVAL_COMMAND]]`), failure signatures (`[[FAILURE_SIGNATURE_N]]` with `[[WHY_NOT_N]]`, ordered by how often each actually occurred) and policy (`[[ESCALATION_CRITERIA]]`).
4. Delete unused signature rows. Keep the signature plus caveat shape.
5. Optional: turn the confirmed cause into a CI check with [`docs/incident-to-static-check.md`](docs/incident-to-static-check.md) and [`examples/check_skeleton.py`](examples/check_skeleton.py).

Example caveat, from `examples/image-resize-worker-outage.md`:

> *This is not evidence that the main application database is misconfigured.* The main app's ORM client uses a different driver and is unaffected, so a working `pnpm db:migrate` is not evidence the worker will boot.

## Examples

- [`examples/image-resize-worker-outage.md`](examples/image-resize-worker-outage.md): fictional; a worker crash-looping after a credential rotation.
- [`examples/webhook-queue-backlog.md`](examples/webhook-queue-backlog.md): fictional; a webhook backlog from a signing-secret mismatch, plus a false-alarm case.
- [`docs/incident-to-static-check.md`](docs/incident-to-static-check.md) and [`examples/check_skeleton.py`](examples/check_skeleton.py): turn an incident cause into a static check (fictional config).

All company, service and platform names in the examples are invented.

## Limits

- Shaped for one recurring, already-understood failure class on one service. It is not an incident-response framework, an on-call handbook or a postmortem template.
- Only as good as your incident history. Signatures and caveats should come from something that was actually misdiagnosed once.
- Assumes a conventional deploy/runtime split (deploy-status API, retrievable logs, an upstream status page). Hardware faults or slow-burn degradation need restructuring.
- Nothing checks that a placeholder was filled in correctly. Review a filled-in runbook against a real past incident.

## Related

- [`project-memory-file-scaffold`](https://github.com/hyderhusainarastu/project-memory-file-scaffold)
- [`pre-publication-review-gate-checklist`](https://github.com/hyderhusainarastu/pre-publication-review-gate-checklist)
- [`cross-session-agent-handoff-prompt-template`](https://github.com/hyderhusainarastu/cross-session-agent-handoff-prompt-template)

Keywords: incident response, runbook, on-call, SRE, postmortem, troubleshooting, documentation template.

## License

Creative Commons Attribution 4.0 International (CC-BY-4.0). See [`LICENSE`](LICENSE).

Credit: hyderhusainarastu (https://github.com/hyderhusainarastu).

---

Part of [palimnote-templates](https://github.com/hyderhusainarastu/palimnote-templates) - more at https://github.com/hyderhusainarastu
