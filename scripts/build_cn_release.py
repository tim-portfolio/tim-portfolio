#!/usr/bin/env python3
"""Build bilingual portfolio delivery snapshots and a China-friendly mirror."""
from __future__ import annotations

import html
import io
import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist-cn"
ASSETS = ROOT / "assets"
README = ROOT / "README_CN.md"
README_EN = ROOT / "README_EN.md"
SNAPSHOT_PDF = ROOT / "Tim_Zhang_Portfolio_Snapshot.pdf"
SNAPSHOT_HTML = ROOT / "Tim_Zhang_Portfolio_Snapshot.html"
LONG_SCREENSHOT = ROOT / "Tim_Zhang_Portfolio_Long_Screenshot.png"
SNAPSHOT_PDFS = {
    "zh": ROOT / "Tim_Zhang_Portfolio_Snapshot_CN.pdf",
    "en": ROOT / "Tim_Zhang_Portfolio_Snapshot_EN.pdf",
}
LONG_SCREENSHOTS = {
    "zh": ROOT / "Tim_Zhang_Portfolio_Long_Screenshot_CN.png",
    "en": ROOT / "Tim_Zhang_Portfolio_Long_Screenshot_EN.png",
}
OFFLINE_ZIP = ROOT / "Tim_Zhang_Portfolio_Offline.zip"
DELIVERABLES = ROOT / "deliverables"
LATEST = DELIVERABLES / "latest"
PDF_FONT_NAME = "portfolio-cjk"
PDF_FONT_CANDIDATES = [
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
]
CJK_FALLBACK_FONT_NAME = "china-s"

GLOBAL_LINK_CSS = """

/* China mirror note: links to GitHub are optional external references. */
a[data-global-link="true"] .global-link-note {
  display: block;
  margin-top: 0.35rem;
  color: var(--brand);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0;
}

a.button[data-global-link="true"] .global-link-note,
a.text-link[data-global-link="true"] .global-link-note {
  display: inline;
  margin-left: 0.35rem;
  font-size: 0.68rem;
}
"""

SNAPSHOT_SECTIONS = [
    (
        "个人定位",
        "张威健（Tim Zhang）是一名数据工程与 AI 系统工程方向候选人，重点展示真实流程中的数据接入、建模、检索、评估、服务设计和云端部署能力。",
    ),
    (
        "代表项目",
        "SRR 智能体案件处理系统：岭南杯二等奖、RMB 10,000 奖金、广州电视台报道、CIC AI Award 展示、LUX 孵化启动展陈、公开参考实现，美国临时专利已提交（申请号 64/092,622）。\n"
        "SecureYield 金融科技方案：香港恒生大学大学联校金融科技创新概念比赛 2026 2nd Runner-up，HK$5,000 奖金，聚焦绿色算力 Token + RWA e-Token 双 Token 机制与三权分立合规模型，并提供参赛 landing page 与 technology page 作为项目证据。\n"
        "Uniflo / OpenUniflo 本地优先 Agent Runtime：展示任务空间、工作区权限、Skill 编排、trace、可复用 Application 候选和专利准备方向。\n"
        "MCC FWA 保险理赔反欺诈图谱：展示 38,659 claims、1.61M nodes、2.57M edges、Neo4j/Spanner Graph-ready、FastAPI + LLM claims review，并提供项目 landing page 与合作公司官方页作为背景材料。\n"
        "GaitGPT 临床步态研究双向翻译桥梁：SVIIF 2026 金奖及两项特别奖、LUX 孵化启动展陈、美国临时专利已提交（申请号 64/092,416）；论文准备中，演示视频现已公开。\n"
        "企业数据平台：跨国零售企业级数据平台与商业银行数据中台，不展示具体公司名。",
    ),
    (
        "核心能力",
        "数据工程、智能体工作流、医疗/金融 AI、检索管线、数据质量自动化、FastAPI 服务和云端部署。",
    ),
    (
        "查看方式",
        "这是一份个人主页快照，用于在网页暂时无法访问时快速了解项目结构和代表成果。",
    ),
]


