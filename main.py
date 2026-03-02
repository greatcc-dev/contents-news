#!/usr/bin/env python3
"""
YouTube 인사이트 자동 쓰레드 포스팅 봇
실행: python main.py          → 수집 + 요약 + 쓰레드 게시
실행: python main.py --dry-run → 게시 없이 결과만 출력 (테스트용)
"""
import sys
import concurrent.futures

from collectors import rss_collector, news_collector, youtube_collector
from processors import summarizer
from publishers import threads_publisher


def collect_all() -> list[dict]:
    """3개 수집기를 병렬 실행"""
    print("=" * 50)
    print("[수집] RSS / News / YouTube 병렬 수집 시작")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(rss_collector.collect): "RSS",
            executor.submit(news_collector.collect): "News",
            executor.submit(youtube_collector.collect): "YouTube",
        }

        all_items = []
        for future, name in futures.items():
            try:
                items = future.result(timeout=30)
                print(f"[{name}] {len(items)}개 수집")
                all_items.extend(items)
            except Exception as e:
                print(f"[{name}] 오류: {e}")

    print(f"[수집] 총 {len(all_items)}개 항목 수집 완료")
    return all_items


def main():
    dry_run = "--dry-run" in sys.argv

    # 1. 콘텐츠 수집
    items = collect_all()

    if not items:
        print("[종료] 수집된 콘텐츠가 없습니다.")
        sys.exit(1)

    # 2. Claude API로 인사이트 포스트 생성
    print("\n[요약] Claude API로 인사이트 포스트 생성 중...")
    try:
        post_text = summarizer.summarize(items)
    except Exception as e:
        print(f"[요약] 실패: {e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("[생성된 포스트]")
    print(post_text)
    print("=" * 50)

    # 3. Threads 게시 (dry-run이면 건너뜀)
    if dry_run:
        print("\n[DRY-RUN] 실제 게시는 건너뜁니다.")
        return

    print("\n[게시] Threads에 포스팅 중...")
    try:
        result = threads_publisher.publish(post_text)
        if result["success"]:
            print(f"[완료] 게시 성공! post_id={result['post_id']}")
        else:
            print(f"[실패] {result['error']}")
            sys.exit(1)
    except Exception as e:
        print(f"[게시] 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
