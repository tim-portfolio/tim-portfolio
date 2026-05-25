#!/usr/bin/env python3
"""Regenerate portfolio, resume, and offline delivery assets from one profile file."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSULTING = ROOT.parent / "咨询" / "00_当前主页与简历"
RESUME_SCRIPT = CONSULTING / "build_resume_v5.py"
RESUME_DOCX = CONSULTING / "Tim_Zhang_Resume_v5.docx"
RESUME_PDF = CONSULTING / "Tim_Zhang_Resume_v5.pdf"
RENDER_DIR = CONSULTING / "resume_v5_render"
RENDER_SCRIPT = Path("/Users/0xtt/.codex/plugins/cache/openai-primary-runtime/documents/26.521.10419/skills/documents/render_docx.py")
PORTFOLIO_RESUME = ROOT / "assets" / "docs" / "Tim_Zhang_Resume.pdf"


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    run([sys.executable, "scripts/apply_profile.py"], ROOT)
    run([sys.executable, str(RESUME_SCRIPT)], CONSULTING)
    if RENDER_DIR.exists():
        shutil.rmtree(RENDER_DIR)
    run([sys.executable, str(RENDER_SCRIPT), str(RESUME_DOCX), "--output_dir", str(RENDER_DIR), "--emit_pdf"], CONSULTING)
    rendered_pdf = RENDER_DIR / RESUME_PDF.name
    if not rendered_pdf.exists():
        raise RuntimeError(f"Rendered PDF not found: {rendered_pdf}")
    shutil.copy2(rendered_pdf, RESUME_PDF)
    shutil.copy2(rendered_pdf, PORTFOLIO_RESUME)
    run([sys.executable, "scripts/build_cn_release.py"], ROOT)
    print("All portfolio assets rebuilt from content/profile.json.")


if __name__ == "__main__":
    main()
