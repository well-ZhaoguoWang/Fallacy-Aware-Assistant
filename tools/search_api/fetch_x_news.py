import os
import praw
import concurrent.futures
from typing import List, Tuple

from main.muti_agents import CommentModerator
from tools.deepseek_service.ask_deepseek import ask_deepseek

moderator = CommentModerator()

# --- Reddit credentials (consider loading from environment variables) ---
# client_id = os.getenv("REDDIT_CLIENT_ID")
# client_secret = os.getenv("REDDIT_CLIENT_SECRET")
# user_agent = os.getenv("REDDIT_USER_AGENT", "huang-app:v1.0")
client_id = "maLsAkyYfNGCr8gQoZE3WA"
client_secret = "Vt5aZj1DFOwbzz7OPCqjCz8_k-iOWQ"
user_agent = "huang-app:v1.0"

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
)


def get_reddit_comments(url: str) -> Tuple[str, List[str]]:
    """
    Fetch all comments for a Reddit submission.
    :param url: Submission URL
    :return: (news-like context string, list of comment bodies)
    """
    submission = reddit.submission(url=url)
    content = f"Title: {submission.title}\nBody: {submission.selftext or ''}"

    # Expand all comments (could be slow for very large threads)
    submission.comments.replace_more(limit=None)

    # Collect raw comment texts, skipping empty/removed
    comments = []
    for c in submission.comments.list():
        body = (c.body or "").strip()
        if body and body.lower() not in {"[deleted]", "[removed]"}:
            comments.append(body)

    return content, comments


def fetch_reddit_comments(url: str) -> str:
    """
    Run fallacy detection on up to 20 comments from a Reddit post,
    then ask the LLM to summarize the findings in plain text.
    """
    content, comments = get_reddit_comments(url)
    ans = []

    if comments:
        comments = comments[:20]  # cap to 20 comments

        def detect(comment: str):
            return moderator.detector.run(news=content, comment=comment, language="en")

        # Concurrent detection
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(detect, comments))
        ans.extend(results)

    prompt = (
        "Below are detected fallacies from a Reddit post's comment section. "
        "Please provide a brief summary of what patterns you see across comments, "
        "including the most common fallacy types and any notable caveats.\n\n"
        f"{str(ans)}\n\n"
        "Requirements: write plain natural text in paragraphs; do NOT use Markdown."
    )

    return ask_deepseek(prompt, language="en", model="v3")


if __name__ == "__main__":
    test_url = "https://reddit.com/r/indianrailways/comments/1m2615j/its_mumbai_bandra_east_garib_nagar_view/"
    result = fetch_reddit_comments(test_url)
    print(result)
