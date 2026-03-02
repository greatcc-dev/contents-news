# publishers/threads_publisher.py - Threads Graph API 포스팅
import requests
import time
from config import THREADS_USER_ID, THREADS_ACCESS_TOKEN, THREADS_API_BASE

MAX_CHARS = 490  # Threads API 500자 제한 (여유 10자)


def split_text(text: str) -> list[str]:
    """
    텍스트를 MAX_CHARS 단위로 문장 기준으로 분할합니다.
    """
    if len(text) <= MAX_CHARS:
        return [text]

    chunks = []
    remaining = text

    while len(remaining) > MAX_CHARS:
        # MAX_CHARS 이내에서 마지막 문장 끝(. ! ?) 찾기
        chunk = remaining[:MAX_CHARS]
        cut = max(
            chunk.rfind("."),
            chunk.rfind("!"),
            chunk.rfind("?"),
        )
        if cut == -1:
            cut = MAX_CHARS  # 문장 끝 없으면 그냥 자르기
        else:
            cut += 1  # 마침표 포함

        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()

    if remaining:
        chunks.append(remaining)

    return chunks


def _create_container(text: str, reply_to_id: str = None) -> str | None:
    """미디어 컨테이너 생성. reply_to_id 있으면 답글로 생성."""
    params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": THREADS_ACCESS_TOKEN,
    }
    if reply_to_id:
        params["reply_to_id"] = reply_to_id

    resp = requests.post(
        f"{THREADS_API_BASE}/{THREADS_USER_ID}/threads",
        params=params,
        timeout=15,
    )

    if resp.status_code != 200:
        print(f"[Threads] 컨테이너 생성 실패: {resp.text}")
        return None

    return resp.json().get("id")


def _publish_container(creation_id: str) -> str | None:
    """컨테이너를 실제 게시. 게시된 post_id 반환."""
    resp = requests.post(
        f"{THREADS_API_BASE}/{THREADS_USER_ID}/threads/publish",
        params={
            "creation_id": creation_id,
            "access_token": THREADS_ACCESS_TOKEN,
        },
        timeout=15,
    )

    if resp.status_code != 200:
        print(f"[Threads] 게시 실패: {resp.text}")
        return None

    return resp.json().get("id")


def publish(text: str) -> dict:
    """
    Threads에 텍스트 포스트를 게시합니다.
    500자 초과 시 자동으로 이어지는 쓰레드로 분할 게시합니다.
    Returns: {"success": bool, "post_id": str | None, "error": str | None}
    """
    if not THREADS_USER_ID or not THREADS_ACCESS_TOKEN:
        raise ValueError("THREADS_USER_ID 또는 THREADS_ACCESS_TOKEN이 설정되지 않았습니다.")

    chunks = split_text(text)
    print(f"[Threads] 총 {len(chunks)}개 쓰레드로 분할 게시")

    first_post_id = None
    prev_post_id = None

    for i, chunk in enumerate(chunks):
        print(f"[Threads] {i+1}/{len(chunks)} 쓰레드 게시 중... ({len(chunk)}자)")

        creation_id = _create_container(chunk, reply_to_id=prev_post_id)
        if not creation_id:
            return {"success": False, "post_id": first_post_id, "error": f"{i+1}번째 컨테이너 생성 실패"}

        time.sleep(3)  # Threads API 권장 대기

        post_id = _publish_container(creation_id)
        if not post_id:
            return {"success": False, "post_id": first_post_id, "error": f"{i+1}번째 게시 실패"}

        if i == 0:
            first_post_id = post_id

        prev_post_id = post_id
        print(f"[Threads] {i+1}번째 게시 성공! post_id={post_id}")

        if i < len(chunks) - 1:
            time.sleep(2)  # 연속 게시 간격

    return {"success": True, "post_id": first_post_id, "error": None}
