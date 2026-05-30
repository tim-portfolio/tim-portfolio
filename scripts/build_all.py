#!/usr/bin/env python3
"""Regenerate portfolio and offline delivery assets."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAREEROS = ROOT.parent / "CareerOS"
RESUME_CHECK = CAREEROS / "profile" / "resume" / "check_resume_uniqueness.py"


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    run([sys.executable, "scripts/apply_profile.py"], ROOT)
    run([sys.executable, str(RESUME_CHECK), "--write-manifest", "--skip-archives"], ROOT)
    run([sys.executable, "scripts/build_cn_release.py"], ROOT)
    run([sys.executable, str(RESUME_CHECK)], ROOT)
    print("All portfolio assets rebuilt from content/profile.json; resume attachments remain canonical in CareerOS.")


if __name__ == "__main__":
    main()
