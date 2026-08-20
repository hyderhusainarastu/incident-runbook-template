> **FICTIONAL EXAMPLE.** "Northwind Signals," "webhook-consumer," "Nimbus Run," "Aurora Queue,"
> and every command output below are invented for this template and do not refer to any real
> company, service, or incident.

# Runbook: webhook-consumer Failure Response

Standing procedure for diagnosing a Nimbus Run failure notification for `webhook-consumer`
(`svc-fict0hook077`). Written after incident `INC-FICT-031`; extends the Nimbus Run-specific
entries already tracked in `docs/ops/known-problems.md` rather than replacing them.

---

## 1. Classify the incident before reading any logs

```sh
# 1. Is this a deploy-time failure, or a runtime crash of an
#    otherwise-live deploy? Check deploy/release status before reading
#    a single log line.
nimbus deploys list svc-fict0hook077 --output json
#   - status "failed" -> deploy-time failure, go to §2.
#   - status "healthy" for the newest entry -> the deploy succeeded;
#     a notification means a runtime crash/backlog, go to §3.

# 2. External-outage check. Rule out the upstream webhook sender's own
#    outage before suspecting your own consumer.
curl -s https://status.example-crm-vendor.invalid/api/v2/status.json
```

Do not proceed to §2 or §3 until this classification step has produced a definite answer.

## 2. Deploy-time (build/boot) failure

1. Diff the failing commit against the last known-good deploy's commit.
2. Check: runtime version pin, lockfile compatibility, `.env`-loading behavior, build/start
   command, required environment variables present (never print values).
3. Reproduce the build locally: `pnpm install --frozen-lockfile && pnpm --filter
   webhook-consumer start` with a sanitized local environment.

## 3. Runtime crash / backlog of a live deploy

```sh
nimbus logs --resource svc-fict0hook077 --output json --limit 200 \
  --start <T-10min> --end <T+2min>
aurora queue depth --queue inbound-webhooks
```

Nimbus's CLI streams newline-delimited JSON, but only when `--output json` is combined with
`--limit`; omitting `--limit` silently reverts to a plain-text tail with no structure.

Look for, in order of how often each has actually occurred here:

1. **Queue depth climbing steadily with zero consumer errors in the log** — the consumer is
   healthy but throughput-bound (a fixed concurrency setting under a burst of inbound events).
   *This is not evidence of a stuck or crashed consumer.* A healthy consumer processing at a
   fixed rate under a burst produces exactly this shape; check the per-message processing
   latency before assuming anything is broken.

2. **`ERR_SIGNATURE_MISMATCH`** on inbound payload verification — follows a webhook-signing
   secret rotation on the sender's side that wasn't mirrored into `WEBHOOK_SIGNING_SECRET` here.
   *This is not evidence of a sender-side bug or an attack.* The sender's own dashboard almost
   always shows the rotation event with a timestamp; check there before treating every rejected
   payload as suspicious traffic. Fix shape: rotate the local secret to match, then replay the
   dead-lettered payloads that failed verification during the mismatch window.

3. **`ECONNRESET` bursts against the queue broker right after a broker-side credential
   rotation** — transient, typically self-resolving on retry within roughly 2 minutes.
   *This is not evidence of a bug in the consumer or a broker outage.* Aurora Queue's connection
   pool recycles credentials on a delay after rotation; retrying every ~15s resolved it here on
   the 5th attempt.

4. **`ENOTFOUND` on `queue.<region>.aurora.invalid`** — wrong broker hostname; the consumer must
   use the regional pooled endpoint (`pool-us-east.aurora.invalid`), never the legacy
   single-node hostname from an older config template.
   *This is not evidence of a DNS or network outage.* The legacy hostname was deprecated and
   removed from DNS entirely; this is a stale-configuration signature, not an infrastructure
   fault.

5. **Any crash reaching the error-reporting handler** — check the structured `[reportError]`
   log line first; it carries the webhook event type, source, and deploy commit.
   *This is not evidence that error-reporting covers every failure mode.* A broker-connection
   failure at startup (signature 3, above) happens before the error-reporting handler is even
   installed, so a startup crash-loop must be diagnosed from `nimbus logs` directly, never from
   the error-reporting dashboard.

## 4. After identifying the cause

1. Reproduce locally against a production-equivalent build with a sanitized environment.
2. Add a regression test that fails on the old behavior (here: a fixture payload signed with the
   stale secret).
3. Ship the smallest correct repair.
4. **Verify via a fresh deploy, not a restart.** A restart on Nimbus Run does not re-pull
   environment variables. Confirm the new instance's own startup log line, not just the API's
   200-status response, and confirm queue depth is actually draining afterward.
5. **Escalate if:** queue depth exceeds the dead-letter threshold before a fix ships, or the
   failure class has never been seen before. Escalation path: page the on-call rotation via the
   incident channel.
6. **Close the incident only when:** the fix is deployed *and independently verified* (queue
   depth returned to baseline, not just "the deploy succeeded"), a regression test exists, and
   the incident is recorded.
7. Record the incident in `docs/ops/incidents/`, and update this runbook if the failure class is
   new.

## 5. Do not

- Redeploy repeatedly hoping a transient issue clears without identifying the failure class
  first (§1).
- Treat a restart as equivalent to a fresh deploy for verifying an environment-variable or code
  change — Nimbus Run restarts reuse the previously-provisioned instance environment.
- Assume a climbing queue depth alone means the consumer is stuck — check per-message processing
  latency and consumer error rate before scaling up concurrency or restarting anything (§3,
  signature 1).
- Manually replay dead-lettered payloads before rotating the signing secret — replays sent
  against the still-mismatched secret will fail identically and pollute the dead-letter queue
  further.
- Close the incident on "the deploy succeeded" alone — see §4.6's closure bar.
