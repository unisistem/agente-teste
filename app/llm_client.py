import logging
import requests
from app.config import settings

logger = logging.getLogger(__name__)


def call_llm(
    question: str = "",
    context: str = "",
    system_prompt: str = "",
    user_message: str = "",
) -> str:
    """Envia pergunta + contexto ao LLM e retorna o texto da resposta.
    
    Aceita dois formatos de chamada:
      - call_llm(question=..., context=...)        — usado pelo nosso orchestrator
      - call_llm(system_prompt=..., user_message=) — usado pelo orchestrator externo
    """
    # Normaliza os dois formatos para system_prompt + user_prompt
    if not system_prompt:
        system_prompt = (
            "Você é um assistente técnico. "
            "Responda APENAS com base no contexto fornecido. "
            "Se o contexto não contiver informação suficiente, responda exatamente: "
            "'Não encontrei informação suficiente na base para responder essa pergunta.' "
            "Responda em português, de forma clara e concisa. "
            "Não invente informações além do que está no contexto."
        )

    if not user_message:
        user_message = f"Contexto:\n{context}\n\nPergunta: {question}"

    if settings.LLM_PROVIDER.lower() == "ollama":
        return _call_ollama(system_prompt, user_message)
    else:
        return _call_openai_compatible(system_prompt, user_message)


def _call_ollama(system_prompt: str, user_prompt: str) -> str:
    """Chama Ollama via endpoint nativo /api/chat."""
    url = f"{settings.LLM_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.3},
    }
    logger.info("Chamando Ollama: %s", settings.LLM_MODEL)
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json().get("message", {}).get("content", "").strip()


def _call_openai_compatible(system_prompt: str, user_prompt: str) -> str:
    """Chama API compatível com OpenAI via /v1/chat/completions."""
    url = f"{settings.LLM_BASE_URL.rstrip('/')}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.LLM_API_KEY}"} if settings.LLM_API_KEY else {}
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": 0.3,
    }
    logger.info("Chamando LLM: %s", settings.LLM_MODEL)
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()