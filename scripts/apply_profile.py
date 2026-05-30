#!/usr/bin/env python3
"""Apply shared profile/contact data to portfolio sources."""
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "content" / "profile.json"
INDEX = ROOT / "index.html"
I18N = ROOT / "assets" / "js" / "i18n.js"


def read_profile() -> dict:
    return json.loads(PROFILE.read_text(encoding="utf-8"))


def marker_replace(text: str, marker: str, replacement: str) -> str:
    pattern = re.compile(
        rf"(<!-- PROFILE:{re.escape(marker)}:START -->).*?(<!-- PROFILE:{re.escape(marker)}:END -->)",
        re.S,
    )
    updated, count = pattern.subn(rf"\1\n{replacement}\n          \2", text)
    if count != 1:
        raise RuntimeError(f"Expected one marker block for {marker}, found {count}.")
    return updated


def js_marker_replace(text: str, marker: str, replacement: str) -> str:
    pattern = re.compile(
        rf"(// PROFILE:{re.escape(marker)}:START).*?(// PROFILE:{re.escape(marker)}:END)",
        re.S,
    )
    updated, count = pattern.subn(rf"\1\n{replacement}\n    \2", text)
    if count != 1:
        raise RuntimeError(f"Expected one JS marker block for {marker}, found {count}.")
    return updated


def apply_index(profile: dict) -> None:
    email = profile["email"]
    hk = profile["phones"]["hk"]
    mainland = profile["phones"]["mainland"]
    github = profile["github"]
    contact_html = f"""          <article class=\"contact-card reveal stagger\" style=\"--reveal-delay: 0.12s;\">
            <p class=\"card-label\">Email</p>
            <a href=\"mailto:{email}\">{email}</a>
          </article>
          <article class=\"contact-card reveal stagger\" style=\"--reveal-delay: 0.2s;\">
            <p class=\"card-label\">Phone</p>
            <p>{hk["label"]}: <a href=\"tel:{hk["tel"]}\">{hk["display"]}</a><br>{mainland["label"]}: <a href=\"tel:{mainland["tel"]}\">{mainland["display"]}</a></p>
          </article>
          <article class=\"contact-card reveal stagger\" style=\"--reveal-delay: 0.28s;\">
            <p class=\"card-label\">GitHub</p>
            <a href=\"{github["url"]}\" target=\"_blank\" rel=\"noopener\">{github["display"]}</a>
          </article>"""
    text = INDEX.read_text(encoding="utf-8")
    text = marker_replace(text, "CONTACT_CARDS", contact_html)
    INDEX.write_text(text, encoding="utf-8")


def apply_i18n(profile: dict) -> None:
    hk = profile["phones"]["hk"]
    mainland = profile["phones"]["mainland"]
    labels_js = f"""    \"Email\": \"邮箱\",
    \"Phone\": \"电话\",
    \"{hk["label"]}:\": \"{hk["label_cn"]}：\",
    \"{mainland["label"]}:\": \"{mainland["label_cn"]}：\",
    \"GitHub\": \"GitHub\","""
    text = I18N.read_text(encoding="utf-8")
    text = js_marker_replace(text, "CONTACT_LABELS", labels_js)
    I18N.write_text(text, encoding="utf-8")


def main() -> None:
    profile = read_profile()
    apply_index(profile)
    apply_i18n(profile)
    print("Profile applied to portfolio sources. Resume attachments are canonical in CareerOS/profile/resume.")


if __name__ == "__main__":
    main()
