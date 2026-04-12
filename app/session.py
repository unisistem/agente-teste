"""
Session Manager - Gerencia memória por session_id.

Responsabilidade única: manter histórico curto por sessão
com TTL (expiração) e limite de mensagens.

Regras:
- Cada session_id é isolado.
- Histórico limitado a SESSION_MAX_HISTORY mensagens.
- Sessão expira após SESSION_TTL segundos sem uso.
- Sem session_id: chamada é independente (sem memória).
"""

import time
import logging
from typing import Dict, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class Session:
    """Representa uma sessão com histórico e expiração."""

    def __init__(
        self,
        max_history: int = settings.SESSION_MAX_HISTORY,
        ttl: int = settings.SESSION_TTL,
    ):
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history
        self.ttl = ttl
        self.last_access = time.time()

    def is_expired(self) -> bool:
        """Verifica se a sessão expirou."""
        return (time.time() - self.last_access) > self.ttl

    def add_message(self, role: str, content: str):
        """Adiciona mensagem ao histórico (com limite)."""
        self.history.append({"role": role, "content": content})
        # Mantém apenas as últimas N mensagens
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        self.last_access = time.time()

    def get_history(self) -> List[Dict[str, str]]:
        """Retorna histórico da sessão."""
        return list(self.history)

    def get_context_string(self) -> str:
        """Retorna histórico como string para contexto."""
        parts = []
        for msg in self.history:
            role = msg.get("role", "user")
            text = msg.get("content", "")
            parts.append(f"{role}: {text}")
        return "\n".join(parts)


class SessionManager:
    """Gerencia múltiplas sessões em memória."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def get_or_create(self, session_id: str) -> Session:
        """
        Retorna sessão existente ou cria nova.
        Remove sessões expiradas automaticamente.
        """
        # Limpa sessões expiradas
        self._cleanup_expired()

        if session_id not in self._sessions:
            self._sessions[session_id] = Session()
            logger.info("Nova sessão criada: %s", session_id)
        else:
            session = self._sessions[session_id]
            if session.is_expired():
                logger.info("Sessão expirada, recriando: %s", session_id)
                self._sessions[session_id] = Session()
            else:
                logger.debug("Sessão existente: %s", session_id)

        return self._sessions[session_id]

    def _cleanup_expired(self):
        """Remove sessões expiradas."""
        expired = [
            sid for sid, s in self._sessions.items()
            if s.is_expired()
        ]
        for sid in expired:
            logger.info("Limpando sessão expirada: %s", sid)
            del self._sessions[sid]


# Instância global (em memória)
session_manager = SessionManager()
