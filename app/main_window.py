#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主窗口 — 灵动科技风
阴影卡片 + 毛玻璃顶栏 + 平滑标签切换
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont

from app.styles import APP_STYLE
from app.dict_tab import DictTab
from app.resources_tab import ResourcesTab
from app.news_tab import NewsTab
from app.saved_tab import SavedTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("波斯语学习助手  |  دستیار یادگیری فارسی")
        self.resize(1180, 820)
        self.setMinimumSize(920, 640)
        self.setStyleSheet(APP_STYLE)

        # ── 中心容器 ──
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # ── 顶部毛玻璃栏 ──
        top_bar = QWidget()
        top_bar.setFixedHeight(52)
        top_bar.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,0.82);
                border-bottom: 0.5px solid rgba(0,0,0,0.06);
            }
        """)
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(28, 0, 28, 0)
        tb_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        brand = QLabel("دستیار فارسی  ·  波斯语学习助手")
        brand.setStyleSheet(
            "font-size:14px; font-weight:700; color:#1D2129; "
            "background:transparent; border:none;"
        )
        tb_layout.addWidget(brand)
        tb_layout.addStretch()

        center_layout.addWidget(top_bar)

        # ── 标签栏 ──
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setStyleSheet("""
            QTabBar {
                background: transparent;
                padding-left: 28px;
                padding-top: 6px;
            }
            QTabBar::tab {
                background: transparent;
                color: #86909C;
                padding: 13px 30px;
                margin: 0 3px;
                border: none;
                border-bottom: 3px solid transparent;
                font-size: 14px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                color: #165DFF;
                font-weight: 700;
                border-bottom: 3px solid #165DFF;
            }
            QTabBar::tab:hover:!selected {
                color: #4E5969;
                border-bottom: 3px solid #E5E6EB;
            }
        """)

        self.dict_tab = DictTab()
        self.resources_tab = ResourcesTab()
        self.news_tab = NewsTab()
        self.saved_tab = SavedTab()

        self.tabs.addTab(self.dict_tab, "📖  查词")
        self.tabs.addTab(self.resources_tab, "🎯  学习资源")
        self.tabs.addTab(self.news_tab, "📰  波斯语新闻")
        self.tabs.addTab(self.saved_tab, "⭐  我的收藏")

        center_layout.addWidget(self.tabs, 1)
        self.setCentralWidget(center)

        # ── 状态栏 ──
        self.status = QStatusBar()
        self.status.setStyleSheet(
            "QStatusBar { background:transparent; color:#86909C; "
            "border:none; font-size:12px; padding:4px 24px; }"
        )
        self.status_label = QLabel("آماده  |  就绪")
        self.status.addWidget(self.status_label)
        self.setStatusBar(self.status)
