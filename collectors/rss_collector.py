# collectors/rss_collector.py - RSS 피드 수집
import feedparser
from datetime import datetime, timezone, timedelta
from config import RSS_FEEDS, RSS_MAX_ITEMS


def collect() -> list[dict]:
    """
    RSS 피드에서 최신 기사를 수집합니다.
    Returns: [{"title": str, "url": str, "summary": str, "source": str}]
    """
    items = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)  # 최근 48시간

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            feed_count = 0
            for entry in feed.entries[:3]:  # 피드당 최대 3개
                # 날짜 파싱
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

                # 기간 이내 기사만
                if published and published < cutoff:
                    continue

                summary = ""
                if hasattr(entry, "summary"):
                    summary = entry.summary[:300]
                elif hasattr(entry, "description"):
                    summary = entry.description[:300]

                items.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": summary,
                    "source": feed.feed.get("title", feed_url),
                    "type": "rss",
                })
                feed_count += 1

        except Exception as e:
            print(f"[RSS] {feed_url} 수집 실패: {e}")

    return items[:RSS_MAX_ITEMS]
