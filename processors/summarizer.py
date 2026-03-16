# processors/summarizer.py - Claude API로 인사이트 포스트 생성
import os
import anthropic
from datetime import datetime, timezone
from config import CLAUDE_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "state", "last_topics.txt")
CATEGORY_FILE = os.path.join(os.path.dirname(__file__), "..", "state", "last_category.txt")

# 6개 카테고리를 순환하여 매 포스트마다 다른 주제를 강제 지정
CATEGORIES = [
    (
        "platform",
        "플랫폼 정책·알고리즘·수익화 변화\n"
        "  (YouTube·Shorts·TikTok·Threads 등의 최신 정책, 알고리즘 업데이트, 수익 분배 변화)"
    ),
    (
        "production",
        "영상 제작·편집·후반작업 기법이나 트렌드\n"
        "  (촬영 방식, 편집 소프트웨어, 색보정, 사운드, 워크플로우 혁신 등)"
    ),
    (
        "gear",
        "카메라·촬영 장비·신규 기기 소식\n"
        "  (신제품 카메라, 렌즈, 드론, 조명, 마이크, 짐벌 등 크리에이터가 주목할 하드웨어)"
    ),
    (
        "ai",
        "AI가 영상 제작이나 크리에이터 업무를 바꾸는 흐름\n"
        "  (AI 편집 도구, AI 보이스·번역, AI 썸네일·스크립트 생성, AI 카메라 기능 등)"
    ),
    (
        "creator",
        "유명 크리에이터의 동향·전략·성공 사례\n"
        "  (배울 점과 인사이트 위주, 공격적이거나 가십성 내용 없이)"
    ),
    (
        "business",
        "크리에이터 비즈니스·이코노미 트렌드\n"
        "  (수익 구조, 브랜드 딜, 구독 경제, 크리에이터 펀드, 멀티채널 전략 등)"
    ),
    (
        "tax",
        "크리에이터를 위한 세무·재무 실전 가이드\n"
        "  (종합소득세, 부가세, 사업자등록, 경비처리, 해외 수익 신고, 세금 절약 팁 등 크리에이터가 꼭 알아야 할 세무 정보)"
    ),
    (
        "creator_case",
        "국내외 유명 크리에이터에게서 배우는 실전 전략\n"
        "  (MrBeast, 주언규, 침착맨, MKBHD, Casey Neistat 등 성공 크리에이터의 구체적 전략·수치·방법론 분석)"
    ),
]


def _get_time_slot() -> str:
    """UTC 0시 = KST 9시(오전), UTC 9시 = KST 18시(저녁)"""
    return "morning" if datetime.now(timezone.utc).hour < 9 else "evening"


def _load_last_topics() -> str:
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def _load_last_category_index() -> int:
    try:
        with open(CATEGORY_FILE, encoding="utf-8") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return -1


def save_last_topics(text: str):
    """게시 성공 후 호출 - 다음 실행의 중복 방지에 사용"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(text[:400])


def save_last_category(index: int):
    """게시 성공 후 호출 - 다음 실행의 카테고리 순환에 사용"""
    os.makedirs(os.path.dirname(CATEGORY_FILE), exist_ok=True)
    with open(CATEGORY_FILE, "w", encoding="utf-8") as f:
        f.write(str(index))


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


def summarize(items: list[dict]) -> tuple[str, int]:
    """
    수집된 콘텐츠 → 쓰레드 포스트 생성
    Returns: (완성된 포스트 텍스트, 사용된 카테고리 인덱스)
    """
    if not items:
        return "", -1

    if not CLAUDE_API_KEY:
        raise ValueError("CLAUDE_API_KEY가 설정되지 않았습니다.")

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    context = build_context(items)

    time_slot = _get_time_slot()
    last_topics = _load_last_topics()

    # 카테고리 순환: 마지막 인덱스 다음 카테고리 선택
    last_index = _load_last_category_index()
    current_index = (last_index + 1) % len(CATEGORIES)
    category_key, category_desc = CATEGORIES[current_index]

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

    prompt = f"""당신은 영상 제작 경력 15년차 PD입니다.
