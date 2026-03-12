# config.py - 수집할 RSS, 키워드 등 설정
import os

# ─── API Keys (GitHub Secrets에서 주입) ─────────────────────────────────────
CLAUDE_API_KEY     = os.environ.get("CLAUDE_API_KEY", "")
THREADS_USER_ID    = os.environ.get("THREADS_USER_ID", "")
THREADS_ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN", "")
NEWS_API_KEY       = os.environ.get("NEWS_API_KEY", "")
YOUTUBE_API_KEY    = os.environ.get("YOUTUBE_API_KEY", "")

# ─── RSS 피드 목록 (크리에이터 비즈니스 + 영상제작/장비/AI 특화) ──────────────
RSS_FEEDS = [
    # 크리에이터 비즈니스 / 플랫폼
    "https://www.tubefilter.com/feed/",           # YouTube 전문 미디어 (크리에이터 뉴스)
    "https://blog.youtube/rss/",                  # YouTube 공식 블로그 (정책/기능 업데이트)
    "https://www.socialmediatoday.com/rss/",      # 소셜미디어 플랫폼 트렌드
    "https://digiday.com/feed/",                  # 크리에이터 이코노미 비즈니스
    # 영상 제작 / 편집 / 후반작업
    "https://nofilmschool.com/feed",              # 영상 제작, 촬영 기법, AI 도구
    "https://www.provideocoalition.com/feed/",   # 프로 영상 제작 업계 뉴스
    # 카메라 / 촬영 장비 / 신규 기기
    "https://petapixel.com/feed/",               # 카메라, 촬영 장비, 영상 기어
    "https://www.dpreview.com/feeds/news",       # 카메라 리뷰/신제품 뉴스
    "https://www.engadget.com/rss.xml",          # 신규 기기, 가젯, AI 기술
    # AI + 미디어/크리에이터
    "https://www.theverge.com/rss/index.xml",    # 테크/AI/플랫폼 뉴스
    "https://www.wired.com/feed/rss",            # AI, 기술, 미디어 트렌드
    # 한국어 소스
    "https://www.mediatoday.co.kr/rss/allArticle.xml",  # 미디어오늘 (미디어 산업)
    "https://www.bloter.net/?feed=rss2",                # 블로터 (테크/플랫폼)
    "https://techneedle.com/feed",                      # 테크니들 (글로벌 테크 한국어)
    "https://www.mobiinside.co.kr/feed",                # 모비인사이드 (마케팅/크리에이터)
    "https://it.donga.com/rss/",                        # IT동아 (기기/AI/테크 한국어)
    # 일본어 소스
    "https://ascii.jp/rss.xml",                         # ASCII.jp (테크/유튜버 트렌드)
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml", # ITmedia (테크/미디어)
    "https://digimaga.net/feed",                        # デジマガ (디지털 마케팅)
    # 참고 YouTube 채널 (크리에이터/비즈니스)
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCctXZhXmG-kf3tlIXgVZUlw",  # GaryVee
]

# ─── NewsAPI 검색 키워드 (크리에이터 비즈니스 + 영상제작/장비/AI) ─────────────
NEWS_KEYWORDS = [
    "creator economy",
    "YouTube monetization",
    "YouTube algorithm",
    "influencer marketing",
    "AI video editing",
    "AI content creation tools",
    "camera gear filmmaker",
    "content creator tools",
]

# ─── YouTube Data API 설정 ───────────────────────────────────────────────────
YOUTUBE_REGION = "KR"           # 한국 기준 인기 영상
YOUTUBE_MAX_RESULTS = 5         # 가져올 영상 수
# 카테고리 ID: 22=People&Blogs, 24=Entertainment, 28=Science&Tech, 25=News&Politics
YOUTUBE_CATEGORY_IDS = ["22", "24", "25", "28"]

# ─── 수집 설정 ───────────────────────────────────────────────────────────────
RSS_MAX_ITEMS = 20      # RSS에서 가져올 최대 기사 수 (피드당 3개 × 18개 소스)
NEWS_MAX_ITEMS = 3      # NewsAPI에서 가져올 최대 기사 수

# ─── Claude 설정 ─────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-6"   # 글 품질·지시 준수율 향상
CLAUDE_MAX_TOKENS = 1500

# ─── Threads API ─────────────────────────────────────────────────────────────
THREADS_API_BASE = "https://graph.threads.net/v1.0"
