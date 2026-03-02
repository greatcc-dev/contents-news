# publishers/threads_publisher.py - Threads Graph API 포스팅
import requests
import time
from config import THREADS_USER_ID, THREADS_ACCESS_TOKEN, THREADS_API_BASE


def publish(text: str) -> dict:
    """
    Threads에 텍스트 포스트를 게시합니다.
    1단계: 컨테이너 생성 → 2단계: 게시
    Returns: {"success": bool, "post_id": str | None, "error": str | None}
    """
    if not THREADS_USER_ID or not THREADS_ACCESS_TOKEN:
        raise ValueError("THREADS_USER_ID 또는 THREADS_ACCESS_TOKEN이 설정되지 않았습니다.")

    # 1단계: 미디어 컨테이너 생성
    container_resp = requests.post(
        f"{THREADS_API_BASE}/{THREADS_USER_ID}/threads",
        params={
            "media_type": "TEXT",
            "text": text,
            "access_token": THREADS_ACCESS_TOKEN,
        },
        timeout=15,
    )

    if container_resp.status_code != 200:
        error_msg = container_resp.text
        print(f"[Threads] 컨테이너 생성 실패: {error_msg}")
        return {"success": False, "post_id": None, "error": error_msg}

    creation_id = container_resp.json().get("id")
    if not creation_id:
        return {"success": False, "post_id": None, "error": "creation_id 없음"}

    # 컨테이너 처리 대기 (Threads API 권장)
    time.sleep(3)

    # 2단계: 게시
    publish_resp = requests.post(
        f"{THREADS_API_BASE}/{THREADS_USER_ID}/threads/publish",
        params={
            "creation_id": creation_id,
            "access_token": THREADS_ACCESS_TOKEN,
        },
        timeout=15,
    )

    if publish_resp.status_code != 200:
        error_msg = publish_resp.text
        print(f"[Threads] 게시 실패: {error_msg}")
        return {"success": False, "post_id": None, "error": error_msg}

    post_id = publish_resp.json().get("id")
    print(f"[Threads] 게시 성공! post_id={post_id}")
    return {"success": True, "post_id": post_id, "error": None}
