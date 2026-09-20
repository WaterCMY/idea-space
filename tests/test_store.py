import importlib.util
import os
import subprocess
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import idea_store as store
import init_idea_space as init


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.ws=Path(self.temp.name)
        for src,dst in init.TARGETS.items():shutil.copy(ROOT/'assets'/src,self.ws/dst)
    def tearDown(self):self.temp.cleanup()
    def record(self):return store.append_entry(self.ws,'stable-1','2026-09-19','认知','虚构测试','这是合成测试记录。')
    def test_retry_keeps_one_entry_and_index_links(self):
        original=(self.ws/store.LOG).read_text(encoding='utf-8')
        self.assertTrue(self.record());self.assertFalse(self.record())
        text=(self.ws/store.LOG).read_text(encoding='utf-8')
        self.assertEqual(len(store.entries(text)),1)
        self.assertIn('还没找到想做的事',text)
        index=(self.ws/store.INDEX).read_text(encoding='utf-8')
        self.assertIn('#idea-stable-1',index)
        self.assertEqual(index,store.updated_index(self.ws))
    def test_interrupted_index_can_be_rebuilt_without_duplicate_log(self):
        with patch.object(store,'rebuild',side_effect=OSError('synthetic fault')):
            with self.assertRaises(OSError):self.record()
        self.assertFalse(self.record())
        self.assertEqual(len(store.entries((self.ws/store.LOG).read_text(encoding='utf-8'))),1)
        self.assertEqual((self.ws/store.INDEX).read_text(encoding='utf-8'),store.updated_index(self.ws))
    def test_summary_and_dream_are_idempotent(self):
        for kind in ['summary','dream']:
            self.assertTrue(store.append_archive(self.ws,kind,'2026-09-18','合成归档'))
            self.assertFalse(store.append_archive(self.ws,kind,'2026-09-18','合成归档'))
    def test_legacy_archive_is_not_duplicated(self):
        p=self.ws/store.LOG;p.write_text(p.read_text(encoding='utf-8')+'\n### 2026-09-18 总结\n旧归档\n',encoding='utf-8')
        self.assertFalse(store.append_archive(self.ws,'summary','2026-09-18','新归档'))
    def test_timezone_and_year_boundary(self):
        now=datetime(2026,12,31,16,0,tzinfo=timezone.utc)
        self.assertEqual(store.target_date('summary',now=now),'2026-12-31')
        self.assertEqual(store.target_date('dream',now=now),'2027-01-01')
    def test_lock_prevents_overlapping_writers(self):
        with store.locked(self.ws):
            with self.assertRaises(ValueError):self.record()
        self.assertFalse((self.ws/'.idea-space.lock').exists())
    def test_init_never_overwrites(self):
        path=self.ws/store.LOG;path.write_text('合成用户记录',encoding='utf-8')
        with patch.object(sys,'argv',['init',str(self.ws)]):self.assertEqual(init.main(),0)
        self.assertEqual(path.read_text(encoding='utf-8'),'合成用户记录')
    def test_init_with_legacy_console_encoding(self):
        with tempfile.TemporaryDirectory() as target:
            env=dict(os.environ,PYTHONIOENCODING='cp1252')
            command=[sys.executable,str(ROOT/'scripts/init_idea_space.py'),target]
            first=subprocess.run(command,env=env,capture_output=True)
            self.assertEqual(first.returncode,0,first.stderr.decode('ascii',errors='replace'))
            path=Path(target)/store.LOG
            path.write_text('Synthetic retained entry',encoding='utf-8')
            retry=subprocess.run(command,env=env,capture_output=True)
            self.assertEqual(retry.returncode,0,retry.stderr.decode('ascii',errors='replace'))
            self.assertEqual(path.read_text(encoding='utf-8'),'Synthetic retained entry')


if __name__=='__main__':unittest.main()
