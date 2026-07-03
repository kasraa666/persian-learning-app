#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
波斯语新闻 — 灵动卡片
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QTextBrowser,
    QSplitter, QProgressBar, QFrame, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QSize
from PyQt6.QtGui import QDesktopServices, QColor

from app.fetcher import (
    fetch_radiofarda_news, fetch_bbc_persian, fetch_euronews_persian,
    fetch_khabaronline_news, fetch_article_content,
)

NEWS_SOURCES = {
    "radiofarda":{"name":"Radio Farda","subtitle":"Radio Farda · News & Analysis","icon":"📻","fetch":fetch_radiofarda_news},
    "bbc":{"name":"BBC Persian","subtitle":"BBC Persian · International","icon":"📡","fetch":fetch_bbc_persian},
    "euronews":{"name":"Euronews Persian","subtitle":"Euronews · European perspective","icon":"🌍","fetch":fetch_euronews_persian},
    "khabar":{"name":"Khabar Online","subtitle":"Khabar Online · Iran domestic","icon":"🇮🇷","fetch":fetch_khabaronline_news},
}

SRC_BTN = """
    QPushButton{background:#FFF;color:#1D2129;text-align:left;
        padding:14px 18px;font-size:13px;border-radius:14px;
        border:1px solid rgba(0,0,0,0.04);font-weight:500;}
    QPushButton:hover{background:#F0F5FF;border-color:#165DFF;color:#165DFF;}
"""

def _shadow(w,color=QColor(22,93,255,18)):
    s=QGraphicsDropShadowEffect(); s.setBlurRadius(24); s.setOffset(0,2); s.setColor(color)
    w.setGraphicsEffect(s)


class NewsListThread(QThread):
    result=pyqtSignal(list); progress=pyqtSignal(str); done=pyqtSignal()
    def __init__(self,k): super().__init__(); self.k=k
    def run(self):
        try:
            info=NEWS_SOURCES[self.k]; self.progress.emit(f"Fetching {info['name']} …")
            self.result.emit(info["fetch"]())
        except Exception as e:
            self.result.emit([{"title":str(e),"url":"","source":"error","type":"error"}])
        finally: self.done.emit()


class ArticleThread(QThread):
    content=pyqtSignal(str); done=pyqtSignal()
    def __init__(self,url): super().__init__(); self.url=url
    def run(self):
        try: self.content.emit(fetch_article_content(self.url))
        except Exception as e: self.content.emit(f"<p style='color:#F53F3F;'>Load failed: {e}</p>")
        finally: self.done.emit()


