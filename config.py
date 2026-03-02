# config.py - 수집할 RSS, 키워드 등 설정
import os

# ─── API Keys (GitHub Secrets에서 주입) ─────────────────────────────────────
CLAUDE_API_KEY     = os.environ.get("CLAUDE_API_KEY", "")
THREADS_USER_ID    = os.environ.get("THREADS_USER_ID", "")
THREADS_ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN", "")
NEWS_API_KEY       = os.environ.get("NEWS_API_KEY", "")
YOUTUBE_API_KEY    = os.environ.get("YOUTUBE_API_KEY", "")

# ─── RSS 피드 목록 (YouTube/크리에이터 특화) ────────────────────────────────
RSS_FEEDS = [
    "https://www.tubefilter.com/feed/",           # YouTube 전문 미디어
    "https://blog.youtube/rss/",                  # YouTube 공식 블로그
    "https://www.socialmediatoday.com/rss/",      # 소셜미디어 트렌드
    "https://techcrunch.com/feed/",               # 테크 뉴스
    "https://www.theverge.com/rss/index.xml",     # 테크/크리에이터 뉴스
]

# ─── NewsAPI 검색 키워드 ─────────────────────────────────────────────────────
NEWS_KEYWORDS = [
    "YouTube creator",
    "creator economy",
    "YouTube monetization",
    "YouTuber",
    "YouTube algorithm",
]

# ─── YouTube Data API 설정 ───────────────────────────────────────────────────
YOUTUBE_REGION = "KR"           # 한국 기준 인기 영상
YOUTUBE_MAX_RESULTS = 5         # 가져올 영상 수
# 카테고리 ID: 22=People&Blogs, 24=Entertainment, 28=Science&Tech
YOUTUBE_CATEGORY_IDS = ["22", "24", "28"]

# ─── 수집 설정 ───────────────────────────────────────────────────────────────
RSS_MAX_ITEMS = 5       # RSS에서 가져올 최대 기사 수
NEWS_MAX_ITEMS = 3      # NewsAPI에서 가져올 최대 기사 수

# ─── Claude 설정 ─────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-haiku-4-5-20251001"   # 빠르고 저렴
CLAUDE_MAX_TOKENS = 800

# ─── Threads API ─────────────────────────────────────────────────────────────
THREADS_API_BASE = "https://graph.threads.net/v1.0"
