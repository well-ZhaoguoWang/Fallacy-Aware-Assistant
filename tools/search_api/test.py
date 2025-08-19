import snscrape.modules.twitter as sntwitter
from snscrape.base import ScraperException

tweet_id = 1945681681626943775

# 1. Single Tweet
try:
    t = next(sntwitter.TwitterTweetScraper(tweet_id).get_items())
    print("Original tweet OK:", t.id, t.user.username, t.date)
except StopIteration:
    print("Original tweet not visible!")

# 2. Conversation search
try:
    scr = sntwitter.TwitterSearchScraper(f"conversation_id:{tweet_id}")
    first = next(scr.get_items())
    print("Conversation search OK, first item:", first.id)
except ScraperException as e:
    print("Conversation search failed:", e)
except StopIteration:
    print("Conversation search returned no data (no exception)")
