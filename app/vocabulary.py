#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生词本模块 — 独立管理词汇，与查词功能联动
存储格式: data/vocabulary.json
每个词条: {word, meaning, source_dict, url, added}
"""
import json, os
from datetime import datetime
from app.styles import DATA_DIR

VOCAB_FILE = os.path.join(DATA_DIR, "vocabulary.json")


def load_vocab():
    if not os.path.exists(VOCAB_FILE):
        return []
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_vocab(items):
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def add_vocab(word, meaning="", source_dict="", url=""):
    """添加一个生词，自动去重"""
    items = load_vocab()
    for it in items:
        if it.get("word") == word:
            return False  # 已存在
    items.append({
        "word": word,
        "meaning": meaning,
        "source_dict": source_dict,
        "url": url,
        "added": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_vocab(items)
    return True


def remove_vocab(word):
    """删除一个生词"""
    items = load_vocab()
    items = [it for it in items if it.get("word") != word]
    save_vocab(items)


def update_vocab_meaning(word, meaning):
    """更新一个生词的释义"""
    items = load_vocab()
    for it in items:
        if it.get("word") == word:
            it["meaning"] = meaning
            break
    save_vocab(items)


def vocab_exists(word):
    """检查单词是否已在生词本中"""
    items = load_vocab()
    for it in items:
        if it.get("word") == word:
            return True
    return False