class NewsTab(QWidget):
    def __init__(self):
        super().__init__()
        root=QVBoxLayout(self); root.setContentsMargins(36,28,36,28); root.setSpacing(18)

        title=QLabel("Persian News  ·  اخبار فارسی")
        title.setStyleSheet("font-size:16px;font-weight:700;color:#1D2129;border:none;background:transparent;")
        root.addWidget(title)

        # 新闻源卡片
        sc=QFrame()
        sc.setStyleSheet("QFrame{background:#FFF;border-radius:20px;border:1px solid rgba(0,0,0,0.04);}")
        _shadow(sc)
        sl=QVBoxLayout(sc); sl.setContentsMargins(20,16,20,16); sl.setSpacing(8)
        sll=QLabel("Choose a news source"); sll.setStyleSheet("color:#86909C;font-size:11px;font-weight:600;border:none;background:transparent;")
        sl.addWidget(sll)
        sg=QHBoxLayout(); sg.setSpacing(10)
        for k,v in NEWS_SOURCES.items():
            b=QPushButton(f"{v['icon']} {v['name']}")
            b.setToolTip(v["subtitle"]); b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(SRC_BTN)
            b.clicked.connect(lambda _,kk=k:self._fetch(kk))
            sg.addWidget(b)
        sg.addStretch(); sl.addLayout(sg)
        root.addWidget(sc)

        self.pb=QProgressBar(); self.pb.setVisible(False); self.pb.setTextVisible(False); self.pb.setFixedHeight(3)
        self.st=QLabel("Click a news source")
        self.st.setStyleSheet("color:#86909C;font-size:13px;border:none;background:transparent;")
        root.addWidget(self.pb); root.addWidget(self.st)

        # 主分割
        main=QSplitter(Qt.Orientation.Horizontal); main.setHandleWidth(0)

        # 列表卡片
        lf=QFrame(); lf.setStyleSheet("QFrame{background:#FFF;border-radius:20px;}")
        _shadow(lf)
        lfl=QVBoxLayout(lf); lfl.setContentsMargins(6,6,6,6)
        self.nl=QListWidget(); self.nl.setWordWrap(True)
        self.nl.itemClicked.connect(self._view)
        self.nl.setStyleSheet(
            "QListWidget{background:#FFF;border:none;border-radius:18px;padding:6px;}"
            "QListWidget::item{padding:12px 18px;border-radius:12px;margin:2px 6px;}"
            "QListWidget::item:hover{background:#F0F5FF;}"
            "QListWidget::item:selected{background:#E8F0FF;color:#165DFF;}"
        )
        lfl.addWidget(self.nl); main.addWidget(lf)

        # 文章卡片
        af=QFrame(); af.setStyleSheet("QFrame{background:#FFF;border-radius:20px;}")
        _shadow(af)
        afl=QVBoxLayout(af); afl.setContentsMargins(4,4,4,4)
        self.av=QTextBrowser(); self.av.setOpenExternalLinks(True)
        self.av.setStyleSheet(
            "QTextBrowser{background:#FFF;border:none;border-radius:18px;padding:20px;font-size:15px;}"
        )
        self._empty_article(); afl.addWidget(self.av); main.addWidget(af)
        main.setStretchFactor(0,3); main.setStretchFactor(1,5)

        root.addWidget(main,1)

        # 工具栏
        bar=QHBoxLayout()
        self.ob=QPushButton("↗ Open in Browser"); self.ob.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ob.setStyleSheet(
            "QPushButton{background:#F2F3F5;color:#4E5969;border:none;border-radius:12px;"
            "padding:10px 22px;font-size:13px;font-weight:500;}"
            "QPushButton:hover{background:#E8F0FF;color:#165DFF;}")
        self.ob.clicked.connect(self._oc)
        sb=QPushButton("☆ Save"); sb.setCursor(Qt.CursorShape.PointingHandCursor)
        sb.setStyleSheet(
            "QPushButton{background:#F2F3F5;color:#4E5969;border:none;border-radius:12px;"
            "padding:10px 22px;font-size:13px;font-weight:500;}"
            "QPushButton:hover{background:#E8F0FF;color:#165DFF;}")
        sb.clicked.connect(self._save)
        bar.addWidget(self.ob); bar.addWidget(sb); bar.addStretch()
        root.addLayout(bar)

        self._cu=""; self._ct=""

    def _empty_article(self):
        self.av.setHtml(
            '<div style="text-align:center;padding:100px 20px;">'
            '<div style="font-size:48px;margin-bottom:12px;">📰</div>'
            '<div style="font-size:16px;color:#86909C;font-weight:600;">Select an article to read</div>'
            '<div style="font-size:13px;color:#C9CDD4;margin-top:8px;">Click any headline on the left</div></div>'
        )

    def _fetch(self,k):
        self.pb.setVisible(True); self.pb.setMaximum(0)
        self.st.setText(f"Fetching … {NEWS_SOURCES[k]['name']}")
        self.st.setStyleSheet("color:#86909C;font-size:13px;border:none;background:transparent;")
        self._t=NewsListThread(k)
        self._t.progress.connect(lambda m:self.st.setText(m))
        self._t.result.connect(self._sl); self._t.done.connect(self._fd)
        self._t.start()

    def _sl(self,items):
        self.nl.clear()
        for it in items:
            txt=f"{it['title']}\n  {it.get('source','')}"
            li=QListWidgetItem(txt); li.setData(Qt.ItemDataRole.UserRole,it)
            li.setSizeHint(QSize(0,54)); self.nl.addItem(li)
        self.st.setText(f"✓ {len(items)} articles · click to read")
        self.st.setStyleSheet("color:#165DFF;font-size:13px;border:none;background:transparent;")

    def _fd(self): self.pb.setMaximum(100); self.pb.setValue(100); self.pb.setVisible(False)

    def _view(self,item):
        d=item.data(Qt.ItemDataRole.UserRole)
        if not d: return
        self._ct=d.get("title",""); self._cu=d.get("url","")
        if d.get("type")=="link":
            self.av.setHtml(
                '<div style="text-align:center;padding:80px;">'
                f'<div style="font-size:18px;color:#165DFF;font-weight:700;">{self._ct}</div>'
                '<div style="color:#86909C;margin:16px 0;">VPN required for this site</div>'
                f'<a href="{self._cu}" style="color:#165DFF;">↗ Open in Browser</a></div>')
            return
        if not self._cu: return
        self.st.setText("Loading article …"); self.st.setStyleSheet("color:#86909C;font-size:13px;border:none;background:transparent;")
        self._at=ArticleThread(self._cu); self._at.content.connect(self._sa); self._at.start()

    def _sa(self,body):
        styled=(
            '<html><head><meta charset="utf-8"><style>'
            'body{background:#fff;color:#1D2129;font-size:15px;'
            'font-family:"Times New Roman",Tahoma,serif;padding:0;}'
            'a{color:#165DFF;text-decoration:none;}'
            'p{line-height:2.2;margin:10px 0;}'
            'h1,h2,h3,h4{color:#165DFF;}img{max-width:100%;border-radius:10px;}'
            '</style></head><body>'
            f'<h2 style="color:#165DFF;">{self._ct}</h2>{body}'
            '<hr style="border:0;border-top:1px solid #E5E6EB;margin:24px 0;">'
            f'<div style="text-align:center;"><a href="{self._cu}">↗ View original</a></div></body></html>'
        )
        self.av.setHtml(styled)

    def _oc(self):
        if self._cu: QDesktopServices.openUrl(QUrl(self._cu))

    def _save(self):
        if self._cu and self._ct:
            from app.saved_tab import add_bookmark
            add_bookmark(self._ct,self._cu,"News")
            self.st.setText("☆ Saved"); self.st.setStyleSheet("color:#165DFF;font-size:13px;border:none;background:transparent;")
