"""Append-only journal operations with a rebuildable category index.

Only explicitly supplied workspace files are accessed. No network access.
"""
import argparse
import base64
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone, date
import json
import os
from pathlib import Path
import re
import tempfile
from zoneinfo import ZoneInfo

LOG = '想法空间.md'
INDEX = '想法空间·分类索引.md'
CATEGORIES = ('如何用AI', '个人成长', '认知', '职场', '投资')
START = '<!-- idea-space:index:start -->'
END = '<!-- idea-space:index:end -->'
ENTRY = re.compile(r'<!-- idea-space:entry:([A-Za-z0-9_=-]+) -->')


def atomic_text(path, text):
    fd, temp = tempfile.mkstemp(prefix='.' + path.name, suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


@contextmanager
def locked(workspace):
    path = workspace / '.idea-space.lock'
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError('工作区正在写入；若进程已退出，请确认后手动移除 .idea-space.lock')
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        path.unlink()


def target_date(kind, tz='Asia/Shanghai', now=None):
    zone = timezone(timedelta(hours=8)) if tz == 'Asia/Shanghai' else ZoneInfo(tz)
    current = (now or datetime.now(zone)).astimezone(zone)
    return (current.date() - timedelta(days=1 if kind == 'summary' else 0)).isoformat()


def entries(text):
    records = [json.loads(base64.urlsafe_b64decode(m)) for m in ENTRY.findall(text)]
    ids = [r['id'] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('日志存在重复稳定 ID')
    for record in records:
        if '<a id="idea-' + record['id'] + '"></a>' not in text:
            raise ValueError('日志缺少条目锚点')
    return records


def render_index(text):
    records = entries(text)
    lines = [START, '## 自动分类索引', '', '> 从带稳定 ID 的日志生成；上方既有人工索引保留。', '',
             '| 日期 | 条数 |', '|---|---|']
    counts = {}
    for r in records:
        counts[r['date']] = counts.get(r['date'], 0) + 1
    lines += [f'| {d} | {counts[d]} |' for d in sorted(counts)]
    for category in CATEGORIES:
        lines += ['', '### ' + category, '']
        for r in records:
            if r['category'] == category:
                title = r['title'].replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
                lines.append(f'- [{r["date"]} · {title}]({LOG}#idea-{r["id"]})')
    return '\n'.join(lines + ['', END])


def updated_index(workspace):
    text = (workspace / LOG).read_text(encoding='utf-8')
    path = workspace / INDEX
    old = path.read_text(encoding='utf-8') if path.exists() else '# 想法空间 · 分类索引\n'
    generated = render_index(text)
    if START in old or END in old:
        if old.count(START) != 1 or old.count(END) != 1 or old.index(START) > old.index(END):
            raise ValueError('索引生成区标记损坏，拒绝覆盖')
        return old[:old.index(START)] + generated + old[old.index(END) + len(END):]
    return old.rstrip() + '\n\n' + generated + '\n'


def rebuild(workspace):
    new = updated_index(workspace)
    path = workspace / INDEX
    if not path.exists() or path.read_text(encoding='utf-8') != new:
        atomic_text(path, new)


def append_entry(workspace, ident, day, category, title, body):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', ident):
        raise ValueError('ID 只能包含字母、数字、下划线与连字符，最多 80 字符')
    date.fromisoformat(day)
    if category not in CATEGORIES or not title.strip() or '\n' in title or '\r' in title:
        raise ValueError('类别或标题无效')
    if '<!-- idea-space:' in body or '<a id="idea-' in body:
        raise ValueError('正文不能包含系统保留标记')
    with locked(workspace):
        path = workspace / LOG
        text = path.read_text(encoding='utf-8')
        if any(r['id'] == ident for r in entries(text)):
            rebuild(workspace)  # Recover an interrupted index update without duplicating the log.
            return False
        updated_index(workspace)  # Preflight existing index markers before touching the log.
        record = {'id':ident, 'date':day, 'category':category, 'title':title}
        encoded = base64.urlsafe_b64encode(json.dumps(record, ensure_ascii=False).encode()).decode()
        block = f'\n<a id="idea-{ident}"></a>\n<!-- idea-space:entry:{encoded} -->\n- **{title}**：{body.strip()} — 类别：{category}\n'
        section = re.search(r'^### ' + re.escape(day) + r'[^\n]*\n', text, re.M)
        if section:
            following = re.search(r'^#{2,3} ', text[section.end():], re.M)
            pos = section.end() + following.start() if following else len(text)
        else:
            marker = '## 🔥 待解决想法清单'
            if marker not in text:
                raise ValueError('缺少每日记录结束标记，请先初始化或整理旧日志')
            pos = text.index(marker)
            block = '\n### ' + day + '\n' + block
        atomic_text(path, text[:pos] + block + '\n' + text[pos:])
        rebuild(workspace)
        return True


def append_archive(workspace, kind, day, body):
    date.fromisoformat(day)
    if kind not in ('summary', 'dream') or '<!-- idea-space:' in body:
        raise ValueError('归档类型或正文无效')
    path = workspace / (LOG if kind == 'summary' else '做梦笔记.md')
    marker = f'<!-- idea-space:archive:{kind}:{day} -->'
    with locked(workspace):
        text = path.read_text(encoding='utf-8')
        legacy = (r'^###\s+' + day + r'\s+总结\s*$' if kind == 'summary' else
                  r'^###\s+(?:🌙\s*)?' + day + r'\s*的梦\s*$')
        if marker in text or re.search(legacy, text, re.M):
            return False
        heading = day + ' 总结' if kind == 'summary' else '🌙 ' + day + ' 的梦'
        atomic_text(path, text.rstrip() + f'\n\n{marker}\n### {heading}\n\n{body.strip()}\n')
        return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workspace', type=Path)
    sub = parser.add_subparsers(dest='command', required=True)
    record = sub.add_parser('record')
    record.add_argument('--id', required=True, help='Stable caller-generated ID; reuse on retry')
    record.add_argument('--category', choices=CATEGORIES, required=True)
    record.add_argument('--title', required=True)
    for command in (record, sub.add_parser('archive')):
        command.add_argument('--date')
        command.add_argument('--timezone', default='Asia/Shanghai')
        command.add_argument('--body-file', type=Path, required=True)
        if command is not record:
            command.add_argument('--kind', choices=('summary', 'dream'), required=True)
    sub.add_parser('reindex')
    sub.add_parser('check')
    args = parser.parse_args()
    try:
        ws = args.workspace.resolve()
        if args.command == 'check':
            expected = updated_index(ws)
            if not (ws / INDEX).exists() or (ws / INDEX).read_text(encoding='utf-8') != expected:
                raise ValueError('分类索引需要重建：运行 reindex')
            print('索引与日志一致（旧格式条目保留，未自动迁移）')
        elif args.command == 'reindex':
            with locked(ws):
                rebuild(ws)
            print('索引已重建')
        else:
            body = args.body_file.read_text(encoding='utf-8')
            kind = getattr(args, 'kind', 'record')
            day = args.date or target_date(kind, args.timezone)
            changed = (append_entry(ws, args.id, day, args.category, args.title, body)
                       if args.command == 'record' else append_archive(ws, kind, day, body))
            print('已追加' if changed else '已存在，本次未重复追加')
        return 0
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
