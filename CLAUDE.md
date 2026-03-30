# CLAUDE.md — Auto TikTok Video Generator

## Project Overview

Automated TikTok video generator: AI script → stock footage → TTS voiceover → karaoke subtitles → upload. Backend is FastAPI + Python async. Content is Vietnamese-first.

## Architecture

```
main.py          CLI entry point
web.py           FastAPI server + WebSocket real-time logs
config.py        Settings dataclass (loaded from .env)
content/         Script generation (AI providers + crawlers)
media/           Stock footage clients (Pexels, Pixabay, Coverr) + TTS
video/           Video assembly (MoviePy + FFmpeg) + effects (Ken Burns, karaoke)
uploader/        TikTok upload via Selenium
cloner/          Website cloner feature
templates/       Web UI (single index.html)
```

## Key Rules

### Async
- All I/O must be async. Never use blocking calls inside FastAPI route handlers or async functions.
- Use `asyncio.gather()` for parallel tasks (e.g., TTS + footage download run simultaneously).

### AI Provider
- Routing: `AI_PROVIDER` env var → `openai` | `anthropic` | `gemini`.
- Always handle fallback: if AI call fails → fall back to template library in `content/templates.py`.
- Use retry via `tenacity` decorator for all AI/API calls.

### Video Processing
- MoviePy for scene-level editing; FFmpeg (`ffmpeg` subprocess) for concatenation when memory is a concern.
- Target format: 1080×1920 (9:16 vertical), 30fps, max 60s.
- Ken Burns zoom: 1.08x smooth zoom applied in `video/effects.py`.
- Karaoke subtitles use word-level timestamps from Edge-TTS — do not break this timing data.

### Content & Language
- Scripts are Vietnamese-first. Prompts in `content/prompts.py` target Vietnamese audience.
- When searching stock footage, translate Vietnamese keywords to English before querying APIs.
- Do not hardcode English-only assumptions in search logic.

### File Paths
- Use `pathlib.Path` everywhere. Do not hardcode `/app` (Docker) or Windows paths.
- `OUTPUT_DIR`, `TEMP_DIR`, `CHROME_PROFILE_DIR` come from `.env` via `Settings`.
- Clean `temp/` after each run; never leave orphaned temp files.

### Selenium / TikTok Upload
- Uses `undetected-chromedriver` — do not switch to regular `selenium.webdriver.Chrome`.
- Chrome profile is persisted in `chrome_profile/` to avoid re-login.
- Add explicit waits (`WebDriverWait`) not `time.sleep()` for TikTok UI interactions.
- Upload flow is fragile — always wrap in try/except and log failures clearly.

### Configuration
- All settings come from `.env` via `config.py` `Settings` dataclass. Do not read `os.environ` directly elsewhere.
- Adding a new setting: add to `Settings` dataclass + `.env.example` together.

### Logging
- Use the module-level logger (`logging.getLogger(__name__)`).
- WebSocket broadcast is handled by a custom log handler in `web.py` — standard `logging` calls automatically appear in the UI.
- Do not use `print()` in production code paths.

### Dependencies
- Python 3.11+. Pin major versions in `requirements.txt` (e.g., `moviepy>=1.0.3,<2.0.0`).
- MoviePy must stay `<2.0.0` — API changed in v2.
- Do not add new heavy dependencies (e.g., PyTorch) without justification; Docker image RAM is limited to 4GB.

## Docker

### Chạy dự án
```bash
# Lần đầu hoặc khi thay đổi dependencies/Dockerfile
docker compose up --build

# Các lần sau
docker compose up -d

# Xem log realtime
docker compose logs -f

# Restart để reload code
docker compose restart
```

Web UI: `http://localhost:8000` | noVNC (TikTok login): `http://localhost:6080`

### Khi nào cần build lại?
- **Không cần** khi sửa code Python — toàn bộ source được mount vào container (xem `volumes` trong `docker-compose.yml`). Chỉ cần `docker compose restart`.
- **Cần build lại** (`--build`) khi: thêm/xóa package trong `requirements.txt`, sửa `Dockerfile`, hoặc thêm thư mục mới chưa có trong `volumes`.

## Common Tasks

### Add a new stock footage source
1. Create `media/<source>_client.py` with `search_videos(query, count) -> list[dict]` interface.
2. Register in `web.py` source selection logic.
3. Add API key to `Settings` + `.env.example`.

### Add a new AI provider
1. Add branch in `content/script_generator.py` provider routing.
2. Add client init and `generate_script()` call.
3. Add API key to `Settings` + `.env.example`.

### Add a new video effect
1. Implement in `video/effects.py` as a function taking a MoviePy clip.
2. Wire into `video/assembler.py` scene composition.

## What NOT to do
- Do not use `subprocess` to call Python scripts — keep everything in-process.
- Do not commit `.env`, `chrome_profile/`, `output/`, `temp/` (already in `.gitignore`).
- Do not add type annotations or docstrings to code you did not change.
- Do not wrap working async code in `asyncio.run()` inside an already-running event loop.
