# 自动化归档

以下是供用户显式启用自动化时使用的任务说明，安装 Skill 不会自动创建定时任务。
工作区路径和 Skill 安装目录由当前环境配置；默认时区 Asia/Shanghai。

## 每日 00:00 总结

读取用户指定工作区的昨日记录和待解决清单，归纳不超过 250 字的总结。
以运行时区的昨日为目标日期；补跑历史任务必须显式传 `--date YYYY-MM-DD`。
将总结写入工作区内的私人临时正文文件，再执行：

```bash
python <skill>/scripts/idea_store.py "<workspace>" archive --kind summary --timezone Asia/Shanghai --body-file "<private-body-file>"
```

工具按日期和类型去重；已有归档时报告“已存在”，不要绕过脚本再手工追加。
无新增记录时写明当天无记录。绝不改写原文或删除待解决事项。

## 每日 03:00 做梦

读取用户指定工作区的日志与分类索引（整合版存在时可读取）。选取 3–6 个跨类别条目，
给出一条主线、跨域联系和一条明确标注“⚠️假设”的可证伪观点；保留来源条目的链接。
将正文写入工作区内的私人临时文件，再执行：

```bash
python <skill>/scripts/idea_store.py "<workspace>" archive --kind dream --timezone Asia/Shanghai --body-file "<private-body-file>"
```

同一天重试不重复追加。补跑时显式传 `--date`。记录假设，不将生成内容改写为用户原话。

## 恢复与校验

```bash
python <skill>/scripts/idea_store.py "<workspace>" reindex
python <skill>/scripts/idea_store.py "<workspace>" check
```

日志与索引不是跨文件事务：日志成功而索引失败时，重建索引即可恢复。
存在 `.idea-space.lock` 时停止写入；只有确认没有写入进程后，用户才可移除遗留锁。
其他时区使用 IANA 名称；系统缺时区数据库时需安装 `tzdata`，默认上海时区无需额外依赖。
