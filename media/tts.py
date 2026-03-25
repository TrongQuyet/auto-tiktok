import logging
from pathlib import Path

import edge_tts

logger = logging.getLogger(__name__)


async def generate_single(text: str, voice: str, output_path: Path) -> Path:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    logger.info(f"TTS generated: {output_path}")
    return output_path


async def generate_voiceover(segments: list[str], voice: str, temp_dir: Path) -> list[Path]:
    paths = []
    for i, segment in enumerate(segments):
        output_path = temp_dir / f"audio_{i}.mp3"
        await generate_single(segment, voice, output_path)
        paths.append(output_path)
    return paths
