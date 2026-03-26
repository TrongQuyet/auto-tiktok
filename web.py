import asyncio
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile, WebSocket, WebSocketDisconnect
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
    tts_rate: str = "+0%"
    subtitle_style: str = "karaoke"
    transition: str = "fade"
    bgm_style: str = "none"
    sfx_enabled: bool = False
    mode: str = "niche"
    segments: list[str] | None = None
    caption: str | None = None
    hashtags: list[str] | None = None


class BatchRequest(BaseModel):
    niches: list[str] = ["motivation"]
    count: int = 1
    workers: int = 1
    subtitle_style: str = "karaoke"
    tts_rate: str = "+0%"
    transition: str = "fade"
    bgm_style: str = "none"
    sfx_enabled: bool = False
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


@app.delete("/api/videos/{filename}")
async def delete_video(filename: str):
    path = Path("output") / filename
    if not path.exists():
        return {"error": "Video not found"}
    path.unlink()
    logger.info(f"Deleted video: {filename}")
    return {"message": f"Deleted {filename}"}


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

    if req.mode == "prompt" and req.segments:
        asyncio.create_task(_run_prompt_video(req))
        return {"message": "Prompt video started", "segments": len(req.segments)}

    batch_req = BatchRequest(
        niches=[req.niche],
        count=1,
        workers=1,
        upload_to_tiktok=req.upload_to_tiktok,
        tts_voice=req.tts_voice,
        tts_rate=req.tts_rate,
        subtitle_style=req.subtitle_style,
        transition=req.transition,
        bgm_style=req.bgm_style,
        sfx_enabled=req.sfx_enabled,
    )
    asyncio.create_task(_run_batch(batch_req))
    return {"message": "Job started", "niche": req.niche}


@app.post("/api/batch")
async def batch_generate(req: BatchRequest):
    if batch_status["running"]:
        return {"error": "A job is already running"}

    req.count = min(req.count, 20)
    req.workers = min(max(req.workers, 1), 2)

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


# ── Helpers ─────────────────────────────────────────────────────────
def _generate_search_queries(segments: list[str]) -> list[str]:
    """Generate focused English Pexels search queries from Vietnamese segments."""
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source="vi", target="en")

        # Step 1: Detect main subject from all segments
        # Translate first segment to find the main topic
        first_en = translator.translate(segments[0][:100]) or ""
        # Common nouns that are likely the main subject
        nouns = {"dog", "cat", "fish", "bird", "horse", "elephant", "lion", "tiger",
                 "bear", "monkey", "dolphin", "whale", "shark", "snake", "rabbit",
                 "ocean", "space", "earth", "sun", "moon", "star", "mountain",
                 "forest", "river", "city", "car", "phone", "computer", "brain",
                 "heart", "eye", "food", "baby", "child", "tree", "flower"}
        main_subject = ""
        for word in first_en.lower().split():
            clean = word.strip(".,!?()\"'")
            if clean in nouns:
                main_subject = clean
                break

        # Step 2: Generate query for each segment
        skip_words = {
            "the", "a", "an", "is", "are", "was", "were", "of", "to", "in",
            "and", "that", "it", "for", "you", "do", "did", "can", "not",
            "this", "but", "they", "have", "has", "with", "from", "be",
            "been", "being", "will", "would", "could", "should", "may",
            "might", "must", "shall", "about", "also", "just", "like",
            "know", "than", "then", "only", "very", "much", "many",
            "some", "any", "all", "most", "other", "more", "less", "each",
            "every", "both", "few", "how", "what", "when", "where", "why",
            "who", "which", "their", "there", "here", "your", "our", "its",
        }

        queries = []
        for seg in segments:
            en = translator.translate(seg[:100])
            if not en:
                queries.append(main_subject or "nature")
                continue

            # Extract meaningful words (nouns, adjectives)
            words = []
            for w in en.split():
                clean = w.strip(".,!?()\"'").lower()
                if clean not in skip_words and len(clean) > 2 and not clean.isdigit():
                    words.append(clean)

            # Build query: main subject + 1-2 context words
            query_parts = []
            if main_subject and main_subject not in words:
                query_parts.append(main_subject)
            query_parts.extend(words[:2])

            query = " ".join(query_parts[:3]) if query_parts else (main_subject or "nature")
            queries.append(query)

        logger.info(f"Search queries (subject='{main_subject}'): {queries}")
        return queries
    except Exception as e:
        logger.warning(f"Translation failed for search queries: {e}")
        return ["nature landscape"] * len(segments)


