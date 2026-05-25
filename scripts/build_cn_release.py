#!/usr/bin/env python3
"""Build a China-friendly static mirror and offline sharing package."""
from __future__ import annotations

import html
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist-cn"
ASSETS = ROOT / "assets"
README = ROOT / "README_CN.md"
SNAPSHOT_PDF = ROOT / "Tim_Zhang_Portfolio_Snapshot.pdf"
SNAPSHOT_HTML = ROOT / "Tim_Zhang_Portfolio_Snapshot.html"
OFFLINE_ZIP = ROOT / "Tim_Zhang_Portfolio_Offline.zip"
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
        "定位",
        "张威健（Tim Zhang）是一名数据工程与 AI 系统工程方向候选人，重点展示真实流程中的数据接入、建模、检索、评估、服务设计和云端部署能力。",
    ),
    (
        "代表项目",
        "SRR 智能体案件处理系统：岭南杯二等奖、广州电视台报道、公开参考实现，并标注 SRR 专利申请准备中。\n"
        "MCC FWA 保险理赔反欺诈图谱：展示 38,659 claims、1.61M nodes、2.57M edges、Neo4j/Spanner Graph-ready、FastAPI + LLM claims review。\n"
        "GaitGPT 临床步态分析智能助手：展示研究型 AI 工作流、文献检索、规则/模板优先架构和临床解释。\n"
        "企业数据平台：跨国零售企业级数据平台与商业银行数据中台，不展示具体公司名。",
    ),
    (
        "离线使用",
        "如果网页打不开，请优先打开 Tim_Zhang_Portfolio_Snapshot.pdf。若需要完整素材，可解压 Tim_Zhang_Portfolio_Offline.zip 后打开 index.html。",
    ),
    (
        "国内访问兜底",
        "主站继续保留 GitHub Pages；国内备用入口使用 EdgeOne Pages 默认域名上传 dist-cn/；暂无域名时不走 ICP 备案版正式站。",
    ),
]


def copy_site() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    shutil.copy2(ROOT / "index.html", DIST / "index.html")
    shutil.copytree(ASSETS, DIST / "assets", ignore=shutil.ignore_patterns(".DS_Store"))
    if README.exists():
        shutil.copy2(README, DIST / "README_CN.md")


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
  <p class="meta">生成时间：{generated_at} ｜ 国内访问兜底：GitHub Pages + EdgeOne Pages 镜像 + 离线包</p>
  {''.join(blocks)}
</body>
</html>
"""


def draw_pdf_with_fitz() -> None:
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
    put(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 国内访问兜底：GitHub Pages + EdgeOne Pages 镜像 + 离线包", 9, (0.38, 0.37, 0.34), 16)
    for title, body in SNAPSHOT_SECTIONS:
        put(title, 15, (0.72, 0.32, 0.21), 4)
        for paragraph in body.split("\n"):
            put(paragraph, 10, (0.08, 0.08, 0.07), 6)
        y += 4
    doc.subset_fonts()
    doc.save(SNAPSHOT_PDF, garbage=4, deflate=True)
    doc.close()


def write_snapshot_pdf() -> None:
    SNAPSHOT_HTML.write_text(snapshot_html(), encoding="utf-8")
    try:
        draw_pdf_with_fitz()
    except Exception as exc:
        resume = ASSETS / "docs/Tim_Zhang_Resume.pdf"
        if not resume.exists():
            raise
        shutil.copy2(resume, SNAPSHOT_PDF)
        print(f"Warning: snapshot PDF fallback copied resume because PDF rendering failed: {exc}")
    shutil.copy2(SNAPSHOT_PDF, DIST / SNAPSHOT_PDF.name)
    shutil.copy2(SNAPSHOT_HTML, DIST / SNAPSHOT_HTML.name)


def write_zip() -> None:
    if OFFLINE_ZIP.exists():
        OFFLINE_ZIP.unlink()
    with zipfile.ZipFile(OFFLINE_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(DIST.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(DIST))


def assert_release() -> None:
    index = (DIST / "index.html").read_text(encoding="utf-8")
    css = (DIST / "assets/css/styles.css").read_text(encoding="utf-8")
    assert "fonts.googleapis.com" not in index
    assert "fonts.gstatic.com" not in index
    assert "Global link / 海外链接" in index
    assert "Source Serif 4" not in css
    assert (DIST / "assets/docs/Tim_Zhang_Resume.pdf").exists()
    assert (DIST / "assets/videos/gaitgpt/gaitgpt-flash2.mp4").exists()
    assert SNAPSHOT_PDF.exists()
    assert OFFLINE_ZIP.exists()


def human_size(path: Path) -> str:
    size = path.stat().st_size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def main() -> None:
    copy_site()
    transform_index()
    transform_css()
    write_snapshot_pdf()
    write_zip()
    assert_release()
    print("China fallback package generated.")
    print(f"- {DIST.relative_to(ROOT)}/")
    print(f"- {OFFLINE_ZIP.name}: {human_size(OFFLINE_ZIP)}")
    print(f"- {SNAPSHOT_PDF.name}: {human_size(SNAPSHOT_PDF)}")


if __name__ == "__main__":
    main()
