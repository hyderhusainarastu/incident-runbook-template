# Runbook: [[SERVICE_NAME]] Failure Response

Standing procedure for diagnosing a [[HOSTING_PROVIDER]] failure notification for `[[SERVICE_IDENTIFIER]]` (`[[INTERNAL_SERVICE_ID]]`). Written after incident `[[INCIDENT_ID]]`; extends the [[HOSTING_PROVIDER]]-specific entries already tracked in `[[KNOWN_PROBLEMS_LOG_PATH]]` rather than replacing them.

Fill in every `[[PLACEHOLDER]]` before using this runbook. Delete this instruction line once done.

---

## 1. Classify the incident before reading any logs

The single most expensive mistake in an incident is reading logs before you know *what kind* of failure produced them — you'll pattern-match the first plausible-looking line instead of the actual cause. Establish the failure class first, cheapest checks first.

```sh
# 1. Is this a deploy-time failure, or a runtime crash of an
#    otherwise-live deploy? Check deploy/release status before reading
#    a single log line.
[[DEPLOY_STATUS_COMMAND]]
#   - status [[BUILD_FAILURE_STATUSES]] -> deploy-time failure, go to §2.
#   - status [[LIVE_STATUS_VALUE]] for the newest entry -> the deploy
#     succeeded; a notification means a runtime crash/restart, go to §3.

# 2. External-outage check. Rule out an upstream dependency's own
#    outage before suspecting your own configuration — a third-party
#    outage can produce an error message that looks identical to a
#    local misconfiguration (see the non-evidence caveats in §3).
curl -s [[UPSTREAM_STATUS_PAGE_URL]]
```

Do not proceed to §2 or §3 until this classification step has produced a definite answer. If the deploy/release status is ambiguous, treat that ambiguity itself as the first thing to resolve, not something to work around.

## 2. Deploy-time (build/boot) failure

1. Diff the failing commit against the last known-good deploy's commit.
2. Check: runtime/toolchain version, lockfile or dependency-manifest compatibility, [[ENV_FILE_LOADING_BEHAVIOR]], build/start command, required environment variables present (never print values).
3. Reproduce the build locally with a sanitized local environment: `[[LOCAL_BUILD_REPRODUCTION_COMMAND]]`.

## 3. Runtime crash of a live deploy

```sh
[[LOG_RETRIEVAL_COMMAND]]
```

[[LOG_FORMAT_QUIRK_NOTE]] — note any non-obvious parsing gotcha in the log output format here (e.g. "not a JSON array", "requires flag X to get structured output") so the next responder doesn't lose time rediscovering it.

Look for, in order of how often each has actually occurred here — **every signature below must carry an explicit non-evidence caveat**, because the fastest way to burn an on-call rotation is chasing a coincidental correlation:

1. **`[[FAILURE_SIGNATURE_1]]`** ([[COMPONENT_1]]) — [[ONE_LINE_DESCRIPTION_1]].
   *This is not evidence of [[WRONG_CONCLUSION_1]].* [[WHY_NOT_1 — explain what actually differs, e.g. a different subsystem, a different client, a coincidental timing overlap]]

2. **`[[FAILURE_SIGNATURE_2]]`** ([[COMPONENT_2]]) — [[ONE_LINE_DESCRIPTION_2]]. Typically follows [[TRIGGER_EVENT_2]] (e.g. a credential rotation).
   *This is not evidence of [[WRONG_CONCLUSION_2]].* [[WHY_NOT_2]] Fix shape: [[FIX_SHAPE_2]].

3. **`[[FAILURE_SIGNATURE_3]]`** — transient, typically self-resolving on retry within [[RETRY_WINDOW_3]].
   *This is not evidence of [[WRONG_CONCLUSION_3]] (e.g. a bug, a bad deploy, a permanent outage).* [[WHY_NOT_3]]

4. **`[[FAILURE_SIGNATURE_4]]`** on `[[HOST_PATTERN_4]]` — [[ONE_LINE_DESCRIPTION_4]].
   *This is not evidence of [[WRONG_CONCLUSION_4]].* [[WHY_NOT_4]]

5. **[[FAILURE_SIGNATURE_5 — e.g. "any crash reaching the error-reporting handler"]]** — check [[ERROR_REPORTING_LOCATION_5]] first; it carries [[CONTEXT_FIELDS_5]].
   *This is not evidence that [[WRONG_CONCLUSION_5 — e.g. "the error-reporting path covers every failure mode"]].* [[WHY_NOT_5 — name the failure class that happens BEFORE error-reporting handlers are installed, and where it must be diagnosed instead]]

Add or remove rows to match your service's actual signature history — the point of ranking by observed frequency is that the list should reflect real incidents, not a generic checklist copied from elsewhere. Never ship a signature without its caveat: an un-caveated signature is exactly what gets someone chasing the wrong fix at 3am.

## 4. After identifying the cause

1. Reproduce locally against a production-equivalent build with a sanitized environment before trusting a fix.
2. Add a regression test that fails on the old behavior.
3. Ship the smallest correct repair — resist bundling unrelated cleanup into an incident fix.
4. **Verify via a fresh deploy, not a restart.** [[RESTART_VS_DEPLOY_DISTINCTION]] Confirm the new instance's own startup log line, not just an API's 200-status response.
5. **Escalate if:** [[ESCALATION_CRITERIA — e.g. "the failure recurs after a verified fix", "the failure class is unprecedented", "estimated user impact exceeds threshold X"]]. Escalation path: [[ESCALATION_CONTACT_OR_CHANNEL]].
6. **Close the incident only when:** the fix is deployed *and independently verified* (not just "the deploy succeeded") *and* a regression test exists *and* the incident is recorded. A closed incident with any of these missing is not actually closed — it's a recurrence waiting to happen.
7. Record the incident in `[[INCIDENT_LOG_PATH]]` following the existing table/record shape, and update this runbook if the failure class is new.

## 5. Do not

- Redeploy repeatedly hoping a transient issue clears without identifying the failure class first (§1) — this burns deploy budget/minutes and destroys the timing signal you need to actually diagnose the problem.
- Treat a restart as equivalent to a fresh deploy for verifying an environment-variable or code change — [[RESTART_VS_DEPLOY_DISTINCTION_SHORT]].
- Assume a generic-looking network/auth error message means your own credential or connection needs fixing — check the relevant upstream status page first (§1, step 2).
- [[ADDITIONAL_FORBIDDEN_REMEDIATION_1 — a remediation that has actually been tried and made things worse or wasted time]]
- [[ADDITIONAL_FORBIDDEN_REMEDIATION_2]]
- Close the incident on "the deploy succeeded" alone — see §4.6's closure bar.
