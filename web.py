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

# Track current batch job status
batch_status = {
    "running": False,
    "total": 0,
    "completed": 0,
    "failed": 0,
    "current_video": 0,
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


class BatchRequest(BaseModel):
    niches: list[str] = ["motivation"]
    count: int = 1
    workers: int = 2
    upload_to_tiktok: bool = False
    tts_voice: str | None = None


# ── API Endpoints ───────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("templates/index.html")


@app.get("/api/status")
async def get_status():
    return batch_status


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
    if batch_status["running"]:
        return {"error": "A job is already running"}

    batch_req = BatchRequest(
        niches=[req.niche],
        count=1,
        workers=1,
        upload_to_tiktok=req.upload_to_tiktok,
        tts_voice=req.tts_voice,
    )
    asyncio.create_task(_run_batch(batch_req))
    return {"message": "Job started", "niche": req.niche}


@app.post("/api/batch")
async def batch_generate(req: BatchRequest):
    if batch_status["running"]:
        return {"error": "A job is already running"}

    req.count = min(req.count, 20)
    req.workers = min(max(req.workers, 1), 4)

    asyncio.create_task(_run_batch(req))
    return {
        "message": "Batch started",
        "total": req.count,
        "workers": req.workers,
        "niches": req.niches,
    }


@app.post("/api/stop")
async def stop_batch():
    if not batch_status["running"]:
        return {"error": "No job running"}
    batch_status["running"] = False
    logger.info("Stop requested by user")
    return {"message": "Stopping..."}


@app.post("/api/upload/{filename}")
async def upload_to_tiktok(filename: str):
    """Upload an existing video to TikTok."""
    if batch_status["running"]:
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


async def _create_single_video(video_num: int, niche: str, settings, tts_voice: str | None) -> Path | None:
    """Create a single video. Returns output path or None on failure."""
    if tts_voice:
        settings.tts_voice = tts_voice

    # Use unique temp dir per video to avoid conflicts in parallel mode
    temp_dir = Path(f"temp/worker_{video_num}")
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Step 1: Generate content
        logger.info(f"[Video {video_num}] Generating script for '{niche}'...")
        content = await generate_content(niche, settings)
        logger.info(f"[Video {video_num}] Script: {content.title} ({len(content.script_segments)} segments)")

        await _broadcast({
            "type": "content",
            "video_num": video_num,
            "title": content.title,
            "segments": content.script_segments,
            "caption": content.caption,
            "hashtags": content.hashtags,
        })

        # Step 2: Download footage + TTS in parallel
        logger.info(f"[Video {video_num}] Downloading footage & generating voiceover...")
        loop = asyncio.get_event_loop()
        footage_task = loop.run_in_executor(
            None, get_footage_for_segments, content.search_queries, settings.pexels_api_key, temp_dir
        )
        tts_task = generate_voiceover(content.script_segments, settings.tts_voice, temp_dir)
        footage_paths, audio_paths = await asyncio.gather(footage_task, tts_task)

        # Step 3: Assemble video
        logger.info(f"[Video {video_num}] Assembling video...")
        video_path = await loop.run_in_executor(
            None, assemble_video, content, footage_paths, audio_paths, settings
        )
        logger.info(f"[Video {video_num}] Done! -> {video_path}")
        return video_path

    except Exception as e:
        logger.error(f"[Video {video_num}] Failed: {e}")
        return None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def _worker(semaphore: asyncio.Semaphore, video_num: int, niche: str, settings, req: BatchRequest):
    """Worker that creates one video, respecting the concurrency semaphore."""
    async with semaphore:
        if not batch_status["running"]:
            return

        batch_status["current_video"] = video_num
        batch_status["status"] = f"Creating video {video_num}/{batch_status['total']}..."
        batch_status["progress"] = int((batch_status["completed"] / batch_status["total"]) * 100)
        await _broadcast({"type": "status", **batch_status})

        result = await _create_single_video(video_num, niche, settings, req.tts_voice)

        if result:
            batch_status["completed"] += 1
            batch_status["video_path"] = str(result)

            if req.upload_to_tiktok:
                await _run_upload(result)
        else:
            batch_status["failed"] += 1

        batch_status["progress"] = int((batch_status["completed"] + batch_status["failed"]) / batch_status["total"] * 100)
        await _broadcast({"type": "status", **batch_status})


async def _run_batch(req: BatchRequest):
    total = req.count
    batch_status.update(
        running=True,
        total=total,
        completed=0,
        failed=0,
        current_video=0,
        status=f"Starting batch: {total} videos, {req.workers} workers...",
        progress=0,
        video_path=None,
        error=None,
    )
    await _broadcast({"type": "status", **batch_status})

    settings = load_settings()
    semaphore = asyncio.Semaphore(req.workers)

    # Build list of (video_num, niche) pairs
    # Cycle through provided niches
    tasks = []
    for i in range(total):
        niche = req.niches[i % len(req.niches)]
        video_num = i + 1
        tasks.append(_worker(semaphore, video_num, niche, settings, req))

    logger.info(f"Batch started: {total} videos, {req.workers} parallel workers")

    # Run all workers (semaphore limits concurrency)
    await asyncio.gather(*tasks)

    batch_status.update(
        running=False,
        status=f"Batch complete! {batch_status['completed']} success, {batch_status['failed']} failed",
        progress=100,
    )
    logger.info(f"Batch done: {batch_status['completed']}/{total} succeeded")
    await _broadcast({"type": "status", **batch_status})


async def _run_upload(video_path: Path):
    batch_status.update(status=f"Uploading {video_path.name} to TikTok...")
    await _broadcast({"type": "status", **batch_status})

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
                logger.info(f"Uploaded {video_path.name} to TikTok!")
            else:
                logger.error(f"Upload failed for {video_path.name}")
        finally:
            uploader.close()

    except Exception as e:
        logger.error(f"Upload error: {e}")

    await _broadcast({"type": "status", **batch_status})
