from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional, List


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


class ChatMessageRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str
    conversation_turns: int = 0
    valence_history: List[float] = []
    arousal_history: List[float] = []
    meditation_done: bool = False


class ChatMessageResponse(BaseModel):
    reply: str
    conversation_id: int
    message_id: int
    conversation_turns: int
    valence_history: List[float]
    arousal_history: List[float]
    avg_valence: float
    avg_arousal: float
    suggest_meditation: bool
    meditation_done: bool


class ImageGenerateRequest(BaseModel):
    conversation_id: int


class ImageGenerateResponse(BaseModel):
    images: List[str]  # base64 encoded JPEGs


class ImageChatRequest(BaseModel):
    conversation_id: int
    message: str
    image_base64: str


class ImageChatResponse(BaseModel):
    reply: str
    message_id: int


class ConversationSummary(BaseModel):
    id: int
    title: str
    updated_at: str
    message_count: int


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: str
    valence: Optional[float] = None
    arousal: Optional[float] = None
    images: Optional[List[str]] = None
