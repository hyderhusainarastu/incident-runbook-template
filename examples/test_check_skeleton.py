#!/usr/bin/env python3
"""Synthetic test for check_skeleton.py. Offline; standard library only."""
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "check_skeleton.py"


def run(root):
    return subprocess.run([sys.executable, str(SCRIPT), str(root)],
                          capture_output=True, text=True)


def main():
    assert run(HERE / "sample").returncode == 0, "good sample must pass"
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "worker.conf").write_text("WORKER_MEMORY_MB=128\n")
        (d / "main.c").write_text(
            "#define BIG 4096\nvoid main_loop(void) {\n char b[BIG];\n run_job(1);\n}\n")
        r = run(d)
        assert r.returncode == 1, r.stdout
        assert r.stdout.count("FAIL") == 3, r.stdout
    with tempfile.TemporaryDirectory() as d:
        assert run(d).returncode == 2, "missing input must exit 2"
    print("ok")


if __name__ == "__main__":
    main()