광고 영상, 방송 콘텐츠, 유튜브 콘텐츠를 두루 거쳤고, 현재는 크리에이터 광고 대행 사업을 운영하는 콘텐츠 비즈니스 실무자입니다.
이론이 아닌 현장에서 몸으로 익힌 인사이트를 나누는 쓰레드(Threads) 계정에 올릴 포스트를 써주세요.

[핵심 독자 - 이 한 사람을 머릿속에 떠올리며 쓸 것]
콘텐츠로 수익을 만들고 싶은 초중급 크리에이터, 또는 콘텐츠 마케팅에 관심 있는 소규모 사업자.
"좋은 콘텐츠를 만들면 사업이 된다"는 걸 알지만 구체적 방법을 찾고 있다.
읽고 나서 "나도 해볼 수 있겠다"는 느낌이 들어야 한다.

[이번 포스트 카테고리 - 반드시 이 카테고리 안에서만 작성할 것]
{category_desc}
이 카테고리에 맞는 참고 콘텐츠를 골라 활용하세요. 소재가 부족하면 이 카테고리에 대한 15년차 PD로서의 인사이트로 보완하세요.

{slot_guide}{avoid_block}

[참고 콘텐츠]
{context}

[글 포맷 - 아래 3가지 중 하나를 랜덤으로 선택하여 작성]

포맷 A "리스트형": 후킹 → 공감 → 핵심 팁 2~3개(①②③) 각 3~5문장 → 마무리
포맷 B "스토리형": 후킹 → 하나의 사례/현상을 깊게 파고드는 에세이식 흐름 → 교훈 → 마무리. 번호 매기기 없이 자연스러운 문단 전개.
포맷 C "한 줄 임팩트형": 짧고 강한 문장들을 줄바꿈으로 나열. 한 문장이 하나의 생각 단위. 마지막에 핵심 메시지 한 방.

어떤 포맷이든 반드시 지킬 것:
- 오프닝 후킹: "이게 무슨 얘기지?" 싶은 반전 도입. 자극적 어그로 금지, 뉴스 요약 금지.
- 마무리: 독자에게 행동 의지를 심는 짧고 강한 클로징.
- 구체성: 숫자·사례·도구명을 반드시 포함.

[작성 규칙]
- 전체 800~1200자 (한국어)
- 이모지 절대 사용 금지
- 해시태그 없음, URL 없음
- 문체: 쓰레드 반말체 — "~했어", "~거든", "~인 거지", "~해봐", "~같아", "~잖아" 형태. 친구한테 얘기하듯이 쓸 것. 존댓말("~해요", "~합니다", "~됩니다") 절대 금지.
- 어투: 겸손하지만 확신에 찬 세미 캐주얼 (주언규 + GaryVee 스타일 — 독자를 가르치려 하지 않고 함께 생각하는 느낌)
- 핵심 인사이트는 충분히 설명: 개념 → 왜 중요한지 → 구체적 예시 → 실행법이나 수치·도구명
- 긍정적 에너지 유지 — 현실을 짚더라도 반드시 해결책과 가능성으로 마무리
- 금지: "유튜브는 끝났다" 류 패배주의 / 크리에이터 비하 / "꾸준함이 답" 류 클리셰 / 흐릿한 마무리
- 금지: 개인 이력·경력 연차·경험담 언급 절대 금지 ("N년 해보니", "광고 업계에 있어보면" 등 1인칭 경력 표현 사용하지 말 것)
- 추상적 문장 하나 뒤에는 반드시 구체적 문장이 따라와야 함
- 팩트체크 필수: 수치·정책·도구명·크리에이터 사례를 언급할 때 참고 콘텐츠에 근거가 있는 것만 사용할 것. 확인 불가능한 수치나 사실은 절대 지어내지 말 것. 불확실하면 "최근 보도에 따르면" 등 출처를 암시하거나, 해당 내용을 빼고 확실한 것만 쓸 것.

포스트만 출력하세요. 설명 없이."""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        temperature=1.0,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip(), current_index
