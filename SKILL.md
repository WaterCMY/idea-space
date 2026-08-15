---
name: idea-space
slug: idea-space
displayName: 想法空间
version: 1.0.0
description: "Personal second-brain 'Idea Space' (想法空间) for WorkBuddy. Use when the user wants to capture daily thoughts, reflections, insights, and experiences into a structured, auto-summarized knowledge base. Triggers include phrases like 记一下, 记到想法空间, sending daily reflections, asking to 总结一下今天的想法, wanting a classified index, or wanting the nightly 21:30 auto-summary and the 03:00 cross-linking 'dreaming' automation configured. Covers the dual-write workflow (daily log plus category index), the 5-category taxonomy, entry formatting conventions, and the two automation prompts."
agent_created: true
---

# 想法空间 (Idea Space) — Personal Second-Brain Skill

A lightweight, file-based personal knowledge system. The user thinks out loud
daily; WorkBuddy captures, classifies, and periodically synthesizes it — without
ever replacing the user's own words or leaking their private journal.

## When to use

- First time: scaffold the system in the current workspace (run `scripts/init_idea_space.py`).
- Every day: the user sends thoughts/reflections/experiences → append to the daily log **and** sync to the category index (dual-write).
- "这个还没解决" → add to the 待解决 (Unsolved) list.
- "总结一下今天的想法" → produce a same-day summary.
- Optionally: configure the 21:30 nightly summary and 03:00 "dreaming" automations (see `references/automations.md`).

## Core files (all in the workspace root)

| File | Role |
|------|------|
| `想法空间.md` | **Daily log** — chronological, one `### YYYY-MM-DD（周X）` section per day. The source of truth. |
| `想法空间·分类索引.md` | **Category index** — same entries re-filed under 5 themes, each line links back to the daily log. |
| `想法空间·整合版.md` | **Integrated view** — merges an external material library (e.g. a Tencent Doc of curated content) × the user's own thinking, two columns per category (📥 摄入素材 / 💡 我的思考). Optional. |
| `做梦笔记.md` | **Dream log** — output of the 03:00 cross-linking automation. Optional. |

> Never put the user's private journal content into a shared/published copy of this skill. Templates in `assets/` are clean scaffolds only.

## The dual-write workflow (most important rule)

Every new entry is written to **both** the daily log and the category index.

1. Read the current `想法空间.md` (and the index if it exists) to find today's date section.
2. Append the entry under `### 2026-MM-DD（周X）` in `想法空间.md`.
3. Append a one-line index entry under the matching category in `想法空间·分类索引.md`.
4. Keep a running entry counter (思考N / 对话整理N / 方法卡N) consistent across both files.

## Entry format

Each entry in the daily log follows this shape:

```
- **💡 思考N · 标题（MM-DD 主题）**：一句话核心观点。→ 展开/实例/交叉引用。 — 类别：自我认知 / 沟通 — 状态：✅ 已想通（接 思考X / 待解决 #Y）
```

Type tags (prefix the bullet):
- `💡 思考N` — insight / reflection
- `💬 对话整理N` — a conversation transcript summary (WeChat / meeting)
- `🔥 待解决` — unsolved idea (track in the 待解决 list)
- `📈 市场学习` — market / investing observation
- `💢 事件/感受` — an event or emotional state
- `🛡 方法卡` — a reusable method/playbook (write standalone file + index link)
- `✅ 践行验证` — proof that a theory was acted on

Every entry ends with `— 类别：... — 状态：...` so the index can filter.

## The 5-category taxonomy (for `想法空间·分类索引.md`)

1. **🤖 如何用AI** — AI落地 / Agent / 工作流 / 个人IP工具
2. **🌱 个人成长** — 自我认知 / 情绪 / 人际沟通 / 健康
3. **🧠 认知** — 思维方法 / 价值观 / 新框架
4. **💼 职场** — 求职 / 规划 / 深耕方向 / 商业构想
5. **📈 投资** — 交易纪律 / 市场认知 / 持仓

The index file keeps a top "入口表" (date → entry count) and one section per category. Each line: `- **【MM-DD 类型N】标题**：一句话。状态：...`

## 待解决清单 (Unsolved list)

Maintained inside `想法空间.md` under `## 🔥 待解决想法清单` as a table:

```
| # | 想法 | 说明 | 起始日期 | 状态 |
|---|------|------|---------|------|
| 1 | ... | ... | 2026-MM-DD | 🔴 没思路 |
```

When an entry resolves, update its status and note the resolving 思考N.

## Setup

On first use in a workspace, run:

```bash
python scripts/init_idea_space.py "<工作区绝对路径>"
```

This scaffolds `想法空间.md`, `想法空间·分类索引.md`, and `做梦笔记.md` from the templates in `assets/`. (Use the managed Python: `C:/Users/cmy20/.workbuddy/binaries/python/versions/3.13.12/python.exe`.)

## Automations (optional but recommended)

See `references/automations.md` for the exact `automation_update` prompt text for:
- **21:30 每日总结** — summarizes the day's entries + reviews the 待解决 list.
- **03:00 做梦** — cross-links entries across categories, surfaces hidden threads, emits one falsifiable ⚠️ hypothesis.

Both append only; they never edit the daily-log source text.

## Principles

- **Append, never rewrite** the user's own words in the daily log.
- **Dual-write** every entry (log + index).
- **Cross-reference** with 思考N / 对话整理N / 待解决 #N so the graph stays connected.
- **Respect privacy** — templates are scaffolds; never ship the user's real journal.
- **Mark uncertainty** — append 🟡/🔴/⚠️ when an idea is tentative or a transcription is suspected wrong.
