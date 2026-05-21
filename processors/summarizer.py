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

[글 구조 - 짧다. 인사이트는 딱 하나만]
이건 짧은 글이야. 욕심내서 여러 얘기 담지 말고, 가장 선명한 인사이트 하나만 골라.
- 시작: "어?" 하고 멈칫하게 만드는 한 줄. 뉴스 요약하듯 시작하지 말 것.
- 가운데: 그 하나를 구체적으로. 숫자나 사례, 도구명 하나라도 박아넣어. 짧게.
- 끝: 억지로 깔끔하게 정리하려 들지 마. 읽고 나서 머리에 남는 한마디로 툭 끊어. 가끔은 여운만 남겨도 좋아.

흐르는 에세이처럼 쓸 때도 있고, 짧은 문장을 줄바꿈으로 툭툭 던질 때도 있어. 그때그때 달라도 돼.
문단은 한두 문장씩 끊어서 줄바꿈해. 쓰레드는 호흡이 짧으니까.

[작성 규칙]
- 전체 300~440자 (한국어). 쓰레드 한 개에 들어가야 해. 절대 길게 쓰지 말 것.
- 이모지 절대 사용 금지. 해시태그 없음, URL 없음.
- 문체: 쓰레드 반말체 — "~했어", "~거든", "~잖아" 형태. 친구한테 톡 보내듯이. 존댓말("~해요", "~합니다", "~됩니다") 절대 금지.
- 사람이 쓴 느낌 (제일 중요):
  · 문장 길이를 들쭉날쭉하게. 툭 끊는 단문 뒤에 좀 긴 문장, 또 단문.
  · 모든 걸 설명하려 들지 마. 독자가 알아서 채울 여백을 남겨.
  · "개념→이유→예시→실행법" 같은 교과서 순서를 맞추려 하지 마. 생각 흐르는 대로.
  · 가끔 혼잣말 같은 한 줄을 껴넣어도 좋아. AI가 쓴 듯 매끈하고 균형 잡힌 글이 제일 안 좋아.
- 위트 한 꼬집 (꼭 넣을 것): 글에 딱 한 군데, 읽다가 피식하게 만드는 대목을 만들어. 무심한 듯 던지는 관찰, 살짝 과장하거나 비튼 표현, 뻔한 걸 새삼스럽게 짚는 한 줄 같은 거. 절제하되 "있는 듯 없는 듯" 수준은 아니고, 읽는 사람이 분명히 알아챌 정도는 돼야 해. 단, 농담·말장난·드립·억지 비유는 금지. 글의 진지함 자체는 유지할 것.
- 어투: 겸손하지만 확신에 찬 느낌. 가르치려 들지 말고 같이 생각하는 톤.
- 톤은 기본적으로 긍정적 — 문제를 짚어도 비관으로 끝내진 마. 단, 억지 희망이나 교훈으로 마무리할 필요는 없어.
- 구체성: 숫자·사례·도구명을 최소 하나는 넣되 짧게.
- 금지: "유튜브는 끝났다" 류 패배주의 / 크리에이터 비하 / "꾸준함이 답" 류 클리셰
- 금지: 개인 이력·경력 연차·경험담 언급 절대 금지 ("N년 해보니", "광고 업계에 있어보면" 등 1인칭 경력 표현 사용하지 말 것)
- 팩트체크 필수: 수치·정책·도구명·크리에이터 사례를 언급할 때 참고 콘텐츠에 근거가 있는 것만 사용할 것. 확인 불가능한 수치나 사실은 절대 지어내지 말 것. 불확실하면 "최근 보도에 따르면" 등 출처를 암시하거나, 해당 내용을 빼고 확실한 것만 쓸 것.

포스트만 출력하세요. 설명 없이."""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        temperature=1.0,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip(), current_index
