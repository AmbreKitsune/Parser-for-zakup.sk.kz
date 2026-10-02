import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if getattr(sys, "frozen", False):
    DATA_DIR = Path(sys.executable).resolve().parent / "data"
else:
    DATA_DIR = PROJECT_ROOT / "data"

CONFIG_FILE = DATA_DIR / "config.ini"
CONFIGS_DIR = DATA_DIR / "configs"
LOG_FILE = DATA_DIR / "parser.log"
OUTPUT_DIR = DATA_DIR / "output"
SAVE_ID_FILE = DATA_DIR / "save_id.txt"
