# -*- coding: utf-8 -*-
"""本地收尾：清理缓存类目录与常见残留文件（不删除 scan_results 内本轮 JSON）。"""
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

if not cfg.get("auto_cleanup", True):
    print("[SKIP] config.auto_cleanup 为 false，跳过清理")
    raise SystemExit(0)

cache_dir = ROOT / Path(cfg["hexstrike_cache_dir"])

# 清空 cache 目录内容（保留目录本身）
if cache_dir.is_dir():
    for child in cache_dir.iterdir():
        try:
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)
        except OSError:
            pass
elif not cache_dir.exists():
    cache_dir.mkdir(parents=True, exist_ok=True)

# 删除工程根下 __pycache__（若存在为目录）
root_pycache = ROOT / "__pycache__"
if root_pycache.is_dir():
    shutil.rmtree(root_pycache, ignore_errors=True)

# 递归删除子目录中的 __pycache__（排除自带 python3 树）
for pyc in ROOT.rglob("__pycache__"):
    try:
        if "python3" in pyc.parts:
            continue
        shutil.rmtree(pyc, ignore_errors=True)
    except OSError:
        pass

print("[OK] 缓存目录已清空 + 本地环境清理完成")
