# From incident to static check

A runbook tells a responder what to do after a failure. A static check stops the same failure from being reintroduced. This guide shows how to turn the "root cause" of a filled-in runbook into a small script that runs in CI and fails when the conditions behind the incident come back.

## When this fits

Use it when the cause is visible in committed source or config: a stack size, a buffer size, a pinned setting, a call that must go through a wrapper. It does not fit causes that only show at runtime, such as load or an upstream outage. Those stay in the runbook.

## Steps

1. **Write the cause as conditions.** Take the runbook's confirmed cause and list each condition that had to hold for the incident to happen. Example: "the job handler runs on the main thread", "the worker memory limit is below 512".
2. **Make each condition one named check.** One function per condition, with a name a reader can search for, and a message that says which file broke which rule and which runbook section to read.
3. **Put thresholds in constants at the top.** The numbers come from the fix, not from guesses. Record in a comment where each number came from.
4. **Resolve indirection.** If a value is set through a macro, constant or alias, resolve it within the same file before comparing. A check that only matches literals passes when someone swaps in a name.
5. **Choose the failure direction.** Prefer a false alarm over a miss. A failing check costs a human a minute; a missed regression costs another incident.
6. **Use exit codes.** `0` all checks pass, `1` at least one check failed, `2` the check could not run (missing input). Print one `PASS`/`FAIL` line per check.
7. **Add a synthetic test.** Feed the script a small fabricated file that violates each rule and one that satisfies all of them, and assert the exit codes. Without this, a check that never fires looks identical to a check that works.
8. **Run it in CI** and link it from the runbook's section 4 ("After identifying the cause").

## Skeleton

[`examples/check_skeleton.py`](../examples/check_skeleton.py) implements steps 1 to 6 against a fictional config and source file: a worker whose memory limit and job-handler placement caused a crash loop. The test in [`examples/test_check_skeleton.py`](../examples/test_check_skeleton.py) covers step 7. Run it with:

```sh
python3 examples/check_skeleton.py examples/sample
python3 examples/test_check_skeleton.py
```

Replace the constants, file names and patterns with your own.

## Limits

- A static check reads text. It cannot prove the system behaves; it only proves the known bad conditions are absent.
- Patterns are best effort. Review them when the code layout changes.
- Keep the number of checks small. Each one should map to a real past incident.
