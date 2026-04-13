import re
import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

MAX_SECTIONS = 3


def _fetch_kb_content() -> str:
    """Faz GET na KB_URL e retorna o conteúdo Markdown."""
    try:
        response = httpx.get(settings.KB_URL, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as exc:
        logger.error("Falha ao buscar KB: %s", exc)
        raise RuntimeError(f"Não foi possível acessar a KB: {exc}") from exc


def _parse_sections(markdown: str) -> list[dict]:
    """Divide o Markdown em seções usando cabeçalhos ##."""
    sections = []
    pattern = r"^##\s+([^\n]+)\n\s*\n(.*?)(?=^##\s+|\Z)"
    matches = re.findall(pattern, markdown, re.MULTILINE | re.DOTALL)
    for title, content in matches:
        title = title.strip()
        content = content.strip()
        if title and content:
            sections.append({"section": title, "content": content})
    return sections


def _score_section(section: dict, query: str) -> int:
    """Pontua relevância da seção para a query.

    - +10 se o título inteiro aparece na query (muito específico)
    - +3  se algum termo da query aparece no título
    - +1  por cada termo que aparece no conteúdo
    """
    query_terms = [w.lower() for w in query.split() if len(w) >= 3]
    content_lower = section["content"].lower()
    title_lower = section["section"].lower()
    query_lower = query.lower()

    score = sum(1 for term in query_terms if term in content_lower)

    if title_lower in query_lower:
        score += 10
    elif any(term in title_lower for term in query_terms):
        score += 3

    return score


def query_kb(question: str) -> list[dict]:
    """Interface pública da tool: retorna seções relevantes para a pergunta."""
    try:
        markdown = _fetch_kb_content()
    except RuntimeError as exc:
        logger.warning("KB indisponível: %s", exc)
        return []

    sections = _parse_sections(markdown)
    scored = [(s, _score_section(s, question)) for s in sections]
    scored.sort(key=lambda x: x[1], reverse=True)
    relevant = [s for s, score in scored if score >= 2]
    return relevant[:MAX_SECTIONS]
