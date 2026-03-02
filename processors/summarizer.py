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

    prompt = f"""당신은 유튜브·크리에이터 이코노미를 오래 지켜봐 온 사람입니다.
아래 최신 콘텐츠를 바탕으로 쓰레드(Threads)에 올릴 짧은 사설을 써주세요.

[수집된 콘텐츠]
{context}

[작성 규칙]
- 700자 내외 (한국어)
- 이모지 절대 사용 금지
- 해시태그 없음
- URL 없음
- bullet 형식 없이 문단 형태로 자연스럽게 이어지는 글
- 뉴스를 요약하는 느낌이 아니라, 이 흐름을 보며 느낀 점을 담담하게 풀어쓰는 느낌
- 마치 지인이 SNS에 올린 글처럼 편하고 솔직한 어투

포스트만 출력하세요. 설명 없이."""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip()
