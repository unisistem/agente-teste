import logging
from fastapi import APIRouter, HTTPException
from app.models import MessageRequest, MessageResponse, SourceItem
from app.orchestrator import process_message

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/messages", response_model=MessageResponse)
async def post_message(request: MessageRequest) -> MessageResponse:
    logger.info("POST /messages | session=%s | msg=%.80s",
                request.session_id or "none", request.message)
    try:
        result = process_message(
            message=request.message,
            session_id=request.session_id,
        )
        return MessageResponse(
            answer=result["answer"],
            sources=[SourceItem(section=s["section"]) for s in result["sources"]],
        )
    except Exception as exc:
        logger.exception("Erro inesperado: %s", exc)
        raise HTTPException(status_code=500, detail="Erro interno.") from exc