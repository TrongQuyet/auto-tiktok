import shutil
import zipfile
from pathlib import Path


def package_zip(source_dir: Path, zip_path: Path) -> Path:
    """Create a ZIP archive from the cloned site directory."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in source_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(source_dir))
    return zip_path


def cleanup(directory: Path):
    """Remove a temporary directory."""
    shutil.rmtree(directory, ignore_errors=True)
