"""
API FastAPI - Endpoint POST /messages

Responsabilidade única: receber requisições HTTP,
validar entrada e delegar ao orchestrator.

Regras:
- Valida que 'message' está presente e não é vazio.
- session_id é opcional.
- Retorna JSON no contrato definido pelo desafio.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator
from typing import Optional, List

from app.orchestrator import process_message

logger = logging.getLogger(__name__)

# Cria app FastAPI com documentação OpenAPI automática
app = FastAPI(
    title="Python Agent Challenge",
    description=(
        "Agente com orquestração de fluxo, "
        "tool de conhecimento e LLM."
    ),
    version="1.0.0",
)

# CORS - permite acesso de qualquer origem (teste local e rede)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir interface web estática
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


# --- Modelos de entrada/saída ---

class MessageRequest(BaseModel):
    """Corpo da requisição para POST /messages."""
    message: str
    session_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """Valida que message não é vazio."""
        if not v or not v.strip():
            raise ValueError("message não pode ser vazio")
        return v.strip()


class SourceItem(BaseModel):
    """Uma fonte na lista de sources."""
    section: str


class MessageResponse(BaseModel):
    """Corpo da resposta de POST /messages."""
    answer: str
    sources: List[SourceItem]


# --- Interface Web ---

@app.get("/", include_in_schema=False)
def index():
    """Serve a interface web de teste."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"error": "Interface web não encontrada"}


# --- Endpoints da API ---

@app.post(
    "/messages",
    response_model=MessageResponse,
    summary="Envia uma mensagem e recebe resposta do agente",
)
def post_message(req: MessageRequest):
    """
    Recebe uma mensagem, consulta a base de conhecimento,
    gera resposta com LLM e retorna answer + sources.
    """
    logger.info("Recebida mensagem via POST /messages")

    result = process_message(
        message=req.message,
        session_id=req.session_id,
    )

    return MessageResponse(
        answer=result["answer"],
        sources=[
            SourceItem(section=s["section"])
            for s in result["sources"]
        ],
    )


@app.get("/health", summary="Verifica se a API está no ar")
def health_check():
    """Endpoint simples para verificação de saúde."""
    return {"status": "ok"}
