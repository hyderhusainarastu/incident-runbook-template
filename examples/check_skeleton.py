#!/usr/bin/env python3
"""Static regression guard skeleton: one named check per incident condition.

Fictional incident: a worker crash-looped because its memory limit was too low
and the job handler ran directly in the main loop. Adapt the constants, file
names and patterns to your own runbook.

Usage: python3 check_skeleton.py ROOT
Exit codes: 0 all checks pass, 1 a check failed, 2 input missing or bad usage.
"""
import re
import sys
from pathlib import Path

MIN_WORKER_MEMORY_MB = 512   # from the fix recorded in the runbook
MAX_STACK_ARRAY_BYTES = 1024  # largest local array allowed

CONF_FILE = "worker.conf"
SOURCE_FILE = "main.c"

_DEFINE_RE = re.compile(r"^#define\s+(\w+)\s+(\d+)\b", re.M)
_ARRAY_RE = re.compile(r"\bchar\s+\w+\s*\[\s*(\w+)\s*\]\s*;")


def check_memory_limit(conf: str):
    m = re.search(r"^WORKER_MEMORY_MB=(\d+)", conf, re.M)
    if not m:
        return f"{CONF_FILE}: WORKER_MEMORY_MB is not set (runbook section 3)"
    if int(m.group(1)) < MIN_WORKER_MEMORY_MB:
        return f"{CONF_FILE}: WORKER_MEMORY_MB={m.group(1)} is below {MIN_WORKER_MEMORY_MB}"
    return None


def check_handler_not_in_main_loop(src: str):
    m = re.search(r"void\s+main_loop\s*\([^)]*\)\s*\{", src)
    if not m:
        return f"{SOURCE_FILE}: main_loop() not found; has the signature changed?"
    depth, i = 1, m.end()
    while i < len(src) and depth:
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        i += 1
    if "run_job(" in src[m.end():i]:
        return f"{SOURCE_FILE}: run_job() called directly from main_loop(); use the worker wrapper"
    return None


def check_stack_arrays(src: str):
    defines = {k: int(v) for k, v in _DEFINE_RE.findall(src)}
    for size in _ARRAY_RE.findall(src):
        n = int(size) if size.isdigit() else defines.get(size)  # resolve #define
        if n is None:
            return f"{SOURCE_FILE}: cannot resolve array size '{size}'"
        if n > MAX_STACK_ARRAY_BYTES:
            return f"{SOURCE_FILE}: local array of {n} bytes exceeds {MAX_STACK_ARRAY_BYTES}"
    return None


def run(root: Path) -> int:
    conf_path, src_path = root / CONF_FILE, root / SOURCE_FILE
    for p in (conf_path, src_path):
        if not p.is_file():
            print(f"ERROR: missing input {p.name}", file=sys.stderr)
            return 2
    conf, src = conf_path.read_text(), src_path.read_text()
    checks = [
        ("memory_limit", check_memory_limit, conf),
        ("handler_not_in_main_loop", check_handler_not_in_main_loop, src),
        ("stack_arrays", check_stack_arrays, src),
    ]
    failed = 0
    for name, fn, text in checks:
        msg = fn(text)
        if msg:
            failed += 1
            print(f"FAIL {name}: {msg}")
        else:
            print(f"PASS {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(run(Path(sys.argv[1])))
