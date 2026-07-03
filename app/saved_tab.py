#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
收藏模块 — 灵动卡片
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QMessageBox,
    QApplication, QFrame, QGraphicsDropShadowEffect, QTabWidget,
)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QDesktopServices, QColor

import json, os
from datetime import datetime
from app.styles import DATA_DIR
from app.vocabulary import load_vocab, save_vocab, remove_vocab

BOOKMARKS_FILE = os.path.join(DATA_DIR,"bookmarks.json")

def _shadow(w):
    s=QGraphicsDropShadowEffect(); s.setBlurRadius(20); s.setOffset(0,2)
    s.setColor(QColor(22,93,255,14)); w.setGraphicsEffect(s)


# ═══════ 收藏夹 ═══════
def load_bookmarks():
    if not os.path.exists(BOOKMARKS_FILE): return []
    try:
        with open(BOOKMARKS_FILE,"r",encoding="utf-8") as f: return json.load(f)
    except: return []

def save_bookmarks(bm):
    with open(BOOKMARKS_FILE,"w",encoding="utf-8") as f: json.dump(bm,f,ensure_ascii=False,indent=2)

def add_bookmark(title,url,cat=""):
    bm=load_bookmarks()
    for b in bm:
        if b.get("url")==url: return
    bm.append({"title":title,"url":url,"category":cat,"added":datetime.now().strftime("%Y-%m-%d %H:%M")})
    save_bookmarks(bm)


