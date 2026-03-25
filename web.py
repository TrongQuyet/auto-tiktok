import asyncio
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import load_settings
from content.script_generator import generate_content
from media.pexels_client import get_footage_for_segments
from media.tts import generate_voiceover
from video.assembler import assemble_video

app = FastAPI(title="Auto TikTok Video Generator")

# Store connected WebSocket clients for real-time logs
ws_clients: list[WebSocket] = []

# Track current job status
current_job = {
    "running": False,
    "status": "idle",
    "progress": 0,
    "video_path": None,
    "error": None,
}


# ── WebSocket log handler ──────────────────────────────────────────
class WebSocketLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        for ws in ws_clients[:]:
            try:
                asyncio.ensure_future(ws.send_json({"type": "log", "message": msg}))
            except Exception:
                pass


ws_handler = WebSocketLogHandler()
ws_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logging.getLogger().addHandler(ws_handler)
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger("web")


# ── Models ──────────────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    niche: str = "motivation"
    upload_to_tiktok: bool = False
    tts_voice: str | None = None


# ── API Endpoints ───────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("templates/index.html")


@app.get("/api/status")
async def get_status():
    return current_job


@app.get("/api/videos")
async def list_videos():
    output_dir = Path("output")
    videos = []
    if output_dir.exists():
        for f in sorted(output_dir.glob("*.mp4"), key=os.path.getmtime, reverse=True):
            stat = f.stat()
            videos.append({
                "name": f.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 1),
                "created": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "url": f"/api/videos/{f.name}",
            })
    return videos


@app.get("/api/videos/{filename}")
async def get_video(filename: str):
    path = Path("output") / filename
    if not path.exists() or not path.is_file():
        return {"error": "Video not found"}
    return FileResponse(path, media_type="video/mp4")


@app.get("/api/voices")
async def list_voices():
    """List available edge-tts voices."""
    try:
        import edge_tts
        voices = await edge_tts.list_voices()
        return [
            {"name": v["ShortName"], "gender": v["Gender"], "locale": v["Locale"]}
            for v in voices
        ]
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    if current_job["running"]:
        return {"error": "A job is already running"}

    asyncio.create_task(_run_pipeline(req))
    return {"message": "Job started", "niche": req.niche}


@app.post("/api/upload/{filename}")
async def upload_to_tiktok(filename: str):
    """Upload an existing video to TikTok."""
    if current_job["running"]:
        return {"error": "A job is already running"}

    path = Path("output") / filename
    if not path.exists():
        return {"error": "Video not found"}

    asyncio.create_task(_run_upload(path))
    return {"message": "Upload started"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_clients.remove(ws)


# ── Pipeline Runner ─────────────────────────────────────────────────
async def _broadcast(data: dict):
    for ws in ws_clients[:]:
        try:
            await ws.send_json(data)
        except Exception:
            ws_clients.remove(ws)


async def _run_pipeline(req: GenerateRequest):
    current_job.update(running=True, status="starting", progress=0, video_path=None, error=None)
    await _broadcast({"type": "status", **current_job})

    try:
        settings = load_settings()
        if req.tts_voice:
            settings.tts_voice = req.tts_voice

        # Clean temp
        if settings.temp_dir.exists():
            shutil.rmtree(settings.temp_dir)
        settings.temp_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Generate content
        current_job.update(status="Generating script with AI...", progress=10)
        await _broadcast({"type": "status", **current_job})
        content = await generate_content(req.niche, settings)
        logger.info(f"Script: {content.title} ({len(content.script_segments)} segments)")

        await _broadcast({
            "type": "content",
            "title": content.title,
            "segments": content.script_segments,
            "caption": content.caption,
            "hashtags": content.hashtags,
        })

        # Step 2: Download footage + TTS
        current_job.update(status="Downloading footage & generating voiceover...", progress=30)
        await _broadcast({"type": "status", **current_job})

        loop = asyncio.get_event_loop()
        footage_task = loop.run_in_executor(
            None, get_footage_for_segments, content.search_queries, settings.pexels_api_key, settings.temp_dir
        )
        tts_task = generate_voiceover(content.script_segments, settings.tts_voice, settings.temp_dir)
        footage_paths, audio_paths = await asyncio.gather(footage_task, tts_task)

        # Step 3: Assemble video
        current_job.update(status="Assembling video...", progress=60)
        await _broadcast({"type": "status", **current_job})
        video_path = await loop.run_in_executor(
            None, assemble_video, content, footage_paths, audio_paths, settings
        )

        current_job.update(status="Video created!", progress=90, video_path=str(video_path))
        await _broadcast({"type": "status", **current_job})

        # Step 4: Upload if requested
        if req.upload_to_tiktok:
            await _run_upload(video_path)
        else:
            current_job.update(status="Done!", progress=100, running=False)
            await _broadcast({"type": "status", **current_job})

        # Cleanup
        shutil.rmtree(settings.temp_dir, ignore_errors=True)
        settings.temp_dir.mkdir(parents=True, exist_ok=True)

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        current_job.update(status=f"Error: {e}", progress=0, running=False, error=str(e))
        await _broadcast({"type": "status", **current_job})


async def _run_upload(video_path: Path):
    current_job.update(running=True, status="Uploading to TikTok...", progress=95)
    await _broadcast({"type": "status", **current_job})

    try:
        from uploader.tiktok import TikTokUploader
        settings = load_settings()
        uploader = TikTokUploader(settings)
        loop = asyncio.get_event_loop()

        def do_upload():
            uploader.start_browser()
            uploader.login()
            return uploader.upload_video(video_path, "", [])

        try:
            success = await loop.run_in_executor(None, do_upload)
            if success:
                current_job.update(status="Posted to TikTok!", progress=100, running=False)
            else:
                current_job.update(status="Upload failed", progress=0, running=False, error="Upload failed")
        finally:
            uploader.close()

    except Exception as e:
        logger.error(f"Upload error: {e}")
        current_job.update(status=f"Upload error: {e}", progress=0, running=False, error=str(e))

    await _broadcast({"type": "status", **current_job})
