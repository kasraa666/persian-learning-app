#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
波斯语学习助手 — 爬虫层
根据实际网站数据结构编写

VajehYab: 数据在 window.__INITIAL_DATA__ JSON 中（非 JS 渲染页拿不到 DOM）
Abadis:   数据在 body > main 中，正常 HTML
Radio Farda: div.media-block__content h4 > a[href*="/a/"]
"""

import re
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
TIMEOUT = 15

DICT_NAMES = {
    "dehkhoda": "لغت‌نامه دهخدا",
    "moein": "فرهنگ معین",
    "amid": "فرهنگ عمید",
    "motaradef": "مترادف و متضاد",
    "fa2en": "فارسی به انگلیسی",
    "en2fa": "انگلیسی به فارسی",
    "fa2tr": "فارسی به ترکی",
    "sareh": "فرهنگ سره",
    "farhangestan": "فرهنگستان",
    "quran": "قرآن",
}

SECTION_LABELS = {
    "meaning": "📖 معنی | 释义",
    "alternative": "🔄 برابر | 替代词",
    "synonym": "🔗 مترادف | 近义词",
    "dictionary": "🌐 دیکشنری | 英译",
}


# ================================================================
#  VajehYab 查词 — 解析 __INITIAL_DATA__ JSON
# ================================================================

def search_vajehyab(word):
    """在 VajehYab 查词，提取页面内嵌 JSON 数据"""
    url = f"https://vajehyab.com/?q={urllib.parse.quote(word)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        data = _extract_initial_data(resp.text)
        if not data:
            return _not_found(word), url

        result = data.get("result", {})
        parts = []

        wordbox = result.get("wordbox")
        if wordbox:
            parts.append(_render_wordbox(wordbox))

        for section in result.get("results", []):
            for hit in section.get("hits", []):
                parts.append(_render_hit(hit))

        if parts:
            return f"<div style='font-family:'Times New Roman',Tahoma,serif;direction:rtl;text-align:right;'>{''.join(parts)}</div>", url
        return _not_found(word), url
    except Exception as e:
        return f"<p style='color:#F53F3F;'>查询失败: {str(e)}</p>", url


def search_amid(word):
    """在 VajehYab 的 Amid 词典查询（同样解析 JSON）"""
    url = f"https://vajehyab.com/amid/{urllib.parse.quote(word)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        data = _extract_initial_data(resp.text)
        if not data:
            return _not_found(word), url

        result = data.get("result", {})
        parts = []

        wordbox = result.get("wordbox")
        if wordbox:
            parts.append(_render_wordbox(wordbox))

        for section in result.get("results", []):
            for hit in section.get("hits", []):
                parts.append(_render_hit(hit))

        if parts:
            return f"<div style='font-family:'Times New Roman',Tahoma,serif;direction:rtl;text-align:right;'>{''.join(parts)}</div>", url
        return _not_found(word), url
    except Exception as e:
        return f"<p style='color:#F53F3F;'>查询失败: {str(e)}</p>", url


def _extract_initial_data(html_text):
    """从 HTML 中提取 window.__INITIAL_DATA__"""
    # 匹配 JSON 对象直到闭合的大括号
    # __INITIAL_DATA__ 内容包含嵌套对象，需要匹配到闭合
    match = re.search(r'window\.__INITIAL_DATA__\s*=\s*(\{.*?\});\s*\n\s*</script>', html_text, re.DOTALL)
    if not match:
        # 尝试更宽松的匹配
        match = re.search(r'window\.__INITIAL_DATA__\s*=\s*(\{.*?\});', html_text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _render_wordbox(wordbox):
    """渲染词头区"""
    title = wordbox.get("title", "")
    subtitle = wordbox.get("subtitle", "")

    html = '<div style="background:#F7F8FA;border-radius:12px;padding:18px;margin-bottom:18px;">'
    html += f'<div style="font-size:24px;font-weight:700;color:#165DFF;">{title}</div>'
    if subtitle:
        html += f'<div style="font-size:16px;color:#4E5969;margin-top:6px;">{subtitle}</div>'

    for sec in wordbox.get("sections", []):
        sec_name = sec.get("section", "")
        desc = sec.get("description", "")
        label = SECTION_LABELS.get(sec_name, sec_name)
        html += f'<div style="margin-top:14px;"><span style="color:#165DFF;font-size:13px;font-weight:600;">{label}</span>'
        html += f'<p style="margin:6px 0 0 0;line-height:2.2;color:#1D2129;">{desc}</p></div>'

    html += '</div>'
    return html


def _render_hit(hit):
    """渲染单个词条"""
    title = hit.get("title", "")
    subtitle = hit.get("subtitle", "")
    summary = hit.get("summary", "")
    pronunciation = hit.get("pronunciation", "")
    dict_name = hit.get("dictionarySlug", "")
    dict_label = DICT_NAMES.get(dict_name, dict_name)

    h = '<div style="background:#F7F8FA;border-radius:8px;padding:12px;margin:8px 0;">'
    h += f'<span style="color:#165DFF;font-size:18px;font-weight:bold;">{title}</span>'
    if subtitle:
        h += f' <span style="color:#4E5969;font-size:14px;">({subtitle})</span>'
    if pronunciation:
        h += f' <span style="color:#86909C;font-size:13px;">[{pronunciation}]</span>'
    h += f'<br><span style="color:#165DFF;font-size:11px;">📘 {dict_label}</span>'
    if summary:
        h += f'<p style="margin:6px 0 0 0;line-height:2;text-align:justify;color:#1D2129;">{summary}</p>'
    h += '</div>'
    return h


def _not_found(word):
    return f"<p style='color:#F53F3F;text-align:center;padding:40px;'>未找到 &laquo;{word}&raquo;</p>"


# ================================================================
#  Abadis 查词 — 解析 HTML DOM
# ================================================================

def search_abadis(word):
    """在 Abadis.ir 查英波词"""
    url = f"https://abadis.ir/entofa/{urllib.parse.quote(word)}/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        content = soup.select_one("main")
        if not content:
            return _not_found(word), url

        # 提取有意义的盒子，移除事件属性
        parts = []
        for box in content.select("div.boxWrd, div.boxTr, div.boxRel, div.lun.boxBd"):
            box_html = str(box)
            box_html = re.sub(r'\s+on\w+="[^"]*"', '', box_html)
            parts.append(box_html)

        if parts:
            return f"<div style='font-family:'Times New Roman',Tahoma,serif;direction:ltr;'>{''.join(parts)}</div>", url
        return _not_found(word), url
    except Exception as e:
        return f"<p style='color:#F53F3F;'>查询失败: {str(e)}</p>", url


# ================================================================
#  新闻爬取
# ================================================================

def fetch_radiofarda_news():
    """
    Radio Farda — 可直连
    结构: div.media-block__content 内的 h4 > a[href*="/a/"]
    """
    items = []
    try:
        url = "https://www.radiofarda.com/"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        seen_urls = set()
        noise = ["infgraphics", "wsw__embed", "banner", "teaser", "social", "share"]

        for a in soup.select('a[href*="/a/"]'):
            href = a.get("href", "").strip()
            if not href:
                continue

            h4 = a.find("h4")
            title = h4.get_text(strip=True) if h4 else a.get_text(strip=True)
            if not title or len(title) < 15:
                continue

            # 检查父级是否为噪声
            p_cls = " ".join(a.parent.get("class", [])).lower() if a.parent else ""
            gp_cls = " ".join(a.parent.parent.get("class", [])).lower() if a.parent and a.parent.parent else ""
            if any(n in p_cls + gp_cls for n in noise):
                continue

            if href.startswith("/"):
                full_url = "https://www.radiofarda.com" + href
            elif "int_cid=banner" in href:
                continue
            elif href.startswith("http"):
                full_url = href
            else:
                continue

            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            items.append({
                "title": title,
                "url": full_url,
                "desc": "Radio Farda | رادیو فردا",
                "source": "Radio Farda",
                "type": "news",
            })

        # 标题去重
        seen_titles = set()
        unique = []
        for item in items:
            if item["title"] not in seen_titles:
                seen_titles.add(item["title"])
                unique.append(item)
        return unique[:25]
    except Exception:
        return [{"title": "Radio Farda 首页", "url": "https://www.radiofarda.com/", "desc": "رادیو فردا", "source": "Radio Farda", "type": "link"}]


def fetch_bbc_persian():
    """
    BBC Persian — 从首页爬取
    返回结构：
      1. 一个"总览页"条目（BBC Persian 首页链接）
      2. 若干栏目导航（topic 页）
      3. 若干具体文章（article 页，/persian/articles/ 路径）
    """
    items = []
    base = "https://www.bbc.com/persian"
    seen_urls = set()

    try:
        resp = requests.get(base, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        # --- 1. 首页总览（放在最前面）---
        items.append({
            "title": "BBC Persian 首页 — همه اخبار",
            "url": base,
            "desc": "BBC 波斯语新闻总览 | صفحه اصلی بی‌بی‌سی فارسی",
            "source": "BBC Persian",
            "type": "home",
        })
        seen_urls.add(base)

        # --- 2. 栏目导航（topic 页）---
        topic_entries = []
        for a in soup.find_all("a", href=lambda h: h and "/persian/topics/" in h):
            title = a.get_text(strip=True)
            href = a["href"]
            if len(title) < 2:
                continue
            # 排除纯数字、纯英文标签等噪声
            if title in ("صفحه فعلی", "current page"):
                continue
            # 有些 topic 是重复出现的（导航栏 + 正文各一次），按 title 去重
            if not href.startswith("http"):
                href = "https://www.bbc.com" + href
            if href in seen_urls:
                continue
            seen_urls.add(href)
            # 排除过长标题的（通常是文章混进来的）
            if len(title) > 25:
                continue
            topic_entries.append({
                "title": title,
                "url": href,
                "desc": f"BBC Persian — {title} (栏目)",
                "source": "BBC Persian",
                "type": "section",
            })

        # 按标题去重
        seen_titles = set()
        unique_topics = []
        for t in topic_entries:
            if t["title"] not in seen_titles:
                seen_titles.add(t["title"])
                unique_topics.append(t)
        items.extend(unique_topics[:10])

        # --- 3. 具体文章（article 页）---
        article_entries = []
        for a in soup.find_all("a", href=lambda h: h and "/persian/articles/" in h):
            title = a.get_text(strip=True)
            href = a["href"]
            if len(title) < 15:
                continue
            if not href.startswith("http"):
                href = "https://www.bbc.com" + href
            if href in seen_urls:
                continue
            seen_urls.add(href)
            # 跳过噪音——标题里有 "ویدیو,مدت" 这种格式的视频摘要
            if title.startswith("ویدیو,"):
                title = title.replace("ویدیو,", "🎬 ", 1)
                # 清理末尾的 مدت 0,xx
                import re
                title = re.sub(r',\s*مدت\s+[\d,]+$', '', title)
            article_entries.append({
                "title": title,
                "url": href,
                "desc": "BBC Persian | بی‌بی‌سی فارسی",
                "source": "BBC Persian",
                "type": "article",
            })

        # 标题去重（同一篇文章可能在不同区块出现）
        seen_at = set()
        unique_articles = []
        for a in article_entries:
            if a["title"] not in seen_at:
                seen_at.add(a["title"])
                unique_articles.append(a)

        items.extend(unique_articles[:30])

        return items
    except Exception:
        return [
            {"title": "BBC Persian 首页 — صفحه اصلی", "url": base, "desc": "BBC 波斯语新闻总览（需科学上网）", "source": "BBC Persian", "type": "home"},
            {"title": "BBC Persian 视频", "url": "https://www.bbc.com/persian/topics/c9wq7rw059dt", "desc": "波斯语视频报道", "source": "BBC Persian", "type": "section"},
            {"title": "BBC Persian 播客", "url": "https://www.bbc.com/persian/podcasts", "desc": "波斯语音频节目", "source": "BBC Persian", "type": "section"},
        ]


def fetch_euronews_persian():
    """
    Euronews Persian — 可直连 (parsi.euronews.com)
    实际结构: a 标签，含 /news/ 或 /travel/ 等路径即文章链接
    """
    items = []
    base = "https://parsi.euronews.com"
    seen_urls = set()

    try:
        resp = requests.get(base, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        # 首页总览
        items.append({
            "title": f"Euronews Persian 首页 — صفحه اصلی یورونیوز",
            "url": base,
            "desc": "Euronews 波斯语新闻总览 | یورونیوز فارسی（可直连）",
            "source": "Euronews",
            "type": "home",
        })
        seen_urls.add(base)

        # Topic/栏目导航
        seen_titles = set()
        for a in soup.find_all("a", href=lambda h: h and "/tag/" in h):
            title = a.get_text(strip=True)
            href = a["href"]
            if len(title) < 2 or len(title) > 30:
                continue
            if not href.startswith("http"):
                href = base + href
            if href in seen_urls or title in seen_titles:
                continue
            seen_urls.add(href)
            seen_titles.add(title)
            items.append({
                "title": title,
                "url": href,
                "desc": f"Euronews — {title} (话题)",
                "source": "Euronews",
                "type": "section",
            })

        # 文章链接: 匹配 /news/, /travel/, /culture/, /sport/, /business/ 等
        import re
        article_pattern = re.compile(r'^/(?:news|travel|culture|sport|business|health|science|green|my-europe|next)/')

        articles_seen = set()
        for a in soup.find_all("a", href=article_pattern):
            title = a.get_text(strip=True)
            href = a["href"]
            if len(title) < 15:
                continue
            if not href.startswith("http"):
                href = base + href
            if href in seen_urls or title in articles_seen:
                continue
            seen_urls.add(href)
            articles_seen.add(title)
            items.append({
                "title": title,
                "url": href,
                "desc": "Euronews Persian | یورونیوز فارسی",
                "source": "Euronews",
                "type": "article",
            })

        return items[:40] if items else [
            {"title": "Euronews Persian", "url": base, "desc": "یورونیوز فارسی（可直连）", "source": "Euronews", "type": "home"},
        ]
    except Exception:
        return [{"title": "Euronews Persian", "url": base, "desc": "یورونیوز فارسی", "source": "Euronews", "type": "home"}]


def fetch_khabaronline_news():
    """
    Khabar Online (خبرآنلاین) — 伊朗国内新闻，可直连
    文章链接格式: /news/<id>/<slug>
    """
    items = []
    base = "https://www.khabaronline.ir"
    seen_urls = set()
    seen_titles = set()

    try:
        resp = requests.get(base, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        # 首页总览
        items.append({
            "title": "خبرآنلاین 首页 — Khabar Online",
            "url": base,
            "desc": "Khabar Online | خبرآنلاین — 伊朗新闻（可直连）",
            "source": "Khabar Online",
            "type": "home",
        })
        seen_urls.add(base)

        # 文章链接: /news/<id>/<slug>
        for a in soup.find_all("a", href=lambda h: h and "/news/" in h):
            href = a.get("href", "").strip()
            title = a.get_text(strip=True)

            if len(title) < 15:
                continue
            # 排除 tag / service 页面
            if "/tag/" in href or "/service/" in href:
                continue

            if not href.startswith("http"):
                href = base + href

            if href in seen_urls or title in seen_titles:
                continue
            seen_urls.add(href)
            seen_titles.add(title)

            items.append({
                "title": title,
                "url": href,
                "desc": "Khabar Online | خبرآنلاین",
                "source": "Khabar Online",
                "type": "article",
            })

        return items[:35] if len(items) > 1 else [
            {"title": "Khabar Online — 首页", "url": base, "desc": "خبرآنلاین", "source": "Khabar Online", "type": "home"},
        ]
    except Exception:
        return [{"title": "Khabar Online", "url": base, "desc": "خبرآنلاین", "source": "Khabar Online", "type": "home"}]


def fetch_isna_news():
    """
    ISNA — 被 ArvanCloud 反爬保护，JS challenge 无法绕过
    替代方案: 使用 Khabar Online 作为伊朗国内新闻源
    """
    return fetch_khabaronline_news()


def fetch_article_content(url):
    """尝试提取文章正文"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        for sel in ["article", "div.wsw", "div.article-body", "div.story-body",
                      "div.content", "main", "div.body", "div[itemprop='articleBody']",
                      "div.article-content", "div.item-body", "div.news-body", "div.item-text"]:
            found = soup.select_one(sel)
            if found and len(found.get_text(strip=True)) > 100:
                return str(found)

        return str(soup.body) if soup.body else str(soup)
    except Exception as e:
        return f"<p style='color:#F53F3F;'>无法加载文章: {str(e)}</p>"


