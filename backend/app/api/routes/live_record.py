import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import assemblyai as aai
from app.core.config import settings

router = APIRouter(prefix="/ws", tags=["Live Record"])

logger = logging.getLogger(__name__)

@router.websocket("/live-record")
async def live_record_websocket(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_event_loop()

    # Callback for when transcriber receives data
    def on_data(transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        payload = {
            "type": "partial" if isinstance(transcript, aai.RealtimePartialTranscript) else "final",
            "text": transcript.text
        }
        
        # Schedule the coroutine in the main event loop
        asyncio.run_coroutine_threadsafe(websocket.send_json(payload), loop)

    def on_error(error: aai.RealtimeError):
        logger.error(f"AssemblyAI Error: {error}")
        payload = {"type": "error", "message": str(error)}
        asyncio.run_coroutine_threadsafe(websocket.send_json(payload), loop)

    def on_open(session_opened: aai.RealtimeSessionOpened):
        logger.info(f"AssemblyAI Session opened: {session_opened.session_id}")
        payload = {"type": "info", "message": "Ready to transcribe"}
        asyncio.run_coroutine_threadsafe(websocket.send_json(payload), loop)

    def on_close():
        logger.info("AssemblyAI Session closed")
        payload = {"type": "info", "message": "Session closed"}
        asyncio.run_coroutine_threadsafe(websocket.send_json(payload), loop)

    # Initialize transcriber
    transcriber = aai.RealtimeTranscriber(
        on_data=on_data,
        on_error=on_error,
        on_open=on_open,
        on_close=on_close,
        sample_rate=16000 # Typical for MediaRecorder audio blocks
    )

    try:
        # Start the transcriber connection
        transcriber.connect()
        
        while True:
            # We expect audio bytes from the client
            message = await websocket.receive()
            
            if "bytes" in message:
                audio_data = message["bytes"]
                transcriber.stream(audio_data)
            elif "text" in message:
                data = json.loads(message["text"])
                if data.get("type") == "stop":
                    break

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in Live Record WS: {e}")
    finally:
        # Clean up
        try:
            transcriber.close()
        except:
            pass
        
        try:
            await websocket.close()
        except:
            pass
