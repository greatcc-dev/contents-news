# collectors/youtube_collector.py - YouTube Data API v3 수집
import requests
from config import YOUTUBE_API_KEY, YOUTUBE_REGION, YOUTUBE_MAX_RESULTS, YOUTUBE_CATEGORY_IDS


def collect() -> list[dict]:
    """
    YouTube Data API로 인기 영상을 수집합니다.
    API 키 없으면 빈 리스트 반환 (선택 사항).
    Returns: [{"title": str, "url": str, "summary": str, "source": str}]
    """
    if not YOUTUBE_API_KEY:
        print("[YouTube] YOUTUBE_API_KEY 없음 - 건너뜀")
        return []

    items = []

    for category_id in YOUTUBE_CATEGORY_IDS:
        try:
            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "snippet,statistics",
                    "chart": "mostPopular",
                    "regionCode": YOUTUBE_REGION,
                    "videoCategoryId": category_id,
                    "maxResults": YOUTUBE_MAX_RESULTS,
                    "key": YOUTUBE_API_KEY,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            for video in data.get("items", []):
                snippet = video.get("snippet", {})
                stats = video.get("statistics", {})
                video_id = video.get("id", "")

                view_count = int(stats.get("viewCount", 0))
                like_count = int(stats.get("likeCount", 0))

                items.append({
                    "title": snippet.get("title", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "summary": (
                        f"{snippet.get('channelTitle', '')} | "
                        f"조회수 {view_count:,} | 좋아요 {like_count:,}\n"
                        f"{snippet.get('description', '')[:200]}"
                    ),
                    "source": "YouTube",
                    "type": "youtube",
                    "views": view_count,
                })

        except Exception as e:
            print(f"[YouTube] category {category_id} 수집 실패: {e}")

    # 조회수 높은 순 정렬 후 상위 반환
    items.sort(key=lambda x: x.get("views", 0), reverse=True)
    return items[:YOUTUBE_MAX_RESULTS]
