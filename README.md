# 波斯语学习助手 | دستیار یادگیری فارسی

A desktop app for learning Persian (Farsi) — dictionary lookup, news reading, learning resources, and vocabulary management.

---

## ✨ Features

- **📖 Dictionary** — Search Persian words across VajehYab, Abadis, and Amid dictionaries
- **📰 Persian News** — Browse articles from Radio Farda, BBC Persian, Euronews, Khabar Online
- **🎯 Learning Resources** — Curated links to YouTube channels, podcasts, courses, and tools
- **⭐ My Library** — Save vocabulary words and bookmarks for later review

---

## 📦 Download

| Platform | Download |
|----------|----------|
| 🪟 **Windows** | [PersianLearning-Windows.zip](https://github.com/YOUR_USERNAME/persian-learning-app/releases/latest/download/PersianLearning-Windows.zip) |
| 🍎 **macOS** | [PersianLearning-macOS.zip](https://github.com/YOUR_USERNAME/persian-learning-app/releases/latest/download/PersianLearning-macOS.zip) |

> **macOS users**: After unzipping, drag `PersianLearning.app` to the Applications folder. On first launch, right-click → **Open** (since this app is not notarized by Apple).

---

## 🚀 Quick Start (from source)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/persian-learning-app.git
cd persian-learning-app

# 2. Install dependencies
pip install pyqt6 PyQt6-WebEngine requests beautifulsoup4 lxml

# 3. Run
python main.py
```

---

## 🛠 Build (from source)

```bash
pip install pyinstaller

# Windows
pyinstaller --onefile --windowed --add-data "data;data" \
  --hidden-import=PyQt6.QtWebEngineWidgets \
  --hidden-import=PyQt6.QtWebChannel \
  --hidden-import=bs4 --hidden-import=lxml --hidden-import=aiohttp \
  --name="PersianLearning" main.py

# macOS
pyinstaller --onedir --windowed --add-data "data:data" \
  --hidden-import=PyQt6.QtWebEngineWidgets \
  --hidden-import=PyQt6.QtWebChannel \
  --hidden-import=bs4 --hidden-import=lxml --hidden-import=aiohttp \
  --name="PersianLearning" \
  --osx-bundle-identifier=com.persianlearning.app main.py
```

---

## 🧱 Tech Stack

- **UI**: PyQt6 (desktop GUI)
- **Scraping**: requests + BeautifulSoup4 + lxml
- **Packaging**: PyInstaller (single-file / .app bundle)
- **CI/CD**: GitHub Actions (Windows + macOS auto-build)

---

## 📝 License

MIT
