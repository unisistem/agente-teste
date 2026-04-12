"""
Orchestrator - Orquestra o fluxo do agente.

Responsabilidade única: coordenar as etapas do fluxo:
  1. Buscar contexto via KB Tool
  2. Montar prompt com pergunta + contexto
  3. Chamar LLM para gerar resposta
  4. Retornar resposta + fontes

Regras de decisão:
- Sempre chama a KB Tool para buscar contexto.
- Se não encontrar seções relevantes, retorna fallback.
- Se encontrar seções, monta prompt com contexto e chama LLM.
- Fontes (sources) vêm apenas das seções realmente usadas.
"""

import logging
from typing import Dict, List, Any, Optional

from app.kb_tool import search_kb
from app.llm_client import call_llm
from app.session import session_manager

logger = logging.getLogger(__name__)

# Mensagem de fallback quando não há contexto
FALLBACK_ANSWER = (
    "Não encontrei informação suficiente na base para "
    "responder essa pergunta."
)

# System prompt define a personalidade do agente
SYSTEM_PROMPT = (
    "Você é um assistente técnico que responde perguntas "
    "com base exclusivamente no contexto fornecido. "
    "Se o contexto não cobrir a pergunta, diga que não tem "
    "informação suficiente. Seja conciso e direto."
)


def _build_user_message(
    question: str,
    context_sections: List[Dict[str, str]],
    session_context: str = "",
) -> str:
    """
    Monta a mensagem do usuário para o LLM.

    Inclui:
    - Contexto da sessão (se existir)
    - Seções relevantes da KB
    - A pergunta original
    """
    parts = []

    # Contexto da sessão (memória de conversa)
    if session_context:
        parts.append("Histórico da conversa:")
        parts.append(session_context)
        parts.append("")

    # Contexto da KB
    parts.append("Contexto da base de conhecimento:")
    for sec in context_sections:
        parts.append(f"\n## {sec['section']}\n{sec['content']}")
    parts.append("")

    # Pergunta
    parts.append(f"Pergunta: {question}")

    return "\n".join(parts)


def process_message(
    message: str,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fluxo principal do agente.

    Etapas:
    1. Busca contexto na KB
    2. Verifica contexto da sessão (se session_id)
    3. Se sem nenhum contexto → fallback
    4. Monta prompt com contexto disponível
    5. Chama LLM
    6. Retorna resposta + fontes
    """
    logger.info("Processando mensagem: %s", message[:80])

    # --- Etapa 1: Buscar contexto na KB ---
    sections = search_kb(message)

    # --- Etapa 2: Verificar contexto da sessão ---
    session_context = ""
    if session_id:
        session = session_manager.get_or_create(session_id)
        session_context = session.get_context_string()

    # --- Etapa 3: Fallback se sem nenhum contexto ---
    if not sections and not session_context:
        logger.info("Sem contexto suficiente, retornando fallback.")
        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }

    # --- Etapa 4: Montar prompt ---
    user_message = _build_user_message(
        question=message,
        context_sections=sections,
        session_context=session_context,
    )

    # --- Etapa 5: Chamar LLM ---
    answer = call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
    )

    # Salva na sessão (se aplicável)
    if session_id:
        session = session_manager.get_or_create(session_id)
        session.add_message("user", message)
        session.add_message("assistant", answer)

    # --- Etapa 6: Montar resposta ---
    sources = [{"section": sec["section"]} for sec in sections]

    return {
        "answer": answer,
        "sources": sources,
    }
