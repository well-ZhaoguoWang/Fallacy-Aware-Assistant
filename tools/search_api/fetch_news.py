import re
from typing import Optional
import requests
from bs4 import BeautifulSoup
from readability import Document


def fetch_news_main_text(
    url: str,
    target: str,
    seg_len: int = 500,
    timeout: int = 10,
    ua: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
) -> str:
    """
    Fetch the main body of a news/article page and return a stitched excerpt:
      (i) the first `seg_len` characters,
      (ii) `seg_len` characters before and after `target`,
      (iii) the last `seg_len` characters.

    Segments are concatenated with " … ". If `target` is not found,
    return only: head segment + " … " + tail segment.

    :param url:     News/article URL.
    :param target:  Target text to center the middle excerpt around.
    :param seg_len: Segment length in characters (default 500).
    :param timeout: Requests timeout in seconds.
    :param ua:      User-Agent string.
    :return:        The concatenated excerpt string.
    """
    # ---------- 1) Download ----------
    resp = requests.get(url, headers={"User-Agent": ua}, timeout=timeout)
    resp.encoding = resp.apparent_encoding
    if resp.status_code != 200:
        raise RuntimeError(f"Request failed: HTTP {resp.status_code}")
    html = resp.text

    # ---------- 2) Extract main text ----------
    try:
        soup = BeautifulSoup(Document(html).summary(), "lxml")
    except Exception:  # fallback
        soup = BeautifulSoup(html, "lxml")

    article_tag = soup.find("article") or soup
    text = article_tag.get_text(separator="\n", strip=True)
    text = re.sub(r"\s+", " ", text).strip()

    # If total text is short (<= 3 segments), return the whole text
    if len(text) <= seg_len * 3:
        return text

    # ---------- 3) Segment slicing ----------
    begin_part = text[:seg_len]
    end_part = text[-seg_len:]

    # Middle segment: `seg_len` before and after the target string
    mid_part: Optional[str] = None
    if target:
        target_clean = re.sub(r"\s+", " ", target).strip()
        pos = text.find(target_clean)
        if pos != -1:
            start = max(0, pos - seg_len)
            end = min(len(text), pos + len(target_clean) + seg_len)
            mid_part = text[start:end]

            # If the middle segment heavily overlaps with head/tail, trim them a bit
            if start < seg_len * 0.2:  # almost touching the beginning
                begin_part = text[:start]  # shorten the head to avoid repetition
            if end > len(text) - seg_len * 0.2:  # almost touching the end
                end_part = text[end:] or ""  # shorten the tail

    # ---------- 4) Merge segments ----------
    parts = [begin_part]
    if mid_part:
        parts.append("…")  # ellipsis separator
        parts.append(mid_part)
    parts.append("…")
    parts.append(end_part)

    # Avoid repeated ellipses / empty fragments
    final = (
        " ".join([p for p in parts if p and p != ""])
        .replace(" …  … ", " … ")
        .strip(" …")
    )

    return final


# --------------------- Example usage ---------------------
if __name__ == "__main__":
    demo_url = "https://x.com/FearedBuck/status/1945681681626943775"
    demo_target = (
        "“The government shouldn’t ban drugs; otherwise it should also ban cannabis, "
        "tobacco, and alcohol. If so, then high-fat snacks and cavity-causing candy "
        "should be banned too. In the end, government would only allow us to drink "
        "juice and eat healthy foods.”"
    )
    print(fetch_news_main_text(demo_url, demo_target))
