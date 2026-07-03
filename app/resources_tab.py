#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
学习资源聚合 — 灵动卡片
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QProgressBar,
    QFrame, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QSize
from PyQt6.QtGui import QDesktopServices, QColor

from app.fetcher import (
    fetch_easy_persian_lessons, fetch_persian_language_online,
    fetch_bbc_persian, YOUTUBE_CHANNELS, PERSIAN_PODCASTS, PERSIAN_RESOURCES,
)

SOURCE_DEFS = {
    "bbc": {"name":"BBC Persian","icon":"📡","desc":"BBC Persian news, video, podcasts","fetch":fetch_bbc_persian},
    "youtube":{"name":"YouTube Channels","icon":"🎬","desc":"PersianPod101 · Chai and Conversation","fetch":lambda:YOUTUBE_CHANNELS},
    "podcasts":{"name":"Persian Podcasts","icon":"🎙️","desc":"ChannelB · Ravaaq · BPlus","fetch":lambda:PERSIAN_PODCASTS},
    "tools":{"name":"Tools & Resources","icon":"🛠️","desc":"Dictionaries · Poetry · Wikipedia","fetch":lambda:PERSIAN_RESOURCES},
    "easypersian":{"name":"Easy Persian","icon":"📚","desc":"150+ free lessons from alphabet to advanced","fetch":fetch_easy_persian_lessons},
    "plo":{"name":"Persian Language Online","icon":"🎓","desc":"Persian Language Foundation courses","fetch":fetch_persian_language_online},
}

SRC_BTN = """
    QPushButton { background:#FFF; color:#1D2129; text-align:left;
        padding:14px 18px; font-size:13px; border-radius:14px;
        border:1px solid rgba(0,0,0,0.04); font-weight:500; }
    QPushButton:hover { background:#F0F5FF; border-color:#165DFF; color:#165DFF; }
"""

def _shadow(w):
    s = QGraphicsDropShadowEffect()
    s.setBlurRadius(24); s.setOffset(0,2); s.setColor(QColor(22,93,255,18))
    w.setGraphicsEffect(s)


class FetchThread(QThread):
    result=pyqtSignal(list); progress=pyqtSignal(str); done=pyqtSignal()
    def __init__(self,k): super().__init__(); self.k=k
    def run(self):
        try:
            info=SOURCE_DEFS[self.k]; self.progress.emit(f"Fetching {info['name']} …")
            d=info["fetch"](); self.result.emit(d)
            self.progress.emit(f"{info['name']} · {len(d)} items")
        except Exception as e:
            self.result.emit([{"title":str(e),"url":"","source":"error","type":"error"}])
        finally: self.done.emit()


