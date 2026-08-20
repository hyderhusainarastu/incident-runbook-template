# Incident Runbook Template

A fill-in-the-blanks template for writing a runbook for one recurring class of service failure
(a background worker, a webhook consumer, a scheduled job, anything with deploy logs and a
process that can crash) — structured so the response starts with *classifying* the failure
instead of pattern-matching the first scary log line.

## The problem this solves

Most incident runbooks are written after the fact as a narrative of what happened, which makes
them hard to act on under pressure: the reader has to reverse-engineer "what do I actually do"
from a story. And most runbooks that *do* give steps skip the part that actually saves time —
telling the reader which conclusions a given symptom does **not** support. A stack trace that
happens to appear right after a deploy gets blamed on the deploy; a generic auth error gets
blamed on your own credentials when it was an upstream outage the whole time. Without an explicit
caveat next to each signature, every responder re-derives (or mis-derives) that judgment call
from scratch, every time, usually at 3am.

This template encodes four things directly:

1. **Classify before you read logs.** The cheapest, fastest checks (deploy status, upstream
   status page) run first, before anyone opens a log stream and starts pattern-matching.
2. **Ranked failure signatures, each with a non-evidence caveat.** Every entry says not just
   "this is the failure," but explicitly what it is *not* evidence of — the wrong conclusion a
   tired responder is most likely to jump to.
3. **A "Do not" section.** Concrete remediations that have actually been tried on this failure
   class and made things worse or wasted time, not a generic checklist.
4. **Explicit escalation and closure criteria.** So "I think it's fixed" and "this incident is
   closed" are two different, separately-checked things.

## Quick start

1. Copy `TEMPLATE.md` into your own repo, e.g. `docs/runbooks/<service>-failure-response.md`.
2. Read the two worked examples in `examples/` first — they show what a filled-in template looks
   like end to end, including how the non-evidence caveats read once populated with real detail.
3. Fill in every `[[PLACEHOLDER]]`. The placeholders fall into a few groups:
   - **Identity:** `[[SERVICE_NAME]]`, `[[SERVICE_IDENTIFIER]]`, `[[HOSTING_PROVIDER]]` — what
     the service is called and where it runs.
   - **Commands:** `[[DEPLOY_STATUS_COMMAND]]`, `[[LOG_RETRIEVAL_COMMAND]]`,
     `[[LOCAL_BUILD_REPRODUCTION_COMMAND]]` — the actual CLI invocations for your platform.
   - **Failure signatures:** `[[FAILURE_SIGNATURE_N]]` / `[[WHY_NOT_N]]` pairs — the ranked list,
     each with its caveat. Order by how often each has *actually* occurred, not by how severe it
     sounds.
   - **Policy:** `[[ESCALATION_CRITERIA]]`, `[[ADDITIONAL_FORBIDDEN_REMEDIATION_N]]` — the
     judgment calls specific to your team.
4. Delete any signature rows you don't need, and add more following the same `signature` +
   *non-evidence caveat* shape — that shape is the part worth keeping even if you rewrite
   everything else.

**Before:** a generic "check the logs" note, or a narrative postmortem nobody can act on mid-
incident.

**After** (from `examples/image-resize-worker-outage.md`):

> **`ETLSCERTCHAIN` at startup, inside the internal job-queue client's own Postgres connection**
> (not the app's main DB client) — follows a `FABLEDB_URL` credential rotation plus a
> connection-string library upgrade...
> *This is not evidence that the main application database is misconfigured.* The main app's ORM
> client uses a different underlying driver and is unaffected — `pnpm db:migrate` working fine is
> not evidence the worker will boot.

That second sentence — the caveat — is the entire point of this template. It's the thing a
runbook without this structure almost never bothers to write down, and the thing that saves the
most time when someone else is holding the pager.

## Why each section exists

- **§1 Classify first** exists because the cost of misclassifying a failure (chasing a runtime
  bug that was actually a deploy failure, or vice versa) is much higher than the cost of one
  cheap status check. Put the cheapest, fastest-to-run checks first.
- **§2/§3 (deploy-time vs. runtime)** are split because they have almost nothing in common as
  investigations — different commands, different evidence, different fixes — and conflating them
  is exactly what makes a first response start in the wrong place.
- **§3's ranked signatures** are ordered by observed frequency, not by theoretical severity,
  because the goal is matching real incident history, not covering every hypothetical. The
  non-evidence caveat on each one exists because a responder under pressure will otherwise chase
  the first plausible correlation instead of the actual cause.
- **§4's escalation/closure split** exists because "the deploy succeeded" and "the incident is
  actually resolved" are different claims, and conflating them is how an incident gets marked
  closed while still recurring quietly.
- **§5 Do not** exists because remediations that feel obviously right under pressure (redeploy
  again, restart the process, assume it's your own credentials) are often the exact things that
  have already been tried on this failure class and made it worse or wasted the response window.

## Examples

- [`examples/image-resize-worker-outage.md`](examples/image-resize-worker-outage.md) — a fully
  fictional worked example: an image-resize background worker crash-looping after a database
  credential rotation.
- [`examples/webhook-queue-backlog.md`](examples/webhook-queue-backlog.md) — a fully fictional
  worked example: a webhook consumer backlog caused by a signing-secret mismatch, plus a
  false-alarm throughput case.

Both examples invent every company, service, and platform name involved and are labeled as
fictional at the top of the file.

## Limitations

- This template is shaped for **one recurring, already-understood failure class** on **one
  service** — an ongoing crash-loop pattern, a known backlog cause, something your team has seen
  before and wants to respond to faster next time. It is not a general incident-response
  framework, an on-call handbook, a postmortem template, or a substitute for actually
  investigating a genuinely novel failure.
- The ranked-signature list is only as good as your team's real incident history. A freshly
  filled-in template with invented or guessed signatures (rather than ones drawn from actual past
  incidents) will read fine and help nobody — the non-evidence caveats in particular need to come
  from something that was actually misdiagnosed once, not a hypothetical.
- It assumes a fairly conventional deploy/runtime split (a platform with its own deploy-status
  API, a process that logs to a retrievable stream, an upstream status page worth checking). A
  failure mode that doesn't fit that shape — a hardware fault, a data-corruption issue with no
  crash signature, a slow-burn degradation with no discrete "incident" moment — will need
  sections added or restructured, not just filled in.
- Nothing here validates that you filled in a placeholder *correctly* — a wrong command or a
  caveat that doesn't actually hold will read just as confidently as a correct one. Review a
  filled-in runbook the way you'd review any other on-call documentation, ideally against a real
  past incident.

## License

Creative Commons Attribution 4.0 International (CC-BY-4.0). See [`LICENSE`](LICENSE).
