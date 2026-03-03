# processors/summarizer.py - Claude API로 인사이트 포스트 생성
import os
import anthropic
from datetime import datetime, timezone
from config import CLAUDE_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "state", "last_topics.txt")


def _get_time_slot() -> str:
    """UTC 0시 = KST 9시(오전), UTC 9시 = KST 18시(저녁)"""
    return "morning" if datetime.now(timezone.utc).hour < 9 else "evening"


def _load_last_topics() -> str:
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def save_last_topics(text: str):
    """게시 성공 후 호출 - 다음 실행의 중복 방지에 사용"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(text[:400])


def build_context(items: list[dict]) -> str:
    """수집된 아이템을 Claude 프롬프트용 텍스트로 변환"""
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] [{item['type'].upper()}] {item['source']}")
        lines.append(f"제목: {item['title']}")
        if item.get("summary"):
            lines.append(f"내용: {item['summary']}")
        lines.append(f"URL: {item['url']}")
        lines.append("")
    return "\n".join(lines)


def summarize(items: list[dict]) -> str:
    """
    수집된 콘텐츠 → 쓰레드 포스트 생성
    Returns: 완성된 포스트 텍스트 (500자 내외)
    """
    if not items:
        return ""

    if not CLAUDE_API_KEY:
        raise ValueError("CLAUDE_API_KEY가 설정되지 않았습니다.")

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    context = build_context(items)

    time_slot = _get_time_slot()
    last_topics = _load_last_topics()

    if time_slot == "morning":
        slot_guide = (
            "오전 발행 포스트입니다. 독자가 하루를 시작하며 "
            "\"오늘 이것만 알면 된다\"고 느낄 최신 트렌드나 새로운 변화에 집중하세요. "
            "후킹은 오늘 눈 뜨자마자 들어야 할 정보처럼 긴박하게."
        )
    else:
        slot_guide = (
            "저녁 발행 포스트입니다. 독자가 하루를 마치며 "
            "\"내일 바로 써먹어야겠다\"고 느낄 실전 인사이트나 행동 지침에 집중하세요. "
            "후킹은 하루를 돌아보며 한 가지 사실이 달리 보이게 만드는 관점으로."
        )

    avoid_block = ""
    if last_topics:
        avoid_block = (
            f"\n\n[이전 포스트 내용 요약 - 같은 주제·논점·사례는 반드시 피할 것]\n{last_topics}"
        )

    prompt = f"""당신은 유튜브와 크리에이터 이코노미를 수년간 직접 경험하고 관찰해온 사람입니다.
크리에이터를 막 시작하려는 사람이나 크리에이터 관련 사업을 하는 사람들이 당신의 글을 읽습니다.
아래 최신 콘텐츠를 참고해서 쓰레드(Threads)에 올릴 사설을 써주세요.

{slot_guide}{avoid_block}

[참고 콘텐츠]
{context}

[글 구조 - 반드시 이 순서로]
1. 후킹 (2~3문장): 독자가 "어, 이게 무슨 말이지?" 하고 멈추게 만드는 문장. 질문이나 반전, 역설적 사실로 시작. 뉴스 요약 금지.
2. 본문 (3~4문장): 지금 실제로 무슨 일이 벌어지고 있는지 핵심만 담백하게. 수집된 콘텐츠를 바탕으로 하되 당신의 해석과 분석을 자유롭게 덧붙일 것.
3. 실용 인사이트 (2~3문장): 이걸 읽는 사람이 지금 당장 어떻게 활용하거나 대비할 수 있는지. 뜬구름 잡는 말 금지, 구체적으로.

[작성 규칙]
- 전체 800~1200자 (한국어) - 500자 초과 시 자동으로 쓰레드 분할 게시됨
- 이모지 절대 사용 금지
- 해시태그 없음, URL 없음
- bullet 없이 문단으로
- 특정 크리에이터 개인 이야기나 가십 제외
- 마치 업계를 잘 아는 지인이 솔직하게 털어놓는 어투

포스트만 출력하세요. 설명 없이."""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        temperature=1.0,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip()
