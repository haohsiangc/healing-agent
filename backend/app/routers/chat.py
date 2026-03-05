from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.models import User, Conversation, Message
from app.models.schemas import (
    ChatMessageRequest, ChatMessageResponse,
    ConversationSummary, MessageOut,
    ImageChatRequest, ImageChatResponse,
)
from app.services.chat_service import ChatService
from app.services.emotion_service import EmotionService

router = APIRouter(prefix="/api/chat", tags=["chat"])
settings = get_settings()

_chat_service: Optional[ChatService] = None
_emotion_service: Optional[EmotionService] = None


def get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(api_key=settings.ANTHROPIC_API_KEY, model=settings.ANTHROPIC_MODEL)
    return _chat_service


def get_emotion_service() -> EmotionService:
    global _emotion_service
    if _emotion_service is None:
        _emotion_service = EmotionService()
    return _emotion_service


@router.post("/message", response_model=ChatMessageResponse)
def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get or create conversation
    if request.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id,
        ).first()
        if not conv:
            raise HTTPException(status_code=404, detail="對話不存在")
    else:
        conv = Conversation(user_id=current_user.id)
        db.add(conv)
        db.flush()

    # Fetch existing history for GPT context
    existing_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in existing_messages]

    # Use EmotionService to just record emotions (if needed) or bypass the hardcoded logic
    # Emotion analysis (we still run this to get scores to save to DB, but we do NOT use its suggest_meditation flag)
    emotion_svc = get_emotion_service()
    avg_valence, avg_arousal, new_valence, new_arousal, new_turns, _ = (
        emotion_svc.analyze(
            text=request.message,
            valence_history=request.valence_history,
            arousal_history=request.arousal_history,
            conversation_turns=request.conversation_turns,
            window=settings.VALENCE_HISTORY_WINDOW,
            trigger_min_turns=settings.EMOTION_TRIGGER_MIN_TURNS,
            arousal_low=settings.AROUSAL_LOW,
            arousal_high=settings.AROUSAL_HIGH,
        )
    )

    # Generate counseling reply via Agent Skills
    chat_svc = get_chat_service()
    skill_result = chat_svc.chat(request.message, history)
    reply = skill_result.message
    agent_suggested_meditation = skill_result.flags.get("suggest_meditation", False)

    # Only set suggest_meditation if the agent suggested it AND the user hasn't already done it
    suggest_meditation = agent_suggested_meditation and not request.meditation_done

    # Persist messages
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=request.message,
        valence=avg_valence,
        arousal=avg_arousal,
    )
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=reply,
    )
    db.add_all([user_msg, assistant_msg])

    # Update conversation title from first message
    if not existing_messages:
        conv.title = request.message[:40] + ("…" if len(request.message) > 40 else "")

    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user_msg)

    return ChatMessageResponse(
        reply=reply,
        conversation_id=conv.id,
        message_id=user_msg.id,
        conversation_turns=new_turns,
        valence_history=new_valence,
        arousal_history=new_arousal,
        avg_valence=avg_valence,
        avg_arousal=avg_arousal,
        suggest_meditation=suggest_meditation,
        meditation_done=request.meditation_done,
    )


@router.post("/image-reflection", response_model=ImageChatResponse)
def chat_about_image(
    request: ImageChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(
        Conversation.id == request.conversation_id,
        Conversation.user_id == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="對話不存在")

    history = [
        {"role": m.role, "content": m.content}
        for m in db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
        .all()
    ]

    chat_svc = get_chat_service()
    reply = chat_svc.chat_about_image(
        user_message=request.message,
        image_base64=request.image_base64,
        conversation_history=history,
    )

    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=f"[圖像聯想] {request.message}",
    )
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=reply,
    )
    db.add_all([user_msg, assistant_msg])
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user_msg)

    return ImageChatResponse(reply=reply, message_id=user_msg.id)


@router.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(50)
        .all()
    )
    return [
        ConversationSummary(
            id=c.id,
            title=c.title,
            updated_at=c.updated_at.isoformat(),
            message_count=len(c.messages),
        )
        for c in convs
    ]


@router.get("/history/{conversation_id}", response_model=list[MessageOut])
def get_history(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="對話不存在")

    return [
        MessageOut(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat(),
            valence=m.valence,
            arousal=m.arousal,
            images=m.images,
        )
        for m in conv.messages
    ]