class BookmarkPanel(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(self); l.setContentsMargins(0,12,0,0); l.setSpacing(10)
        bar=QHBoxLayout()
        ob=QPushButton("↗ Open"); ob.setCursor(Qt.CursorShape.PointingHandCursor)
        ob.setStyleSheet("QPushButton{background:#F2F3F5;color:#4E5969;border:none;border-radius:12px;padding:10px 22px;font-size:13px;font-weight:500;}QPushButton:hover{background:#E8F0FF;color:#165DFF;}")
        ob.clicked.connect(self._open)
        db=QPushButton("Delete"); db.setCursor(Qt.CursorShape.PointingHandCursor)
        db.setStyleSheet("QPushButton{background:#FFF1F0;color:#F53F3F;border:none;border-radius:12px;padding:10px 22px;font-size:13px;font-weight:500;}QPushButton:hover{background:#FFECE8;}")
        db.clicked.connect(self._del)
        bar.addWidget(ob); bar.addWidget(db); bar.addStretch(); l.addLayout(bar)
        self.lw=QListWidget(); self.lw.setWordWrap(True)
        self.lw.setStyleSheet(
            "QListWidget{background:#FFF;border:none;border-radius:18px;padding:6px;}"
            "QListWidget::item{padding:10px 18px;border-radius:12px;margin:2px 6px;}"
            "QListWidget::item:hover{background:#F0F5FF;}")
        self.lw.itemDoubleClicked.connect(self._open); l.addWidget(self.lw,1)
        self._refresh()

    def _refresh(self):
        self.lw.clear(); items=load_bookmarks()
        if not items: self.lw.addItem(QListWidgetItem("No bookmarks yet")); return
        items.sort(key=lambda x:x.get("added",""),reverse=True)
        for b in items:
            txt=f"📌 {b.get('title','')} [{b.get('category','')}]\n     {b.get('url','')} · {b.get('added','')}"
            li=QListWidgetItem(txt); li.setData(Qt.ItemDataRole.UserRole,b)
            li.setSizeHint(QSize(0,50)); self.lw.addItem(li)

    def _open(self):
        it=self.lw.currentItem()
        if it and it.data(Qt.ItemDataRole.UserRole):
            u=it.data(Qt.ItemDataRole.UserRole).get("url","")
            if u: QDesktopServices.openUrl(QUrl(u))

    def _del(self):
        it=self.lw.currentItem()
        if not it or not it.data(Qt.ItemDataRole.UserRole): return
        d=it.data(Qt.ItemDataRole.UserRole)
        r=QMessageBox.question(self,"Confirm",f"Delete «{d.get('title','')}»?")
        if r==QMessageBox.StandardButton.Yes:
            bm=load_bookmarks(); bm=[b for b in bm if b.get("url")!=d.get("url","")]
            save_bookmarks(bm); self._refresh()


# ═══════ 生词本 ═══════
class VocabPanel(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(self); l.setContentsMargins(0,12,0,0); l.setSpacing(10)
        bar=QHBoxLayout()
        db=QPushButton("Delete"); db.setCursor(Qt.CursorShape.PointingHandCursor)
        db.setStyleSheet("QPushButton{background:#FFF1F0;color:#F53F3F;border:none;border-radius:12px;padding:10px 22px;font-size:13px;font-weight:500;}QPushButton:hover{background:#FFECE8;}")
        db.clicked.connect(self._del)
        self.cnt=QLabel(""); self.cnt.setStyleSheet("color:#86909C;font-size:13px;border:none;background:transparent;")
        bar.addWidget(db); bar.addStretch(); bar.addWidget(self.cnt); l.addLayout(bar)
        self.lw=QListWidget(); self.lw.setWordWrap(True)
        self.lw.setStyleSheet(
            "QListWidget{background:#FFF;border:none;border-radius:18px;padding:6px;}"
            "QListWidget::item{padding:10px 18px;border-radius:12px;margin:2px 6px;}"
            "QListWidget::item:hover{background:#F0F5FF;}")
        l.addWidget(self.lw,1); self._refresh()

    def _refresh(self):
        self.lw.clear(); items=load_vocab()
        if not items: self.lw.addItem(QListWidgetItem("No saved words · click «+ Save Word» in search")); self.cnt.setText(""); return
        items.sort(key=lambda x:x.get("added",""),reverse=True)
        for v in items:
            w=v.get("word",""); s=v.get("source_dict",""); a=v.get("added","")
            txt=f"📝 {w}"
            if s: txt+=f"  [{s}]"
            txt+=f"\n     {a}"
            li=QListWidgetItem(txt); li.setData(Qt.ItemDataRole.UserRole,v)
            li.setSizeHint(QSize(0,46)); self.lw.addItem(li)
        self.cnt.setText(f"{len(items)} words")

    def _del(self):
        it=self.lw.currentItem()
        if not it or not it.data(Qt.ItemDataRole.UserRole): return
        d=it.data(Qt.ItemDataRole.UserRole)
        r=QMessageBox.question(self,"Confirm",f"Delete «{d.get('word','')}»?")
        if r==QMessageBox.StandardButton.Yes: remove_vocab(d.get("word","")); self._refresh()


# ═══════ 统筹面板 ═══════
class SavedTab(QWidget):
    def __init__(self):
        super().__init__()
        root=QVBoxLayout(self); root.setContentsMargins(36,28,36,28); root.setSpacing(16)
        title=QLabel("My Library  ·  ذخیره‌های من")
        title.setStyleSheet("font-size:16px;font-weight:700;color:#1D2129;border:none;background:transparent;")
        root.addWidget(title)

        # 子标签卡片
        cf=QFrame()
        cf.setStyleSheet("QFrame{background:#FFF;border-radius:20px;border:1px solid rgba(0,0,0,0.04);}")
        _shadow(cf)
        cll=QVBoxLayout(cf); cll.setContentsMargins(8,8,8,8)

        self.sub=QTabWidget(); self.sub.setDocumentMode(True)
        self.sub.tabBar().setStyleSheet("""
            QTabBar{background:transparent;padding-left:8px;}
            QTabBar::tab{background:transparent;color:#86909C;padding:12px 28px;
                border:none;border-bottom:3px solid transparent;font-size:13px;font-weight:500;}
            QTabBar::tab:selected{color:#165DFF;font-weight:700;border-bottom:3px solid #165DFF;}
            QTabBar::tab:hover:!selected{color:#4E5969;border-bottom:3px solid #C9CDD4;}
        """)
        self.vp=VocabPanel(); self.bp=BookmarkPanel()
        self.sub.addTab(self.vp,"📝 Vocabulary")
        self.sub.addTab(self.bp,"📌 Bookmarks")
        self.sub.currentChanged.connect(lambda i: [self.vp._refresh() if i==0 else self.bp._refresh()])
        cll.addWidget(self.sub)
        root.addWidget(cf,1)
