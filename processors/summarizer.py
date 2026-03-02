# processors/summarizer.py - Claude API로 인사이트 포스트 생성
import anthropic
from config import CLAUDE_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS


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

    prompt = f"""당신은 유튜브와 크리에이터 이코노미를 수년간 직접 경험하고 관찰해온 사람입니다.
크리에이터를 막 시작하려는 사람이나 크리에이터 관련 사업을 하는 사람들이 당신의 글을 읽습니다.
아래 최신 콘텐츠를 참고해서 쓰레드(Threads)에 올릴 사설을 써주세요.

[참고 콘텐츠]
{context}

[글 구조 - 반드시 이 순서로]
1. 후킹 (2~3문장): 독자가 "어, 이게 무슨 말이지?" 하고 멈추게 만드는 문장. 질문이나 반전, 역설적 사실로 시작. 뉴스 요약 금지.
2. 본문 (3~4문장): 지금 실제로 무슨 일이 벌어지고 있는지 핵심만 담백하게. 수집된 콘텐츠를 바탕으로 하되 당신의 해석과 분석을 자유롭게 덧붙일 것.
3. 실용 인사이트 (2~3문장): 이걸 읽는 사람이 지금 당장 어떻게 활용하거나 대비할 수 있는지. 뜬구름 잡는 말 금지, 구체적으로.

[작성 규칙]
- 전체 450자 이내 (한국어) - Threads API 500자 제한 엄수, 반드시 지킬 것
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

    text = message.content[0].text.strip()
    # Threads API 500자 제한 안전장치
    if len(text) > 490:
        text = text[:490].rsplit(".", 1)[0] + "."
    return text
