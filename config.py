# config.py - 수집할 RSS, 키워드 등 설정
import os

# ─── API Keys (GitHub Secrets에서 주입) ─────────────────────────────────────
CLAUDE_API_KEY     = os.environ.get("CLAUDE_API_KEY", "")
THREADS_USER_ID    = os.environ.get("THREADS_USER_ID", "")
THREADS_ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN", "")
NEWS_API_KEY       = os.environ.get("NEWS_API_KEY", "")
YOUTUBE_API_KEY    = os.environ.get("YOUTUBE_API_KEY", "")

# ─── RSS 피드 목록 (크리에이터 비즈니스 특화) ───────────────────────────────
RSS_FEEDS = [
    # 영어 소스
    "https://www.tubefilter.com/feed/",           # YouTube 전문 미디어
    "https://blog.youtube/rss/",                  # YouTube 공식 블로그 (정책/기능 업데이트)
    "https://www.socialmediatoday.com/rss/",      # 소셜미디어 플랫폼 트렌드
    "https://www.theverge.com/rss/index.xml",     # 테크/플랫폼 뉴스
    "https://digiday.com/feed/",                  # 크리에이터 이코노미 비즈니스
    # 한국어 소스
    "https://www.mediatoday.co.kr/rss/allArticle.xml",  # 미디어오늘 (미디어 산업)
    "https://www.bloter.net/?feed=rss2",                # 블로터 (테크/플랫폼)
    "https://techneedle.com/feed",                      # 테크니들 (글로벌 테크 한국어)
    "https://www.mobiinside.co.kr/feed",                # 모비인사이드 (마케팅/크리에이터)
    # 일본어 소스
    "https://ascii.jp/rss.xml",                         # ASCII.jp (테크/유튜버 트렌드)
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml", # ITmedia (테크/미디어)
    "https://digimaga.net/feed",                        # デジマガ (디지털 마케팅)
]

# ─── NewsAPI 검색 키워드 (크리에이터 비즈니스/산업 중심) ─────────────────────
NEWS_KEYWORDS = [
    "creator economy",
    "YouTube monetization",
    "YouTube algorithm",
    "influencer marketing",
    "content creator business",
]

# ─── YouTube Data API 설정 ───────────────────────────────────────────────────
YOUTUBE_REGION = "KR"           # 한국 기준 인기 영상
YOUTUBE_MAX_RESULTS = 5         # 가져올 영상 수
# 카테고리 ID: 22=People&Blogs, 24=Entertainment, 28=Science&Tech, 25=News&Politics
YOUTUBE_CATEGORY_IDS = ["22", "24", "25", "28"]

# ─── 수집 설정 ───────────────────────────────────────────────────────────────
RSS_MAX_ITEMS = 5       # RSS에서 가져올 최대 기사 수
NEWS_MAX_ITEMS = 3      # NewsAPI에서 가져올 최대 기사 수

# ─── Claude 설정 ─────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-haiku-4-5-20251001"   # 빠르고 저렴
CLAUDE_MAX_TOKENS = 1000

# ─── Threads API ─────────────────────────────────────────────────────────────
THREADS_API_BASE = "https://graph.threads.net/v1.0"
