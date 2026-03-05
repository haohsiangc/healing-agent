from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.models import User, Conversation, Message
from app.models.schemas import ImageGenerateRequest, ImageGenerateResponse
from app.services.generation_service import GenerationService
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/image", tags=["image"])
settings = get_settings()

_gen_service: Optional[GenerationService] = None
_chat_service: Optional[ChatService] = None


def get_gen_service() -> GenerationService:
    global _gen_service
    if _gen_service is None:
        _gen_service = GenerationService(
            mock=settings.MOCK_IMAGE_GENERATION,
            lora_path=settings.LORA_PATH,
            hf_token=settings.HF_TOKEN,
        )
    return _gen_service


def get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(api_key=settings.ANTHROPIC_API_KEY, model=settings.ANTHROPIC_MODEL)
    return _chat_service


@router.post("/generate", response_model=ImageGenerateResponse)
def generate_images(
    request: ImageGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(
        Conversation.id == request.conversation_id,
        Conversation.user_id == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="對話不存在")

    # Build conversation text for prompt
    user_messages = [
        m.content for m in conv.messages if m.role == "user"
    ]
    combined_text = " ".join(user_messages)

    # Translate to English image prompt
    chat_svc = get_chat_service()
    try:
        english_prompt = chat_svc.translate_to_image_prompt(combined_text[:1000])
    except Exception:
        english_prompt = "abstract healing art, warm colors, peaceful"

    gen_svc = get_gen_service()
    images = gen_svc.generate(english_prompt, num_images=4)

    # Persist image attachments to a system message
    system_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content="[已生成療癒圖像]",
        images=images,
    )
    db.add(system_msg)
    db.commit()

    return ImageGenerateResponse(images=images)
