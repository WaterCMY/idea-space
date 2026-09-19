---
name: idea-space
slug: idea-space
displayName: 想法空间
version: 1.2.0
description: "Personal second-brain 'Idea Space' (想法空间) for WorkBuddy. Use when the user wants to capture daily thoughts, reflections, insights, and experiences into a structured, auto-summarized knowledge base. Triggers include phrases like 记一下, 记到想法空间, sending daily reflections, asking to 总结一下今天的想法, wanting a classified index, or wanting the midnight 00:00 auto-summary and the 03:00 cross-linking 'dreaming' automation configured. Covers the dual-write workflow (daily log plus category index), the 5-category taxonomy, entry formatting conventions, the auto-distill conversation rule, and the two automation prompts."
agent_created: true
---

# 想法空间 (Idea Space) — Personal Second-Brain Skill

A lightweight, file-based personal knowledge system. The user thinks out loud
daily; WorkBuddy captures, classifies, and periodically synthesizes it — without
ever replacing the user's own words or leaking their private journal.

## When to use

- First time: scaffold the system in the current workspace (run `scripts/init_idea_space.py`).
- Every day: the user sends thoughts/reflections/experiences → append to the daily log and regenerate its managed category index.
- "这个还没解决" → add to the 待解决 (Unsolved) list.
- "总结一下今天的想法" → produce a same-day summary.
- Substantive conversation → distill only after workspace opt-in (see *Auto-distill* below).
- Optionally: configure the 00:00 midnight summary and 03:00 "dreaming" automations (see `references/automations.md`).

## Core files (all in the workspace root)

| File | Role |
|------|------|
| `想法空间.md` | **Daily log** — chronological, one `### YYYY-MM-DD（周X）` section per day. The source of truth. |
| `想法空间·分类索引.md` | **Category index** — same entries re-filed under 5 themes, each line links back to the daily log. |
| `想法空间·整合版.md` | **Integrated view** — merges an external material library (e.g. a Tencent Doc of curated content) × the user's own thinking, two columns per category (📥 摄入素材 / 💡 我的思考). Optional. |
| `做梦笔记.md` | **Dream log** — output of the 03:00 cross-linking automation. Optional. |

> Never put the user's private journal content into a shared/published copy of this skill. Templates in `assets/` are clean scaffolds only.

## Reliable append workflow

The daily log is the source of truth. New records get a stable caller-generated ID;
the category index is derived from their metadata and links to explicit anchors.

1. Use `python scripts/idea_store.py "<workspace>" record --id <stable-id> --date YYYY-MM-DD --category 认知 --title "标题" --body-file "<private-body-file>"`.
2. Reuse the same ID on retry. The script locks the workspace, atomically appends once, then rebuilds the managed index section.
3. Run `python scripts/idea_store.py "<workspace>" check`. If an index update was interrupted, run `reindex`; do not append the entry again with a new ID.
4. Existing unmarked journal entries and manually maintained index text are preserved. Do not silently migrate or delete them.
5. Keep body files in the user's private workspace, never in the distributable skill. The human-readable 思考N label may remain, but the stable ID controls deduplication.

## Auto-distill conversations (opt-in per workspace)

Default to archiving explicit requests such as “记一下”. Automatically distill substantive conversations only when the current user has opted in for this workspace. A preference from another person's installation is not authorization. Never publish private entries with the skill.

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

The generated index keeps date counts and one section per category, with stable anchor links to the daily log. Preserve any legacy manual index above the generated section.

## 待解决清单 (Unsolved list)

Maintained inside `想法空间.md` under `## 🔥 待解决想法清单` as a table:

```
| # | 想法 | 说明 | 起始日期 | 状态 |
|---|------|------|---------|------|
| 1 | ... | ... | YYYY-MM-DD | 🔴 没思路 |
```

When an entry resolves, update its status and note the resolving 思考N.

## Setup

On first use in a workspace, run:

```bash
python scripts/init_idea_space.py "<工作区绝对路径>"
```

This scaffolds `想法空间.md`, `想法空间·分类索引.md`, and `做梦笔记.md` from the templates in `assets/`. Use Python 3.10+ from the current environment; no personal absolute runtime path is required.

## Automations (optional but recommended)

See `references/automations.md` for the exact `automation_update` prompt text for:
- **00:00 每日总结** — runs at midnight, so it archives "yesterday" using `idea_store.py archive --kind summary` (default timezone Asia/Shanghai); summarizes the day's entries + reviews the 待解决 list.
- **03:00 做梦** — cross-links entries across categories, surfaces hidden threads, emits one falsifiable ⚠️ hypothesis.

Both append only; they never edit the daily-log source text.

## Principles

- **Append, never rewrite** the user's own words in the daily log.
- **Dual-write** every entry (log + index).
- **Auto-distill** substantive conversation into entries by default.
- **Cross-reference** with 思考N / 对话整理N / 待解决 #N so the graph stays connected.
- **Respect privacy** — templates are scaffolds; never ship the user's real journal.
- **Mark uncertainty** — append 🟡/🔴/⚠️ when an idea is tentative or a transcription is suspected wrong.
