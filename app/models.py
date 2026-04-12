# models.py — Define o formato dos dados que entram e saem da API.
# Pydantic valida automaticamente; se o dado vier errado, retorna HTTP 422.

from typing import List, Optional
from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    # Corpo da requisição POST /messages
    message: str = Field(..., min_length=1, description="Pergunta do usuário")
    session_id: Optional[str] = Field(default=None, description="ID de sessão opcional")


class SourceItem(BaseModel):
    # Um item de fonte — contém apenas o nome da seção usada
    section: str = Field(..., description="Nome da seção da KB")


class MessageResponse(BaseModel):
    # Corpo da resposta
    answer: str = Field(..., description="Resposta gerada pelo LLM")
    sources: List[SourceItem] = Field(default_factory=list, description="Seções usadas")