# ================================================================
#  资源爬取
# ================================================================

def fetch_easy_persian_lessons():
    """EasyPersian.com"""
    items = []
    try:
        url = "https://www.easypersian.com/"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        seen = set()
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            title = a.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            if not any(x in href.lower() for x in ["lesson", "persian-", "farsi", "alphabet", "grammar", "vocabulary"]):
                continue
            if href.startswith("/"):
                href = "https://www.easypersian.com" + href
            elif not href.startswith("http"):
                href = urllib.parse.urljoin(url, href)
            if href in seen:
                continue
            seen.add(href)
            items.append({"title": title, "url": href, "desc": "EasyPersian.com — 免费波斯语教程", "source": "Easy Persian", "type": "tutorial"})
        return items[:30] if items else [{"title": "Easy Persian — 课程首页", "url": "https://www.easypersian.com/", "desc": "150+ 课免费教程", "source": "Easy Persian", "type": "tutorial"}]
    except Exception:
        return [{"title": "Easy Persian", "url": "https://www.easypersian.com/", "desc": "150+ 课免费教程", "source": "Easy Persian", "type": "tutorial"}]


def fetch_persian_language_online():
    """PersianLanguageOnline.com"""
    items = []
    try:
        url = "https://persianlanguageonline.com/"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        seen = set()
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            title = a.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            if "persianlanguageonline.com" in href or href.startswith("/") or \
               any(x in href.lower() for x in ["lesson", "course", "learn"]):
                if href.startswith("/"):
                    href = "https://persianlanguageonline.com" + href
                elif not href.startswith("http"):
                    href = urllib.parse.urljoin(url, href)
                if href in seen:
                    continue
                seen.add(href)
                items.append({"title": title, "url": href, "desc": "Persian Language Online — 免费课程", "source": "Persian Language Online", "type": "tutorial"})
        return items[:20] if items else [{"title": "Persian Language Online", "url": "https://persianlanguageonline.com/", "desc": "免费波斯语课程", "source": "Persian Language Online", "type": "tutorial"}]
    except Exception:
        return [{"title": "Persian Language Online", "url": "https://persianlanguageonline.com/", "desc": "免费波斯语课程", "source": "Persian Language Online", "type": "tutorial"}]