def copy_site() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    shutil.copy2(ROOT / "index.html", DIST / "index.html")
    shutil.copy2(ROOT / "go.html", DIST / "go.html")
    shutil.copytree(
        ASSETS,
        DIST / "assets",
        ignore=shutil.ignore_patterns(".DS_Store", "Tim_Zhang_Resume*.pdf", "Tim_Zhang_Resume*.docx"),
    )
    if README.exists():
        shutil.copy2(README, DIST / "README_CN.md")
    if README_EN.exists():
        shutil.copy2(README_EN, DIST / "README_EN.md")


def remove_google_fonts(index_text: str) -> str:
    lines = []
    for line in index_text.splitlines():
        if "fonts.googleapis.com" in line or "fonts.gstatic.com" in line:
            continue
        lines.append(line)
    return "\n".join(lines) + "\n"


def annotate_github_links(index_text: str) -> str:
    pattern = re.compile(r'(<a\b(?=[^>]*href="https://github\.com/)(?![^>]*data-global-link)[^>]*>)(.*?)(</a>)', re.S)

    def repl(match: re.Match[str]) -> str:
        start, body, end = match.groups()
        start = start[:-1] + ' data-global-link="true" title="Global link / 海外链接">'
        if "global-link-note" not in body:
            body = f'{body}<span class="global-link-note">Global link / 海外链接</span>'
        return start + body + end

    return pattern.sub(repl, index_text)


def transform_index() -> None:
    index_path = DIST / "index.html"
    text = index_path.read_text(encoding="utf-8")
    text = remove_google_fonts(text)
    text = annotate_github_links(text)
    index_path.write_text(text, encoding="utf-8")


def transform_css() -> None:
    css_path = DIST / "assets/css/styles.css"
    text = css_path.read_text(encoding="utf-8")
    text = text.replace('--font-serif: "Source Serif 4", Georgia, serif;', '--font-serif: Georgia, "Times New Roman", "Songti SC", "STSong", serif;')
    text = text.replace('--font-sans: "Manrope", "Helvetica Neue", Arial, sans-serif;', '--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;')
    text = text.replace('--font-mono: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;', '--font-mono: "SFMono-Regular", Consolas, "Liberation Mono", monospace;')
    text += GLOBAL_LINK_CSS
    css_path.write_text(text, encoding="utf-8")


