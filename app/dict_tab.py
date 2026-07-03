#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查词模块 — 灵动科技风
阴影卡片 + 动画反馈 + 胶囊快捷词 + 生词预览条
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QComboBox, QTextBrowser, QLabel, QSplitter, QFrame, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QSequentialAnimationGroup, QSize, QPoint,
)
from PyQt6.QtGui import QColor, QFont

from app.fetcher import search_vajehyab, search_abadis, search_amid
from app.vocabulary import add_vocab, vocab_exists, load_vocab, remove_vocab


# ═══════════════════════════════════════════════════════
#  搜索线程
# ═══════════════════════════════════════════════════════
class DictSearchThread(QThread):
    result = pyqtSignal(str, str, str)
    word_info = pyqtSignal(str, str, str)
    error = pyqtSignal(str)

    def __init__(self, word, source):
        super().__init__()
        self.word = word.strip()
        self.source = source

    def run(self):
        try:
            if self.source == "vajehyab":
                html, url = search_vajehyab(self.word)
                src = "VajehYab"
            elif self.source == "abadis":
                html, url = search_abadis(self.word)
                src = "Abadis"
            else:
                html, url = search_amid(self.word)
                src = "Amid"
            self.result.emit(self._wrap(html, url, src), src, self.word)
            self.word_info.emit(self.word, url, src)
        except Exception as e:
            self.error.emit(str(e))

    def _wrap(self, body, url, src):
        descs = {
            "VajehYab": "دهخدا · معین · عمید  —  Persian detailed dictionary",
            "Abadis": "English ↔ Persian  ·  دیکشنری انگلیسی به فارسی",
            "Amid": "فرهنگ عمید  —  Classic definition dictionary",
        }
        names = {"VajehYab": "VajehYab  واژه‌یاب", "Abadis": "Abadis  آبادیس", "Amid": "Amid  عمید"}
        return (
            '<div style="margin:0 0 20px 0;">'
            f'<div style="font-size:18px;font-weight:700;color:#165DFF;margin:0 0 4px 0;">'
            f'{names.get(src,src)}</div>'
            f'<div style="font-size:11px;color:#86909C;margin:0 0 14px 0;letter-spacing:0.3px;">'
            f'{descs.get(src,"")}</div>'
            f'<div style="font-family:\"Times New Roman\",Tahoma,serif;">{body}</div>'
            f'<div style="margin-top:18px;">'
            f'<a href="{url}" style="color:#165DFF;text-decoration:none;font-size:12px;'
            f'font-weight:500;">↗ View full result on web</a></div></div>'
        )


# ═══════════════════════════════════════════════════════
#  阴影卡片框
# ═══════════════════════════════════════════════════════
def add_shadow(w, radius=20, offset=2, color=QColor(0,0,0,25)):
    s = QGraphicsDropShadowEffect()
    s.setBlurRadius(radius)
    s.setOffset(0, offset)
    s.setColor(color)
    w.setGraphicsEffect(s)