# ================================================================
#  预置资源（稳定内容）
# ================================================================

YOUTUBE_CHANNELS = [
    {"title": "PersianPod101 — 系统波斯语教学", "url": "https://www.youtube.com/@PersianPod101", "desc": "英语授课，从入门到中级", "source": "YouTube", "type": "video"},
    {"title": "Learn Persian with Chai and Conversation", "url": "https://www.youtube.com/@chaiandconversation", "desc": "波斯语口语对话教学", "source": "YouTube", "type": "video"},
    {"title": "Persian Learning — 语法与词汇", "url": "https://www.youtube.com/@PersianLearning", "desc": "波斯语语法详解、词汇拓展", "source": "YouTube", "type": "video"},
    {"title": "Reza Nazari — 阅读与诗歌", "url": "https://www.youtube.com/@RezaNazari", "desc": "波斯语阅读练习、文学赏析", "source": "YouTube", "type": "video"},
    {"title": "Manoto TV — 伊朗电视节目", "url": "https://www.youtube.com/@manototv", "desc": "综艺、访谈、纪录片", "source": "YouTube", "type": "video"},
    {"title": "Radio Javan — 伊朗音乐与访谈", "url": "https://www.youtube.com/@radiojavan", "desc": "流行音乐 + 歌手访谈", "source": "YouTube", "type": "video"},
    {"title": "YouTube 搜索: آموزش زبان فارسی", "url": "https://www.youtube.com/results?search_query=%D8%A2%D9%85%D9%88%D8%B2%D8%B4+%D8%B2%D8%A8%D8%A7%D9%86+%D9%81%D8%A7%D8%B1%D8%B3%DB%8C", "desc": "波斯语授课的波斯语教学", "source": "YouTube", "type": "search"},
]

