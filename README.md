# YouTube 인사이트 자동 쓰레드 봇

YouTube/크리에이터 관련 콘텐츠를 수집 → Claude API로 인사이트 요약 → Threads에 6시간마다 자동 포스팅

---

## 빠른 시작

### 1. 저장소 준비

```bash
# GitHub에 새 저장소 생성 후
git init
git remote add origin https://github.com/YOUR_USERNAME/youtube-insights-bot.git
git add .
git commit -m "init"
git push -u origin main
```

### 2. API 키 발급

| 키 | 발급 위치 | 필수 여부 |
|----|-----------|-----------|
| `CLAUDE_API_KEY` | https://console.anthropic.com | 필수 |
| `THREADS_USER_ID` | Meta Developer (아래 참고) | 필수 |
| `THREADS_ACCESS_TOKEN` | Meta Developer (아래 참고) | 필수 |
| `NEWS_API_KEY` | https://newsapi.org | 선택 |
| `YOUTUBE_API_KEY` | https://console.cloud.google.com | 선택 |

### 3. GitHub Secrets 설정

`GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret`

위 표의 키를 모두 등록합니다.

### 4. Threads API 설정 방법

1. https://developers.facebook.com 접속 → 앱 생성
2. "Threads API" 제품 추가
3. Instagram 계정 연동
4. 그래프 API 탐색기에서 권한 부여:
   - `threads_basic`
   - `threads_content_publish`
5. 장기 액세스 토큰 발급 (60일짜리 → 갱신 필요)
6. 유저 ID 확인:
   ```
   GET https://graph.threads.net/v1.0/me?access_token=YOUR_TOKEN
   ```

### 5. 테스트 실행

**로컬 테스트 (게시 없음):**
```bash
pip install -r requirements.txt
export CLAUDE_API_KEY="sk-ant-..."
python main.py --dry-run
```

**GitHub Actions 수동 실행:**
- Actions 탭 → `YouTube Insights → Threads` → `Run workflow`
- `dry_run` 체크하면 게시 없이 테스트

---

## 커스터마이징

### RSS 피드 추가/변경
[config.py](config.py)의 `RSS_FEEDS` 리스트 수정

### 키워드 변경
[config.py](config.py)의 `NEWS_KEYWORDS` 수정

### 포스팅 시간 변경
[.github/workflows/post.yml](.github/workflows/post.yml)의 `cron` 수정
- UTC 기준으로 작성 (KST = UTC+9)

---

## 파일 구조

```
├── collectors/
│   ├── rss_collector.py      # RSS 피드 수집
│   ├── news_collector.py     # NewsAPI 수집
│   └── youtube_collector.py  # YouTube Data API 수집
├── processors/
│   └── summarizer.py         # Claude API 인사이트 요약
├── publishers/
│   └── threads_publisher.py  # Threads 게시
├── config.py                 # 설정 (RSS, 키워드 등)
├── main.py                   # 진입점
└── .github/workflows/post.yml # GitHub Actions 스케줄러
```
# contents-news