# ── Pipeline Runner ─────────────────────────────────────────────────
async def _broadcast(data: dict):
    for ws in ws_clients[:]:
        try:
            await ws.send_json(data)
        except Exception:
            ws_clients.remove(ws)


async def _run_prompt_video(req: GenerateRequest):
    """Create video from user-provided script segments."""
    batch_status.update(
        running=True, total=1, completed=0, failed=0, current_video=1,
        status="Creating video from prompt...", progress=0, video_path=None, error=None,
    )
    await _broadcast({"type": "status", **batch_status})

    try:
        settings = load_settings()
        if req.tts_voice:
            settings.tts_voice = req.tts_voice

        temp_dir = Path("temp/prompt_video")
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Build ContentPlan from user input
        from content.script_generator import ContentPlan

        # Generate English search queries from Vietnamese segments
        search_queries = _generate_search_queries(req.segments)

        content = ContentPlan(
            title="Custom Prompt Video",
            script_segments=req.segments,
            caption=req.caption or "",
            hashtags=req.hashtags or ["#fyp"],
            search_queries=search_queries,
        )

        await _broadcast({
            "type": "content",
            "video_num": 1,
            "title": content.title,
            "segments": content.script_segments,
            "caption": content.caption,
            "hashtags": content.hashtags,
        })

        # Download footage + TTS
        batch_status.update(status="Downloading footage & generating voiceover...", progress=30)
        await _broadcast({"type": "status", **batch_status})

        loop = asyncio.get_event_loop()
        footage_task = loop.run_in_executor(
            None, get_footage_for_segments, content.search_queries, settings.pexels_api_key, temp_dir
        )
        tts_task = generate_voiceover(content.script_segments, settings.tts_voice, temp_dir, rate=req.tts_rate)
        footage_paths, (audio_paths, word_timings) = await asyncio.gather(footage_task, tts_task)

        # Assemble
        batch_status.update(status="Assembling video...", progress=60)
        await _broadcast({"type": "status", **batch_status})
        video_path = await loop.run_in_executor(
            None, assemble_video, content, footage_paths, audio_paths, settings,
            req.subtitle_style, word_timings, req.transition, req.bgm_style, req.sfx_enabled,
        )

        batch_status.update(completed=1, video_path=str(video_path))

        # Upload if requested
        if req.upload_to_tiktok:
            await _run_upload(video_path)

        batch_status.update(running=False, status="Done!", progress=100)
        await _broadcast({"type": "status", **batch_status})

        shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        logger.error(f"Prompt video error: {e}")
        batch_status.update(running=False, status=f"Error: {e}", progress=0, error=str(e))
        await _broadcast({"type": "status", **batch_status})


