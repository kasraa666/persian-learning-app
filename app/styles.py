# -*- coding: utf-8 -*-
"""
灵动科技风 全局样式
品牌: #165DFF / 渐变 #4080FF / 浅蓝底 #F0F5FF
"""
import os, sys, platform

# ═══════════════════════════════════════════════════════
#  数据目录
# ═══════════════════════════════════════════════════════

# 用户可写目录 — macOS 的 .app 是只读的，用户数据必须分开存
if platform.system() == 'Darwin':
    USER_DATA_DIR = os.path.join(
        os.path.expanduser('~'), 'Library', 'Application Support', 'PersianLearning'
    )
elif platform.system() == 'Windows':
    USER_DATA_DIR = os.path.join(
        os.environ.get('APPDATA', os.path.expanduser('~')), 'PersianLearning'
    )
else:
    USER_DATA_DIR = os.path.join(os.path.expanduser('~'), '.persian-learning')

os.makedirs(USER_DATA_DIR, exist_ok=True)

# 应用资源目录（只读）— 打包后从 PyInstaller 临时目录读取，开发模式从源码目录
if getattr(sys, 'frozen', False):
    ASSETS_DIR = os.path.join(sys._MEIPASS, 'data')
else:
    ASSETS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'
    )

# 兼容旧代码：DATA_DIR 指向用户数据目录（vocabulary.py, saved_tab.py 用）
DATA_DIR = USER_DATA_DIR

# 启动时把打包内的初始数据文件复制到用户目录（如果还不存在）
_INIT_FILES = ['bookmarks.json', 'vocabulary.json']
for _f in _INIT_FILES:
    _src = os.path.join(ASSETS_DIR, _f)
    _dst = os.path.join(USER_DATA_DIR, _f)
    if os.path.exists(_src) and not os.path.exists(_dst):
        try:
            import shutil
            shutil.copy2(_src, _dst)
        except Exception:
            pass

APP_STYLE = """
/* ═══════════════════════════════════════════
   全局 — macOS + Windows 兼容字体
   ═══════════════════════════════════════════ */
QMainWindow {
    background-color: #F0F5FF;
}
QWidget {
    font-family: "Geeza Pro", "Times New Roman", "Tahoma", "Arial", sans-serif;
    font-size: 14px;
    color: #1D2129;
}

/* ═══════════════════════════════════════════
   标签栏 — 极简线条指示
   ═══════════════════════════════════════════ */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: #86909C;
    padding: 14px 32px;
    margin: 0 4px;
    border: none;
    border-bottom: 3px solid transparent;
    font-size: 14px;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #165DFF;
    font-weight: 700;
    border-bottom: 3px solid #165DFF;
    background: transparent;
}
QTabBar::tab:hover:!selected {
    color: #4E5969;
    border-bottom: 3px solid #C9CDD4;
}

/* ═══════════════════════════════════════════
   按钮
   ═══════════════════════════════════════════ */
QPushButton {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #165DFF, stop:1 #4080FF);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 14px;
}
QPushButton:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #4080FF, stop:1 #5C9EFF);
}
QPushButton:pressed {
    background: #0E4AD5;
}

/* ═══════════════════════════════════════════
   输入框
   ═══════════════════════════════════════════ */
QLineEdit {
    background: #FFFFFF;
    color: #1D2129;
    border: 2px solid #E5E6EB;
    border-radius: 28px;
    padding: 10px 20px;
    font-size: 15px;
}
QLineEdit:focus {
    border-color: #165DFF;
}

/* ═══════════════════════════════════════════
   多行输入
   ═══════════════════════════════════════════ */
QPlainTextEdit, QTextEdit {
    background: #FFFFFF;
    color: #1D2129;
    border: 1px solid #E5E6EB;
    border-radius: 14px;
    padding: 14px 18px;
    font-size: 14px;
}

/* ═══════════════════════════════════════════
   列表 — 无边框卡片
   ═══════════════════════════════════════════ */
QListWidget, QTreeWidget, QTableWidget {
    background: #FFFFFF;
    color: #1D2129;
    border: none;
    border-radius: 16px;
    outline: none;
    padding: 6px;
}
QListWidget::item, QTreeWidget::item {
    padding: 12px 18px;
    border-radius: 10px;
    margin: 2px 6px;
}
QListWidget::item:hover, QTreeWidget::item:hover {
    background: #F0F5FF;
}
QListWidget::item:selected, QTreeWidget::item:selected {
    background: #E8F0FF;
    color: #165DFF;
}

/* ═══════════════════════════════════════════
   滚动条 — 极细
   ═══════════════════════════════════════════ */
QScrollBar:vertical {
    background: transparent;
    width: 5px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #C9CDD4;
    border-radius: 3px;
    min-height: 36px;
}
QScrollBar::handle:vertical:hover {
    background: #A8ADB4;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* ═══════════════════════════════════════════
   分组框
   ═══════════════════════════════════════════ */
QGroupBox {
    border: none;
    border-radius: 14px;
    margin-top: 20px;
    padding: 22px 18px 18px 18px;
    font-weight: 700;
    color: #1D2129;
    background: #FFFFFF;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 18px;
    padding: 0 8px;
    color: #165DFF;
    font-size: 14px;
    font-weight: 700;
}

/* ═══════════════════════════════════════════
   进度条
   ═══════════════════════════════════════════ */
QProgressBar {
    background: transparent;
    border: none;
    border-radius: 0;
    text-align: center;
    color: transparent;
    font-size: 0;
    height: 3px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #165DFF, stop:0.5 #4080FF, stop:1 #165DFF);
    border-radius: 2px;
}

/* ═══════════════════════════════════════════
   文本浏览器
   ═══════════════════════════════════════════ */
QTextBrowser {
    background: #FFFFFF;
    color: #1D2129;
    border: none;
    border-radius: 16px;
    padding: 16px;
}

/* ═══════════════════════════════════════════
   下拉框
   ═══════════════════════════════════════════ */
QComboBox {
    background: #F7F8FA;
    color: #1D2129;
    border: 1px solid #E5E6EB;
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 13px;
}
QComboBox:hover {
    border-color: #165DFF;
    background: #FFFFFF;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox QAbstractItemView {
    background: #FFFFFF;
    color: #1D2129;
    border: 1px solid #E5E6EB;
    border-radius: 10px;
    padding: 6px;
}
QComboBox QAbstractItemView::item:selected {
    background: #E8F0FF;
    color: #165DFF;
}

/* ═══════════════════════════════════════════
   分割线
   ═══════════════════════════════════════════ */
QSplitter::handle {
    background: transparent;
    width: 0;
}

/* ═══════════════════════════════════════════
   状态栏
   ═══════════════════════════════════════════ */
QStatusBar {
    background: transparent;
    color: #86909C;
    border: none;
    font-size: 12px;
    padding: 6px 24px;
}
"""
