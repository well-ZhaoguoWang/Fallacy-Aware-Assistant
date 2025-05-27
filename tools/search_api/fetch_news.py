import re
import requests
from readability import Document          # 自动提取“正文”最稳的库
from bs4 import BeautifulSoup


def fetch_news_main_text(url: str,
                         max_length: int = 2000,
                         timeout: int = 10,
                         ua: str = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/126.0.0.0 Safari/537.36")) -> str:
    """
    根据新闻地址爬取主要内容，并截断到 max_length 个字符以内
    :param url: 新闻页面 URL
    :param max_length: 返回文本最大字符数，默认 1000
    :param timeout: requests 超时时间（秒），默认 10
    :param ua: 伪装的 User-Agent，防止被简单反爬
    :return: 清洗后的正文（utf-8 字符串）
    """
    # ---------- 1. 下载网页 ----------
    resp = requests.get(url, headers={"User-Agent": ua}, timeout=timeout)
    # 自动识别编码，防止中文页面乱码
    resp.encoding = resp.apparent_encoding

    if resp.status_code != 200:
        raise RuntimeError(f"请求失败：HTTP {resp.status_code}")

    html = resp.text

    # ---------- 2. 尝试用 readability 提取正文 ----------
    try:
        readable_doc = Document(html)
        cleaned_html = readable_doc.summary()        # 只保留正文的 HTML 子树
        soup = BeautifulSoup(cleaned_html, "lxml")
    except Exception:                                # ↘ 如果正文提取失败就 fallback
        soup = BeautifulSoup(html, "lxml")

    # ---------- 3. 提取纯文本 ----------
    # 如果有 <article> 标签就优先用它；没有就退而求其次
    article_tag = soup.find("article") or soup
    text = article_tag.get_text(separator="\n", strip=True)

    # ---------- 4. 文本清洗 ----------
    # 合并多余空白、去掉多连续换行
    text = re.sub(r"\s+", " ", text).strip()

    # ---------- 5. 截断 ----------
    if len(text) > max_length:
        text = text[:max_length]

    return text


# --------------------- 示范用法 ---------------------
if __name__ == "__main__":
    demo_url = "https://globalvoices.org/2018/03/27/lgbtqi-rights-defenders-sound-alarm-over-costa-ricas-presidential-election/"
    print(fetch_news_main_text(demo_url))