PERSIAN_PODCASTS = [
    {"title": "ChannelB — چنل‌بی (科技/文化)", "url": "https://channelbpodcast.com/", "desc": "伊朗最受欢迎播客。语速适中，中级学习者最佳。", "source": "播客", "type": "audio"},
    {"title": "Ravaaq (رواق) — 历史哲学播客", "url": "https://castbox.fm/channel/Ravaaq-id4168082", "desc": "深度讨论波斯历史与哲学，用词正式", "source": "播客", "type": "audio"},
    {"title": "BPlus Podcast — بی‌پلاس", "url": "https://bpluspodcast.com/", "desc": "每期深入探讨一本书或话题", "source": "播客", "type": "audio"},
    {"title": "Khabgard (خبرگرد) — 新闻评论", "url": "https://khabgard.com/", "desc": "每周新闻综述，了解伊朗时事", "source": "播客", "type": "audio"},
    {"title": "Naav (نَو) — 创业与商业", "url": "https://naav.me/", "desc": "伊朗创业生态、科技商业话题", "source": "播客", "type": "audio"},
]

PERSIAN_RESOURCES = [
    {"title": "Dehkhoda Dictionary (لغت‌نامه دهخدا)", "url": "https://dehkhoda.ut.ac.ir/", "desc": "最权威的波斯语词典", "source": "资源", "type": "tool"},
    {"title": "VajehYab (واژه‌یاب)", "url": "https://vajehyab.com/", "desc": "聚合多种波斯语词典", "source": "资源", "type": "tool"},
    {"title": "Abadis (آبادیس)", "url": "https://abadis.ir/", "desc": "英波双语词典 + 翻译", "source": "资源", "type": "tool"},
    {"title": "Ganjoor (گنجور)", "url": "https://ganjoor.net/", "desc": "波斯古典诗歌全集（حافظ، سعدی، مولوی...）", "source": "资源", "type": "literature"},
    {"title": "Persian Wikipedia (ویکی‌پدیای فارسی)", "url": "https://fa.wikipedia.org/", "desc": "波斯语维基百科——海量阅读材料", "source": "资源", "type": "encyclopedia"},
]
