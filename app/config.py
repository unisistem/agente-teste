"""
Configuração da aplicação.

Carrega variáveis de ambiente do .env e fornece
acesso centralizado às configurações.
"""

import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()


class Settings:
    """Configurações da aplicação via variáveis de ambiente."""

    # Base de conhecimento
    KB_URL = os.getenv(
        "KB_URL",
        "https://raw.githubusercontent.com/igortce/python-agent-challenge/refs/heads/main/python_agent_knowledge_base.md"
    )

    # LLM
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:1.5b")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")

    # Servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))

    # Sessão (TTL em segundos)
    SESSION_TTL = int(os.getenv("SESSION_TTL", "300"))  # 5 minutos
    SESSION_MAX_HISTORY = int(os.getenv("SESSION_MAX_HISTORY", "5"))


settings = Settings()
