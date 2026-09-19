# 想法空间 (Idea Space) — WorkBuddy Skill

一个跑在 WorkBuddy 工作区里的**个人第二大脑**。每天把你的思考 / 感悟 / 反思 / 经历发给我，我按固定结构归入「每日记录」并同步到「分类索引」，再配上两个自动化：**00:00 每日总结**与**03:00 凌晨做梦（跨域联想）**。

> 本仓库即一个 WorkBuddy 技能（Skill）。安装后在对话里说「记一下」「总结一下今天的想法」即可触发。

## 核心文件

| 文件 | 作用 |
|------|------|
| `想法空间.md` | 每日记录（按日期流水，第一手真相） |
| `想法空间·分类索引.md` | 分类索引（5 大类重排，每条回链主文档） |
| `想法空间·整合版.md` | 整合版（外部素材库 × 我的思考，可选） |
| `做梦笔记.md` | 凌晨做梦输出（跨域暗线 + 可证伪假设） |

## 工作流（日志为准，索引派生）

新条目通过 `scripts/idea_store.py record` 写入日志，再生成带稳定锚点的分类索引。重试复用条目 ID，避免重复；旧格式日志和人工索引保留。

条目类型标签：`💡 思考N` / `💬 对话整理N` / `🔥 待解决` / `📈 市场学习` / `💢 事件·感受` / `🛡 方法卡` / `✅ 践行验证`。

每条以 `— 类别：... — 状态：...` 收尾，便于索引过滤。

## 5 大分类

🤖 如何用AI ｜ 🌱 个人成长 ｜ 🧠 认知 ｜ 💼 职场 ｜ 📈 投资

## 一键初始化

```bash
python scripts/init_idea_space.py "<你的工作区绝对路径>"
```

会用 `assets/` 下的干净模板（**不含任何私人内容**）生成上述四个文件。

## 自动化（见 references/automations.md）

- **00:00 每日总结** — 向内归纳当天 + 回顾待解决清单
- **03:00 做梦** — 横向联想，跨分类连线，产出 1 条 ⚠️ 可证伪假设

两个自动化**只追加、永不改写**主文档原文。

## 目录结构

```
idea-space/
├── SKILL.md                      # 技能主文档（工作流说明）
├── README.md                     # 本文件
├── assets/                       # 干净模板（无私人数据）
│   ├── idea-space.template.md
│   ├── classification-index.template.md
│   ├── integrated.template.md
│   └── dream-notes.template.md
├── references/
│   └── automations.md            # 两个 automation_update 提示词
└── scripts/
    └── init_idea_space.py        # 脚手架脚本
```

## 隐私说明

本技能只提供**结构与工作流**，模板均为空壳。**切勿**把真实日记内容打包发布——发布前请确认 `想法空间.md` 等文件不在待发布范围内。

## 可靠写入与验证

需要 Python 3.10+。正文文件放在私人工作区；以下命令不会联网。

```bash
python scripts/idea_store.py "<workspace>" record --id entry-unique-id --category 认知 --title "标题" --body-file "<private-body-file>"
python scripts/idea_store.py "<workspace>" reindex
python scripts/idea_store.py "<workspace>" check
python verify_all.py
```

`--date YYYY-MM-DD` 可指定日期。自动整理对话须由当前用户按工作区启用，默认只记录明确要求保存的内容。
初始化前检查全部模板，已有文件不覆盖。归档去重与时区说明见 [自动化文档](references/automations.md)。
