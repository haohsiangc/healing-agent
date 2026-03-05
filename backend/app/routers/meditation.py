import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import get_settings

router = APIRouter(prefix="/api/meditation", tags=["meditation"])
settings = get_settings()


@router.get("/audio")
def get_meditation_audio():
    path = settings.MEDITATION_AUDIO_PATH
    if not os.path.exists(path):
        raise HTTPException(
            status_code=404,
            detail="冥想音頻文件未找到，請將 meditation_v2.m4a 放置於 backend/static/ 目錄下",
        )
    return FileResponse(path, media_type="audio/mp4", filename="meditation.m4a")
