import os
from pathlib import Path
from git import Repo, exc
from loguru import logger

from src.mdx_converter import generate_mdx_docs
from src.utils import RichCloneProgress, run_process_with_progress

BUILD_DIR = Path("build")
TYPST_DIR = BUILD_DIR / "typst"
ASSETS_DIR = BUILD_DIR / "assets"
OUTPUT_JSON = BUILD_DIR / "output.json"
MDX_PATH = BUILD_DIR / "docs"


def ensure_directories():
    if not ASSETS_DIR.exists():
        logger.info(f"Creating {ASSETS_DIR}")
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    else:
        logger.info(f"Directory {ASSETS_DIR} already exists")
    if not MDX_PATH.exists():
        logger.info(f"Creating {MDX_PATH}")
        MDX_PATH.mkdir(parents=True, exist_ok=True)
    else:
        logger.info(f"Directory {MDX_PATH} already exists")


def get_typst() -> None:
    REPO_URL = "https://github.com/typst/typst.git"
    if os.path.exists(TYPST_DIR):
        logger.success(f"Directory {TYPST_DIR} already exists, skipping")
        return
    try:
        Repo.clone_from(REPO_URL, TYPST_DIR, progress=RichCloneProgress())
    except Exception as e:
        logger.error(f"Failed to clone {REPO_URL}: {e}")
        return
    logger.success(f"Successfully cloned {REPO_URL} to {TYPST_DIR}")


def get_docs_json(force: bool = False) -> Path | None:
    if not force and OUTPUT_JSON.exists():
        logger.success(f"File {OUTPUT_JSON} already exists, skipping")
        return OUTPUT_JSON
    cmd = [
        "cargo", "run", 
        "--package", "typst-docs", 
        "--color", "always", 
        "--", 
        "--assets-dir", ASSETS_DIR, 
        "--out-file", OUTPUT_JSON
    ]

    logger.info(f"Running cargo command: {' '.join(cmd)}")
    return_code = run_process_with_progress(cmd, "Building docs", TYPST_DIR)

    if return_code != 0:
        logger.error(f"Cargo command failed with return code {return_code}")
        exit(1)
    logger.success("Cargo command completed successfully")

    return OUTPUT_JSON
    

def main():
    ensure_directories()
    get_typst()
    json = get_docs_json(force=False)
    if not json:
        logger.error("Failed to get Typst docs json")
        exit(1)
    generate_mdx_docs(json, MDX_PATH)

if __name__ == "__main__":
    main()