# Persian Learning App | دستیار یادگیری فارسی

A PyQt6 desktop application for learning Persian (Farsi) — dictionary lookup, news reading, curated learning resources, and vocabulary management, all in one place.

<p align="center">
  <em>Add screenshots here</em>
</p>

---

## ✨ Features

| Tab | Description |
|---|---|
| 📖 **Dictionary** | Look up Persian words across three dictionaries: **VajehYab** (Dehkhoda, Moein, Amid — aggregated), **Abadis** (English–Persian bilingual), and **Amid**. One-click save words to your vocabulary. |
| 📰 **News** | Read Persian articles from **Radio Farda**, **BBC Persian**, **Euronews Persian**, and **Khabar Online**. Tap any headline to fetch the full article. Save articles as bookmarks. |
| 📚 **Resources** | Curated Persian learning materials: YouTube channels (PersianPod101, Chai and Conversation), podcasts (ChannelB, Ravaaq, BPlus, Khabgard, Naav), **Easy Persian** (150+ free lessons), **Persian Language Online**, and more. |
| ⭐ **My Library** | Two sub-tabs: **Vocabulary** (saved words with dictionary source and date) and **Bookmarks** (saved articles with category and date). Delete support with confirmation. |

---

## 📦 Installation

### Option 1: Download (recommended)

Go to [Releases](../../releases) and download `PersianLearning.exe`. Double-click to run — no Python or dependencies required.

### Option 2: Run from source

```bash
git clone https://github.com/kasraa666/persian-learning-app.git
cd persian-learning-app
pip install PyQt6 requests beautifulsoup4 lxml brotlicffi
python main.py
```

### Option 3: Build the .exe yourself

```bash
pip install pyinstaller
pyinstaller PersianLearning.spec
# Output: dist/PersianLearning.exe
```

---

## ⚠️ Important Notes

- **Internet required** — Dictionary lookup, news fetching, and resource aggregation all depend on live web scraping. Only your saved vocabulary and bookmarks are available offline.
- **VPN may be needed** — BBC Persian and some other sources may be inaccessible from certain regions.
- **Fragile by nature** — This app parses live website HTML. If a source site changes its structure, the corresponding feature may temporarily break until the parser is updated.
- **Windows only** — Currently packaged for Windows. macOS / Linux are not tested or supported.

---

## 📁 Project Structure

```
persian-learning-app/
├── main.py                  # Entry point
├── PersianLearning.spec     # PyInstaller spec
├── app/
│   ├── main_window.py       # Main window, tab bar, status bar
│   ├── dict_tab.py          # Dictionary lookup tab
│   ├── news_tab.py          # Persian news tab
│   ├── resources_tab.py     # Learning resources tab
│   ├── saved_tab.py         # Saved vocabulary & bookmarks tab
│   ├── fetcher.py           # Web scraping layer (HTTP + HTML parsing)
│   ├── vocabulary.py        # Vocabulary CRUD (JSON storage)
│   └── styles.py            # Global Qt stylesheet & data directory
├── data/                    # User data (vocabulary.json, bookmarks.json)
└── .github/workflows/       # CI/CD (GitHub Actions)
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| GUI | PyQt6 |
| HTTP & Parsing | Requests, BeautifulSoup4, lxml |
| Packaging | PyInstaller (single .exe) |
| CI/CD | GitHub Actions |

---

## 🙏 Data Sources

This app aggregates content from the following websites:

- [VajehYab](https://vajehyab.com/) — Persian dictionary aggregator (Dehkhoda, Moein, Amid)
- [Abadis](https://abadis.ir/) — English–Persian bilingual dictionary
- [Radio Farda](https://www.radiofarda.com/) — Persian news
- [BBC Persian](https://www.bbc.com/persian) — Persian news
- [Euronews Persian](https://parsi.euronews.com/) — Persian news
- [Khabar Online](https://www.khabaronline.ir/) — Iranian news
- [Easy Persian](https://www.easypersian.com/) — Free Persian lessons
- [Persian Language Online](https://persianlanguageonline.com/) — Online learning resources

---

## 📝 License

MIT — see [LICENSE](LICENSE) for details.