async def _create_single_video(video_num: int, niche: str, settings, tts_voice: str | None, subtitle_style: str = "karaoke", tts_rate: str = "+0%", transition: str = "fade", bgm_style: str = "none", sfx_enabled: bool = False) -> Path | None:
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
        tts_task = generate_voiceover(content.script_segments, settings.tts_voice, temp_dir, rate=tts_rate)
        footage_paths, (audio_paths, word_timings) = await asyncio.gather(footage_task, tts_task)

        # Step 3: Assemble video
        logger.info(f"[Video {video_num}] Assembling video...")
        video_path = await loop.run_in_executor(
            None, assemble_video, content, footage_paths, audio_paths, settings,
            subtitle_style, word_timings, transition, bgm_style, sfx_enabled,
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

        result = await _create_single_video(
            video_num, niche, settings, req.tts_voice, req.subtitle_style,
            req.tts_rate, req.transition, req.bgm_style, req.sfx_enabled,
        )

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


# ── Subtitle Feature ───────────────────────────────────────────────
subtitle_status = {
    "running": False,
    "status": "idle",
    "progress": 0,
    "output_path": None,
    "error": None,
}


@app.get("/api/subtitle/status")
async def get_subtitle_status():
    return subtitle_status


@app.post("/api/subtitle")
async def add_subtitle(
    video: UploadFile = File(...),
    source_lang: str = Form("zh"),
    target_lang: str = Form("vi"),
    font_size: int = Form(18),
    enable_dub: str = Form("false"),
    dub_voice: str = Form("vi-VN-NamMinhNeural"),
    original_volume: float = Form(0.1),
):
    if subtitle_status["running"]:
        return {"error": "A subtitle job is already running"}

    # Save uploaded file
    upload_dir = Path("temp/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    input_path = upload_dir / video.filename

    with open(input_path, "wb") as f:
        content = await video.read()
        f.write(content)

    logger.info(f"Uploaded video: {video.filename} ({len(content) / 1024 / 1024:.1f} MB)")

    dub = enable_dub.lower() in ("true", "1", "yes")
    asyncio.create_task(_run_subtitle(
        input_path, source_lang, target_lang, font_size,
        dub=dub, dub_voice=dub_voice, original_volume=original_volume,
    ))
    return {"message": "Subtitle job started", "filename": video.filename, "dubbing": dub}


@app.post("/api/subtitle/existing/{filename}")
async def add_subtitle_existing(
    filename: str,
    source_lang: str = "zh",
    target_lang: str = "vi",
    font_size: int = 18,
):
    """Add subtitles to an existing video in output/"""
    if subtitle_status["running"]:
        return {"error": "A subtitle job is already running"}

    path = Path("output") / filename
    if not path.exists():
        return {"error": "Video not found"}

    asyncio.create_task(_run_subtitle(path, source_lang, target_lang, font_size))
    return {"message": "Subtitle job started", "filename": filename}


async def _run_subtitle(
    input_path: Path,
    source_lang: str,
    target_lang: str,
    font_size: int,
    dub: bool = False,
    dub_voice: str = "vi-VN-NamMinhNeural",
    original_volume: float = 0.1,
):
    subtitle_status.update(running=True, status="Starting...", progress=0, output_path=None, error=None)
    await _broadcast({"type": "subtitle_status", **subtitle_status})

    try:
        loop = asyncio.get_event_loop()

        # Step 1: Transcribe
        subtitle_status.update(status="Đang nhận diện giọng nói (Whisper)...", progress=15)
        await _broadcast({"type": "subtitle_status", **subtitle_status})

        from subtitle.transcriber import transcribe
        segments = await loop.run_in_executor(None, transcribe, input_path, source_lang)
        logger.info(f"Transcribed {len(segments)} segments")

        # Step 2: Translate
        subtitle_status.update(status=f"Đang dịch sang tiếng Việt ({len(segments)} đoạn)...", progress=35)
        await _broadcast({"type": "subtitle_status", **subtitle_status})

        from subtitle.translator import translate_segments
        lang_map = {"zh": "zh-CN", "ja": "ja", "ko": "ko", "en": "en"}
        src = lang_map.get(source_lang, source_lang)
        translated = await loop.run_in_executor(None, translate_segments, segments, src, target_lang)

        await _broadcast({
            "type": "subtitle_preview",
            "segments": [{"start": s["start"], "end": s["end"], "original": s.get("original", ""), "text": s["text"]} for s in translated],
        })

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_for_subtitle = input_path

        # Step 3 (optional): Dubbing - generate Vietnamese voiceover
        if dub:
            subtitle_status.update(status=f"Đang lồng tiếng ({len(translated)} đoạn)...", progress=50)
            await _broadcast({"type": "subtitle_status", **subtitle_status})

            from subtitle.dubber import dub_video
            dubbed_path = Path("output") / f"dub_{timestamp}_{input_path.stem}.mp4"
            temp_dir = Path("temp") / f"dub_{timestamp}"
            await dub_video(
                input_path, translated, dub_voice, dubbed_path,
                original_volume=original_volume, temp_dir=temp_dir,
            )
            video_for_subtitle = dubbed_path
            logger.info(f"Dubbing done: {dubbed_path}")

        # Step 4: Burn subtitles
        subtitle_status.update(status="Đang chèn phụ đề vào video...", progress=80)
        await _broadcast({"type": "subtitle_status", **subtitle_status})

        output_path = Path("output") / f"sub_{timestamp}_{input_path.stem}.mp4"
        if dub:
            output_path = Path("output") / f"dubbed_{timestamp}_{input_path.stem}.mp4"

        from subtitle.burner import burn_subtitles
        await loop.run_in_executor(None, burn_subtitles, video_for_subtitle, translated, output_path, font_size)

        # Clean up intermediate dubbed file if subtitle was also burned
        if dub and video_for_subtitle != input_path and video_for_subtitle != output_path:
            video_for_subtitle.unlink(missing_ok=True)

        subtitle_status.update(running=False, status="Hoàn thành!", progress=100, output_path=str(output_path))
        logger.info(f"Done: {output_path}")

    except Exception as e:
        logger.error(f"Subtitle/dub error: {e}")
        subtitle_status.update(running=False, status=f"Lỗi: {e}", progress=0, error=str(e))

    await _broadcast({"type": "subtitle_status", **subtitle_status})

    # Cleanup uploaded file if it was in temp
    if "temp/uploads" in str(input_path):
        input_path.unlink(missing_ok=True)
