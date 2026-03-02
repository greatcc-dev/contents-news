# collectors/news_collector.py - NewsAPI 수집
import requests
from config import NEWS_API_KEY, NEWS_KEYWORDS, NEWS_MAX_ITEMS


def collect() -> list[dict]:
    """
    NewsAPI로 YouTube/크리에이터 관련 최신 뉴스를 수집합니다.
    API 키 없으면 빈 리스트 반환 (선택 사항).
    Returns: [{"title": str, "url": str, "summary": str, "source": str}]
    """
    if not NEWS_API_KEY:
        print("[News] NEWS_API_KEY 없음 - 건너뜀")
        return []

    items = []
    query = " OR ".join(f'"{kw}"' for kw in NEWS_KEYWORDS[:3])

    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": NEWS_MAX_ITEMS,
                "apiKey": NEWS_API_KEY,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        for article in data.get("articles", [])[:NEWS_MAX_ITEMS]:
            items.append({
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "summary": (article.get("description") or "")[:300],
                "source": article.get("source", {}).get("name", "NewsAPI"),
                "type": "news",
            })

    except Exception as e:
        print(f"[News] 수집 실패: {e}")

    return items