# ═══════════════════════════════════════════════════════
#  胶囊按钮
# ═══════════════════════════════════════════════════════
class PillButton(QPushButton):
    def __init__(self, text, tip=""):
        super().__init__(text)
        if tip:
            self.setToolTip(tip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hover = False
        self.setStyleSheet(self._css())

    def _css(self):
        bg = "#F2F3F5" if not self._hover else "#E8F0FF"
        clr = "#4E5969" if not self._hover else "#165DFF"
        return (
            f"QPushButton {{ background:{bg}; color:{clr}; border:none; "
            f"border-radius:20px; padding:7px 18px; font-size:13px; font-weight:500; }}"
        )

    def enterEvent(self, e):
        self._hover = True
        self.setStyleSheet(self._css())
        self._anim_scale(1.04)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self.setStyleSheet(self._css())
        self._anim_scale(1.0)
        super().leaveEvent(e)

    def _anim_scale(self, target):
        a = QPropertyAnimation(self, b"geometry")
        a.setDuration(180)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        r = self.geometry()
        dw = int(r.width() * (target - 1) / 2)
        dh = int(r.height() * (target - 1) / 2)
        a.setEndValue(r.adjusted(-dw, -dh, dw, dh))
        a.start()


# ═══════════════════════════════════════════════════════
#  查询标签页
# ═══════════════════════════════════════════════════════
class DictTab(QWidget):
    def __init__(self):
        super().__init__()
        self._word = ""
        self._url = ""
        self._src = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 36)
        root.setSpacing(20)

        # ── 搜索卡片 ──
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background:#FFFFFF; border-radius:20px; border:1px solid rgba(0,0,0,0.04); }"
        )
        add_shadow(card, 30, 3, QColor(22,93,255,30))

        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 22, 28, 22)
        cl.setSpacing(14)

        # 标题行
        title = QLabel("Search Dictionary  ·  جستجوی واژه")
        title.setStyleSheet("font-size:16px;font-weight:700;color:#1D2129;background:transparent;border:none;")
        cl.addWidget(title)

        # 搜索行
        sr = QHBoxLayout()
        sr.setSpacing(12)

        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Type Persian or English word …")
        self.word_input.setFixedHeight(50)
        self.word_input.setStyleSheet(
            "QLineEdit { background:#F7F8FA; color:#1D2129; border:2px solid #E5E6EB; "
            "border-radius:28px; padding:0 22px; font-size:15px; }"
            "QLineEdit:focus { border-color:#165DFF; background:#FFFFFF; }"
        )
        self.word_input.returnPressed.connect(self._search)

        self.source_combo = QComboBox()
        self.source_combo.addItems(["VajehYab  واژه‌یاب", "Abadis  آبادیس", "Amid  عمید"])
        self.source_combo.setFixedHeight(50)
        self.source_combo.setMinimumWidth(170)
        self.source_combo.setStyleSheet(
            "QComboBox { background:#F7F8FA; color:#1D2129; border:1px solid #E5E6EB; "
            "border-radius:14px; padding:0 16px; font-size:13px; }"
            "QComboBox:hover { border-color:#165DFF; background:#FFF; }"
            "QComboBox::drop-down { border:none; width:24px; }"
            "QComboBox QAbstractItemView { background:#FFF; border:1px solid #E5E6EB; "
            "border-radius:12px; padding:6px; }"
            "QComboBox QAbstractItemView::item:selected { background:#E8F0FF; color:#165DFF; }"
        )

        self.search_btn = QPushButton("Search")
        self.search_btn.setFixedSize(100, 50)
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.setStyleSheet(
            "QPushButton { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 #165DFF,stop:1 #4080FF); color:#FFF; border:none; "
            "border-radius:28px; font-size:14px; font-weight:700; }"
            "QPushButton:hover { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 #4080FF,stop:1 #5C9EFF); }"
            "QPushButton:pressed { background:#0E4AD5; }"
        )
        self.search_btn.clicked.connect(self._search)

        self.vocab_btn = QPushButton("+ Save Word")
        self.vocab_btn.setFixedHeight(50)
        self.vocab_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.vocab_btn.setEnabled(False)
        self.vocab_btn.setStyleSheet(
            "QPushButton { background:#F2F3F5; color:#4E5969; border:none; "
            "border-radius:14px; padding:0 20px; font-size:13px; font-weight:500; }"
            "QPushButton:hover { background:#E8F0FF; color:#165DFF; }"
        )
        self.vocab_btn.clicked.connect(self._toggle)

        sr.addWidget(self.word_input, 4)
        sr.addWidget(self.source_combo)
        sr.addWidget(self.search_btn)
        sr.addWidget(self.vocab_btn)
        cl.addLayout(sr)

        # 快捷词 — 胶囊
        qr = QHBoxLayout()
        qr.setSpacing(8)
        for w, cn in [
            ("سلام","Hello"),("کتاب","Book"),("دانشگاه","University"),
            ("آب","Water"),("دوست","Friend"),("بزرگ","Big"),
            ("زبان","Language"),("آزادی","Freedom"),
        ]:
            pb = PillButton(w, cn)
            pb.clicked.connect(lambda _, ww=w: self._quick(ww))
            qr.addWidget(pb)
        qr.addStretch()
        cl.addLayout(qr)

        # 状态
        self.status_label = QLabel("Type a word, choose a dictionary, press Enter")
        self.status_label.setStyleSheet("color:#86909C;font-size:12px;border:none;background:transparent;")
        cl.addWidget(self.status_label)

        root.addWidget(card)

        # ── 结果区 ──
        spl = QSplitter(Qt.Orientation.Vertical)
        spl.setHandleWidth(0)

        # 结果浏览器
        result_frame = QFrame()
        result_frame.setStyleSheet("QFrame { background:#FFFFFF; border-radius:20px; }")
        add_shadow(result_frame, 24, 2, QColor(22,93,255,18))
        rl = QVBoxLayout(result_frame)
        rl.setContentsMargins(4, 4, 4, 4)
        self.result_view = QTextBrowser()
        self.result_view.setOpenExternalLinks(True)
        self.result_view.setStyleSheet(
            "QTextBrowser { background:#FFFFFF; border:none; border-radius:18px; "
            "padding:20px; font-size:15px; }"
        )
        self._show_empty_state()
        rl.addWidget(self.result_view)
        spl.addWidget(result_frame)

        # 生词预览
        vpw = QWidget()
        vpl = QVBoxLayout(vpw)
        vpl.setContentsMargins(0, 8, 0, 0)
        vl = QLabel("Today's Words  ·  واژگان امروز")
        vl.setStyleSheet("color:#4E5969;font-size:11px;font-weight:600;border:none;background:transparent;")
        vpl.addWidget(vl)
        self.vocab_preview = QTextBrowser()
        self.vocab_preview.setFixedHeight(96)
        self.vocab_preview.setStyleSheet(
            "QTextBrowser { background:#FFFFFF; border:1px solid rgba(0,0,0,0.04); "
            "border-radius:14px; padding:8px 14px; }"
        )
        vpl.addWidget(self.vocab_preview)
        spl.addWidget(vpw)
        spl.setStretchFactor(0, 4)
        spl.setStretchFactor(1, 1)

        root.addWidget(spl, 1)
        self._refresh_vocab_preview()

    # ── 空状态 ──
    def _show_empty_state(self):
        self.result_view.setHtml(
            '<div style="text-align:center;padding:80px 20px;">'
            '<div style="font-size:56px;margin-bottom:16px;filter:grayscale(0.3);">📖</div>'
            '<div style="font-size:16px;color:#86909C;font-weight:600;">Search Persian Words</div>'
            '<div style="font-size:13px;color:#C9CDD4;margin-top:8px;">'
            'VajehYab · Abadis · Amid  —  Three dictionaries combined</div></div>'
        )

    # ── 搜索 ──
    def _search(self):
        w = self.word_input.text().strip()
        if not w:
            return
        self._word = w
        m = {0:"vajehyab",1:"abadis",2:"amid"}
        self._src = m[self.source_combo.currentIndex()]
        self._set_status("Searching …", "#86909C")
        self.search_btn.setEnabled(False)
        self.vocab_btn.setEnabled(False)
        self._t = DictSearchThread(w, self._src)
        self._t.result.connect(self._on_ok)
        self._t.error.connect(self._on_err)
        self._t.word_info.connect(self._on_info)
        self._t.finished.connect(lambda: self.search_btn.setEnabled(True))
        self._t.start()

    def _quick(self, w):
        self.word_input.setText(w)
        self._search()

    def _on_ok(self, html, src, word):
        self._set_status("", "")
        styled = (
            '<html><head><meta charset="utf-8"><style>'
            'body{background:#fff;color:#1D2129;font-size:15px;'
            'font-family:"Times New Roman",Tahoma,serif;padding:0;}'
            'a{color:#165DFF;text-decoration:none;}'
            '</style></head><body>'+html+'</body></html>'
        )
        self.result_view.setHtml(styled)

    def _on_err(self, msg):
        self._set_status("Error: "+msg, "#F53F3F")
        self.vocab_btn.setEnabled(False)

    def _on_info(self, word, url, src):
        self._word = word
        self._url = url
        self._src = src
        self._update_vocab_btn()

    # ── 生词 ──
    def _update_vocab_btn(self):
        if vocab_exists(self._word):
            self.vocab_btn.setText("✓ Saved")
            self.vocab_btn.setStyleSheet(
                "QPushButton { background:#E8FFEA; color:#00B42A; border:none; "
                "border-radius:14px; padding:0 20px; font-size:13px; font-weight:600; }")
        else:
            self.vocab_btn.setText("+ Save Word")
            self.vocab_btn.setStyleSheet(
                "QPushButton { background:#F2F3F5; color:#4E5969; border:none; "
                "border-radius:14px; padding:0 20px; font-size:13px; font-weight:500; }"
                "QPushButton:hover { background:#E8F0FF; color:#165DFF; }")
        self.vocab_btn.setEnabled(True)

    def _toggle(self):
        w = self._word
        if not w:
            return
        if vocab_exists(w):
            remove_vocab(w)
            self._set_status("Removed from vocabulary", "#F53F3F")
        else:
            add_vocab(w, "", self._src, self._url)
            self._set_status(f"Saved — {w}", "#165DFF")
        self._update_vocab_btn()
        self._refresh_vocab_preview()

    def _refresh_vocab_preview(self):
        import datetime
        items = load_vocab()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        recent = [i for i in items if i.get("added","").startswith(today)][:5] or items[-5:]
        if not recent:
            self.vocab_preview.setHtml(
                '<div style="text-align:center;padding:16px;color:#C9CDD4;font-size:12px;">'
                'No saved words yet — click "+ Save Word" to start</div>')
        else:
            tags = []
            for i in recent:
                tags.append(
                    f'<span style="display:inline-block;background:#F0F5FF;color:#165DFF;'
                    f'padding:5px 14px;margin:4px;border-radius:20px;font-size:14px;'
                    f'font-family:"Times New Roman",Tahoma,serif;">{i.get("word","")}</span>')
            note = ""
            if len(items) > 5:
                note = f'<div style="color:#C9CDD4;font-size:10px;margin-top:6px;">{len(items)} total · see Saved tab</div>'
            self.vocab_preview.setHtml(
                '<div style="direction:rtl;padding:2px;">'+''.join(tags)+note+'</div>')

    def _set_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"color:{color or '#86909C'};font-size:12px;border:none;background:transparent;")