def snapshot_html() -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    blocks = []
    for title, body in SNAPSHOT_SECTIONS:
        paragraphs = "".join(f"<p>{html.escape(line)}</p>" for line in body.split("\n"))
        blocks.append(f"<section><h2>{html.escape(title)}</h2>{paragraphs}</section>")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>张威健 Portfolio Snapshot</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; color: #141413; line-height: 1.65; margin: 44px; }}
    h1 {{ font-size: 28px; margin: 0 0 8px; }}
    h2 {{ font-size: 18px; margin: 24px 0 8px; color: #9a4f35; }}
    p {{ margin: 0 0 8px; }}
    .meta {{ color: #666; margin-bottom: 22px; }}
  </style>
</head>
<body>
  <h1>张威健（Tim Zhang）Portfolio Snapshot</h1>
  <p class="meta">生成时间：{generated_at} ｜ 个人主页快照</p>
  {''.join(blocks)}
</body>
</html>
"""


def capture_homepage_screenshot(language: str) -> bool:
    capture_script = ROOT / "scripts/capture_web_snapshot.mjs"
    if not capture_script.exists():
        return False
    screenshot_path = LONG_SCREENSHOTS[language]
    if screenshot_path.exists():
        screenshot_path.unlink()
    url = (ROOT / "index.html").resolve().as_uri()
    result = subprocess.run(
        ["node", str(capture_script), url, str(screenshot_path), f"--lang={language}"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print("Warning: homepage screenshot capture failed; using text snapshot fallback.")
        if result.stderr.strip():
            print(result.stderr.strip())
        return False
    return screenshot_path.exists()


def screenshot_to_pdf(language: str) -> None:
    import fitz  # type: ignore
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    image = Image.open(LONG_SCREENSHOTS[language])
    pdf_path = SNAPSHOT_PDFS[language]
    page_width = 595
    page_height = 842
    margin = 18
    target_width = page_width - (margin * 2)
    scale = target_width / image.width
    slice_height = int((page_height - (margin * 2)) / scale)

    doc = fitz.open()
    y = 0
    while y < image.height:
        bottom = min(image.height, y + slice_height)
        crop = image.crop((0, y, image.width, bottom))
        stream = io.BytesIO()
        crop.save(stream, format="PNG", optimize=True)
        display_height = crop.height * scale
        page = doc.new_page(width=page_width, height=display_height + (margin * 2))
        rect = fitz.Rect(margin, margin, margin + target_width, margin + display_height)
        page.insert_image(rect, stream=stream.getvalue())
        y = bottom
    doc.save(pdf_path, garbage=4, deflate=True)
    doc.close()
    image.close()


def draw_pdf_with_fitz(output_path: Path = SNAPSHOT_PDF) -> None:
    import fitz  # type: ignore

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    font_path = next((candidate for candidate in PDF_FONT_CANDIDATES if candidate.exists()), None)
    if font_path:
        page.insert_font(fontname=PDF_FONT_NAME, fontfile=str(font_path))
        font_name = PDF_FONT_NAME
    else:
        font_name = CJK_FALLBACK_FONT_NAME
    margin = 48
    y = 52

    def put(text: str, size: int = 11, color: tuple[float, float, float] = (0.08, 0.08, 0.07), gap: int = 12) -> None:
        nonlocal page, y
        rect = fitz.Rect(margin, y, 595 - margin, 812)
        needed = max(42, (len(text) // 32 + 1) * (size + 7))
        if y + needed > 812:
            page = doc.new_page(width=595, height=842)
            y = 52
            rect = fitz.Rect(margin, y, 595 - margin, 812)
        page.insert_textbox(rect, text, fontname=font_name, fontsize=size, color=color, lineheight=1.25)
        y += needed + gap

    put("张威健（Tim Zhang）Portfolio Snapshot", 20, (0.08, 0.08, 0.07), 8)
    put(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 个人主页快照", 9, (0.38, 0.37, 0.34), 16)
    for title, body in SNAPSHOT_SECTIONS:
        put(title, 15, (0.72, 0.32, 0.21), 4)
        for paragraph in body.split("\n"):
            put(paragraph, 10, (0.08, 0.08, 0.07), 6)
        y += 4
    doc.subset_fonts()
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()


def render_pdf_preview(pdf_path: Path, image_path: Path) -> None:
    import fitz  # type: ignore

    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pix.save(image_path)
    doc.close()


def write_snapshot_pdf() -> None:
    SNAPSHOT_HTML.write_text(snapshot_html(), encoding="utf-8")
    for language in ["zh", "en"]:
        if capture_homepage_screenshot(language):
            screenshot_to_pdf(language)
        elif language == "zh":
            try:
                draw_pdf_with_fitz(SNAPSHOT_PDFS[language])
            except Exception as exc:
                raise RuntimeError("Chinese snapshot PDF rendering failed.") from exc
            render_pdf_preview(SNAPSHOT_PDFS[language], LONG_SCREENSHOTS[language])
        else:
            shutil.copy2(SNAPSHOT_PDFS["zh"], SNAPSHOT_PDFS[language])
            if LONG_SCREENSHOTS["zh"].exists():
                shutil.copy2(LONG_SCREENSHOTS["zh"], LONG_SCREENSHOTS[language])
            else:
                render_pdf_preview(SNAPSHOT_PDFS[language], LONG_SCREENSHOTS[language])
            print("Warning: English screenshot failed; copied Chinese snapshot as fallback.")
    shutil.copy2(SNAPSHOT_PDFS["zh"], SNAPSHOT_PDF)
    shutil.copy2(LONG_SCREENSHOTS["zh"], LONG_SCREENSHOT)
    for path in [SNAPSHOT_PDF, *SNAPSHOT_PDFS.values(), *LONG_SCREENSHOTS.values()]:
        if path.exists():
            shutil.copy2(path, DIST / path.name)
    shutil.copy2(SNAPSHOT_HTML, DIST / SNAPSHOT_HTML.name)
    if LONG_SCREENSHOT.exists():
        shutil.copy2(LONG_SCREENSHOT, DIST / LONG_SCREENSHOT.name)


def write_zip() -> None:
    if OFFLINE_ZIP.exists():
        OFFLINE_ZIP.unlink()
    with zipfile.ZipFile(OFFLINE_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(DIST.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(DIST))


def write_english_readme() -> None:
    README_EN.write_text(
        """# Weijian (Tim) Zhang Portfolio Offline Package

This is an offline version of the portfolio for quick review when the website is temporarily unavailable.

## Quick View

| File | Purpose |
|---|---|
| `Tim_Zhang_Portfolio_Snapshot_EN.pdf` | English PDF snapshot |
| `Tim_Zhang_Portfolio_Snapshot_CN.pdf` | Chinese PDF snapshot |
| `index.html` | Full offline portfolio page |
| `assets/` | Images, videos, and page assets |

## How to Use

1. Open `Tim_Zhang_Portfolio_Snapshot_EN.pdf` first.
2. Use `Tim_Zhang_Portfolio_Snapshot_CN.pdf` if a Chinese version is preferred.
3. To view the full page experience, unzip the package and open `index.html`.
4. Resume attachments are managed separately in CareerOS and are not packaged here.

## Content Highlights

- SRR Agentic Case Processing System
- SecureYield FinTech competition-winning proposal with landing and technology pages
- Uniflo / OpenUniflo multi-end intelligent continuous delivery platform
- MCC FWA insurance claims fraud graph intelligence with project and partner-company evidence links
- GaitGPT bidirectional clinical gait translation bridge
- Enterprise data platform experience across multinational retail and commercial banking
""",
        encoding="utf-8",
    )


def write_deliverables() -> None:
    if LATEST.exists():
        shutil.rmtree(LATEST)
    LATEST.mkdir(parents=True, exist_ok=True)
    files = [
        SNAPSHOT_PDFS["zh"],
        SNAPSHOT_PDFS["en"],
        LONG_SCREENSHOTS["zh"],
        LONG_SCREENSHOTS["en"],
        OFFLINE_ZIP,
        README,
        README_EN,
    ]
    for path in files:
        if path.exists():
            shutil.copy2(path, LATEST / path.name)
    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "commit": current_commit(),
        "files": [
            {
                "name": path.name,
                "size_bytes": path.stat().st_size,
                "size": human_size(path),
            }
            for path in files
            if path.exists()
        ],
        "command": "python3 scripts/build_cn_release.py",
    }
    (LATEST / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def current_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def assert_release() -> None:
    index = (DIST / "index.html").read_text(encoding="utf-8")
    css = (DIST / "assets/css/styles.css").read_text(encoding="utf-8")
    assert "fonts.googleapis.com" not in index
    assert "fonts.gstatic.com" not in index
    assert "Global link / 海外链接" in index
    assert "Source Serif 4" not in css
    assert not any((DIST / "assets/docs").glob("Tim_Zhang_Resume*"))
    assert not any(LATEST.glob("Tim_Zhang_Resume*"))
    with zipfile.ZipFile(OFFLINE_ZIP) as archive:
        assert not any("Tim_Zhang_Resume" in name for name in archive.namelist())
    assert (DIST / "assets/videos/gaitgpt/gaitgpt-flash2.mp4").exists()
    assert SNAPSHOT_PDF.exists()
    assert SNAPSHOT_PDFS["zh"].exists()
    assert SNAPSHOT_PDFS["en"].exists()
    assert LONG_SCREENSHOTS["zh"].exists()
    assert LONG_SCREENSHOTS["en"].exists()
    assert OFFLINE_ZIP.exists()


def human_size(path: Path) -> str:
    size = path.stat().st_size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def main() -> None:
    write_english_readme()
    copy_site()
    transform_index()
    transform_css()
    write_snapshot_pdf()
    write_zip()
    write_deliverables()
    assert_release()
    print("Portfolio delivery package generated.")
    print(f"- {DIST.relative_to(ROOT)}/")
    print(f"- {LATEST.relative_to(ROOT)}/")
    print(f"- {SNAPSHOT_PDFS['zh'].name}: {human_size(SNAPSHOT_PDFS['zh'])}")
    print(f"- {SNAPSHOT_PDFS['en'].name}: {human_size(SNAPSHOT_PDFS['en'])}")
    print(f"- {OFFLINE_ZIP.name}: {human_size(OFFLINE_ZIP)}")


if __name__ == "__main__":
    main()
