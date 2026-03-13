# backend/app/services/meet_summary.py:
import os
import shutil
import asyncio
from datetime import datetime
from typing import Optional
from fastapi import UploadFile

from app.services.summarizer_service import process_file
from app.api.ws_manager import manager

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_uploaded_file(file: UploadFile, calendar_context: Optional[str] = None, client_id: Optional[str] = None, custom_api_key: Optional[str] = None, model_preference: Optional[str] = None):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ts}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)

    if client_id:
        await manager.send_personal_message("Saving file...", client_id)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    loop = asyncio.get_event_loop()
    
    def notify_progress(msg: str):
        if client_id:
            asyncio.run_coroutine_threadsafe(manager.send_personal_message(msg, client_id), loop)

    txt, summary_text, json_path, folder, facts, speaker_summaries = await loop.run_in_executor(
        None, process_file, path, calendar_context, notify_progress, custom_api_key, model_preference
    )

    return {
        "transcript": txt,
        "summary": summary_text,
        "facts": facts,
        "json": json_path,
        "folder": folder,
        "speaker_summaries": speaker_summaries,
    }