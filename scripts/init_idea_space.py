#!/usr/bin/env python3
"""Scaffold the 想法空间 (Idea Space) files into a workspace.

Usage:
    python scripts/init_idea_space.py "<workspace_absolute_path>"

Copies the clean templates from assets/ into the target workspace with the
proper Chinese filenames. Existing files are skipped (never overwritten).
"""
import os
import sys
import shutil

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL_DIR, "assets")

TARGETS = {
    "idea-space.template.md": "想法空间.md",
    "classification-index.template.md": "想法空间·分类索引.md",
    "integrated.template.md": "想法空间·整合版.md",
    "dream-notes.template.md": "做梦笔记.md",
}


def main() -> int:
    # A redirected Windows console may use a code page without Chinese glyphs.
    # Logging must not abort initialization or the existing-file preservation path.
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(errors='backslashreplace')
    if len(sys.argv) < 2:
        print("usage: init_idea_space.py <workspace_path>")
        return 1
    ws = sys.argv[1]
    missing = [src for src in TARGETS if not os.path.isfile(os.path.join(ASSETS, src))]
    if missing:
        print('missing templates: ' + ', '.join(missing))
        return 2
    os.makedirs(ws, exist_ok=True)
    for src, dst in TARGETS.items():
        s = os.path.join(ASSETS, src)
        d = os.path.join(ws, dst)
        if not os.path.exists(s):
            print(f"missing template: {s}")
            return 2
        if os.path.exists(d):
            print(f"skip (exists): {dst}")
        else:
            try:
                with open(s, 'rb') as source, open(d, 'xb') as target:
                    shutil.copyfileobj(source, target)
                print(f"created: {dst}")
            except FileExistsError:
                print(f"skip (exists): {dst}")
    print("done — 想法空间 scaffold ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
