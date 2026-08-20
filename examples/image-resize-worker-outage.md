> **FICTIONAL EXAMPLE.** "PixelForge," "img-resize-worker," "Cascade Cloud," "Fabledb," and every
> command output below are invented for this template and do not refer to any real company,
> service, or incident.

# Runbook: img-resize-worker Failure Response

Standing procedure for diagnosing a Cascade Cloud failure notification for `img-resize-worker`
(`svc-fict0resize001`). Written after incident `INC-FICT-014`; extends the Cascade Cloud-specific
entries already tracked in `docs/ops/known-problems.md` rather than replacing them.

---

## 1. Classify the incident before reading any logs

```sh
# 1. Is this a deploy-time failure, or a runtime crash of an
#    otherwise-live deploy? Check deploy/release status before reading
#    a single log line.
cascade releases list svc-fict0resize001 --output json
#   - status "build_failed"/"rollback" -> deploy-time failure, go to §2.
#   - status "running" for the newest entry -> the deploy succeeded;
#     a notification means a runtime crash/restart, go to §3.

# 2. External-outage check. Rule out an upstream dependency's own
#    outage before suspecting your own configuration.
curl -s https://status.example-imagelib.invalid/api/v2/status.json
```

Do not proceed to §2 or §3 until this classification step has produced a definite answer.

## 2. Deploy-time (build/boot) failure

1. Diff the failing commit against the last known-good deploy's commit.
2. Check: runtime version pin, lockfile compatibility, `.env`-loading behavior, build/start
   command, required environment variables present (never print values).
3. Reproduce the build locally with a sanitized local environment:
   `corepack enable && pnpm install --frozen-lockfile && pnpm --filter resize-worker start`.

## 3. Runtime crash of a live deploy

```sh
cascade logs --resource svc-fict0resize001 --output json --limit 200 \
  --start <T-5min> --end <T+2min>
```

Cascade's CLI emits concatenated JSON objects, not a JSON array — a plain `json.load()` fails
with "Extra data." Pipe through `jq -c .` or parse by tracking brace depth.

Look for, in order of how often each has actually occurred here:

1. **`ERR_UNSUPPORTED_COLOR_PROFILE`** (image-decode step) — a source image carries an ICC
   color profile the decode library doesn't recognize.
   *This is not evidence of a corrupted upload.* The same file opens fine in a standard image
   viewer; the decode library's profile table is simply narrower than what browsers accept.
   Confirmed by re-encoding the source with the profile stripped and re-running the same job.

2. **`ETLSCERTCHAIN` at startup, inside the internal job-queue client's own Postgres
   connection** (not the app's main DB client) — follows a `FABLEDB_URL` credential rotation
   plus a connection-string library upgrade that now maps `sslmode=require` to a stricter
   verification mode than the job-queue client's TLS bundle supports.
   *This is not evidence that the main application database is misconfigured.* The main app's
   ORM client uses a different underlying driver and is unaffected — `pnpm db:migrate` working
   fine is not evidence the worker will boot. Fix shape: build the job-queue client's config
   from discrete `host`/`port`/`user`/`password` fields instead of a single connection string,
   so an explicit `ssl: { rejectUnauthorized: false }` isn't silently overwritten by the
   connection-string parser's own defaults.

3. **`ECIRCUITBREAKER` / auth failures right after a DB password reset** — transient, typically
   self-resolving on retry within roughly 2 minutes.
   *This is not evidence of a bug or a wrong password.* Fabledb's connection pooler trips a
   temporary circuit breaker while the credential change propagates; retrying every ~20s
   resolved it here on the 6th attempt.

4. **`ENETUNREACH` on `db.<ref>.fabledb.invalid`** — wrong connection string; the worker must
   use the pooler endpoint (`pooler-us.fabledb.invalid:6543`), never the direct IPv6-only host.
   *This is not evidence of a network outage.* Cascade Cloud's egress has no IPv6 route to the
   direct host at all; this is a fixed, known limitation of the platform, not an intermittent
   fault.

5. **Any crash reaching the error-reporting handler** — check the structured `[reportError]`
   log line first; it carries the job id, resize preset, and deploy commit.
   *This is not evidence that error-reporting covers every failure mode.* A startup crash in
   the job-queue client (signature 2, above) happens before the error-reporting handler is even
   installed, so a startup crash-loop must be diagnosed from `cascade logs` directly, never from
   the error-reporting dashboard.

## 4. After identifying the cause

1. Reproduce locally against a production-equivalent build with a sanitized environment.
2. Add a regression test that fails on the old behavior (here: a fixture image carrying the
   unrecognized ICC profile).
3. Ship the smallest correct repair.
4. **Verify via a fresh deploy, not a restart.** A restart on Cascade Cloud does not re-pull
   environment variables or re-run the build step. Confirm the new instance's own startup log
   line, not just the API's 200-status response.
5. **Escalate if:** the failure recurs after a verified fix, or the failure class has never been
   seen before. Escalation path: page the on-call rotation via the incident channel.
6. **Close the incident only when:** the fix is deployed *and independently verified*, a
   regression test exists, and the incident is recorded.
7. Record the incident in `docs/ops/incidents/`, and update this runbook if the failure class is
   new.

## 5. Do not

- Redeploy repeatedly hoping a transient issue clears without identifying the failure class
  first (§1).
- Treat a restart as equivalent to a fresh deploy for verifying an environment-variable or code
  change — Cascade Cloud restarts reuse the previously-provisioned instance environment.
- Assume "could not read credentials" from the source-image library means the library's license
  key needs reissuing — check the upstream status page first (§1, step 2); a fictional prior
  incident here traced an identical message to an upstream partial outage.
- Retry a job indefinitely on `ERR_UNSUPPORTED_COLOR_PROFILE` — it will never succeed without
  the profile-stripping fix; retrying only burns queue capacity.
- Close the incident on "the deploy succeeded" alone — see §4.6's closure bar.
