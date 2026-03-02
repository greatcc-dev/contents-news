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

    prompt = f"""당신은 유튜브·크리에이터 이코노미 전문 콘텐츠 큐레이터입니다.
아래 최신 콘텐츠를 분석해 쓰레드(Threads) SNS에 올릴 인사이트 포스트를 작성하세요.

[수집된 콘텐츠]
{context}

[작성 규칙]
- 전체 500자 이내 (한국어)
- 핵심 인사이트 2~3가지를 이모지와 함께 bullet로 정리
- 마지막에 핵심 메시지 1문장 (✨로 시작)
- 출처 URL 1개 (가장 중요한 것만)
- 해시태그 3~5개로 마무리 (#유튜브 #크리에이터이코노미 등)
- 자연스럽고 읽기 쉬운 구어체

포스트만 출력하세요. 설명 없이."""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip()