class ResourcesTab(QWidget):
    def __init__(self):
        super().__init__()
        root=QVBoxLayout(self); root.setContentsMargins(36,28,36,28); root.setSpacing(18)

        title=QLabel("Learning Resources  ·  منابع آموزشی")
        title.setStyleSheet("font-size:16px;font-weight:700;color:#1D2129;border:none;background:transparent;")
        root.addWidget(title)

        # 数据源卡片
        sc=QFrame()
        sc.setStyleSheet("QFrame{background:#FFF;border-radius:20px;border:1px solid rgba(0,0,0,0.04);}")
        _shadow(sc)
        sl=QVBoxLayout(sc); sl.setContentsMargins(20,16,20,16); sl.setSpacing(8)
        sll=QLabel("Choose a source"); sll.setStyleSheet("color:#86909C;font-size:11px;font-weight:600;border:none;background:transparent;")
        sl.addWidget(sll)
        sg=QHBoxLayout(); sg.setSpacing(10)
        for k,v in SOURCE_DEFS.items():
            b=QPushButton(f"{v['icon']} {v['name']}")
            b.setToolTip(v["desc"]); b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(SRC_BTN)
            b.clicked.connect(lambda _,kk=k: self._fetch(kk))
            sg.addWidget(b)
        sg.addStretch(); sl.addLayout(sg)
        root.addWidget(sc)

        self.pb=QProgressBar(); self.pb.setVisible(False); self.pb.setTextVisible(False); self.pb.setFixedHeight(3)
        self.st=QLabel("Click a source button above")
        self.st.setStyleSheet("color:#86909C;font-size:13px;border:none;background:transparent;")
        root.addWidget(self.pb); root.addWidget(self.st)

        # 结果列表卡片
        lf=QFrame(); lf.setStyleSheet("QFrame{background:#FFF;border-radius:20px;}")
        _shadow(lf)
        lfl=QVBoxLayout(lf); lfl.setContentsMargins(6,6,6,6)
        self.rl=QListWidget(); self.rl.setWordWrap(True)
        self.rl.itemDoubleClicked.connect(self._open)
        self.rl.setStyleSheet(
            "QListWidget{background:#FFF;border:none;border-radius:18px;padding:6px;}"
            "QListWidget::item{padding:12px 18px;border-radius:12px;margin:2px 6px;}"
            "QListWidget::item:hover{background:#F0F5FF;}"
            "QListWidget::item:selected{background:#E8F0FF;color:#165DFF;}"
        )
        lfl.addWidget(self.rl); root.addWidget(lf,1)

        # 底部按钮
        bar=QHBoxLayout()
        self.op=QPushButton("↗ Open in Browser")
        self.op.setEnabled(False); self.op.setCursor(Qt.CursorShape.PointingHandCursor)
        self.op.setStyleSheet(
            "QPushButton{background:#F2F3F5;color:#4E5969;border:none;border-radius:12px;"
            "padding:10px 22px;font-size:13px;font-weight:500;}"
            "QPushButton:hover{background:#E8F0FF;color:#165DFF;}")
        self.op.clicked.connect(self._os)
        clr=QPushButton("Clear"); clr.setCursor(Qt.CursorShape.PointingHandCursor)
        clr.setStyleSheet(
            "QPushButton{background:#F2F3F5;color:#86909C;border:none;border-radius:12px;"
            "padding:10px 22px;font-size:13px;}"
            "QPushButton:hover{color:#F53F3F;}")
        clr.clicked.connect(lambda:self.rl.clear())
        bar.addWidget(self.op); bar.addWidget(clr); bar.addStretch()
        root.addLayout(bar)

    def _fetch(self,k):
        self.pb.setVisible(True); self.pb.setMaximum(0)
        self.st.setText(f"Fetching … {SOURCE_DEFS[k]['name']}")
        self.st.setStyleSheet("color:#86909C;font-size:13px;border:none;background:transparent;")
        self._t=FetchThread(k)
        self._t.progress.connect(lambda m:self.st.setText(m))
        self._t.result.connect(self._show); self._t.done.connect(self._fd)
        self._t.start()

    def _show(self,items):
        self.rl.clear()
        icons={"news":"📰","video":"🎬","audio":"🎧","tutorial":"📖","search":"🔍",
               "tool":"🛠️","literature":"📜","encyclopedia":"📚","home":"🏠",
               "section":"📂","article":"📄","link":"🔗"}
        for it in items:
            ic=icons.get(it.get("type",""),"📌")
            txt=f"{ic}  {it['title']}\n     {it.get('source','')} — {it.get('desc','')}"
            li=QListWidgetItem(txt); li.setData(Qt.ItemDataRole.UserRole,it.get("url",""))
            li.setSizeHint(QSize(0,54)); self.rl.addItem(li)
        self.st.setText(f"✓ {len(items)} items"); self.st.setStyleSheet("color:#165DFF;font-size:13px;border:none;background:transparent;")
        self.op.setEnabled(bool(items))

    def _fd(self): self.pb.setMaximum(100); self.pb.setValue(100); self.pb.setVisible(False)

    def _os(self):
        it=self.rl.currentItem()
        if it: u=it.data(Qt.ItemDataRole.UserRole)
        if u: QDesktopServices.openUrl(QUrl(u))

    def _open(self,it):
        u=it.data(Qt.ItemDataRole.UserRole)
        if u: QDesktopServices.openUrl(QUrl(u))
