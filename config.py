import json
from pathlib import Path
from decouple import config as env


BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = BASE_DIR / "db.json"


with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    DB = json.load(f)


PD_PDF_PATH = BASE_DIR/"data"/DB["meta"]["pd_agreement"]["pdf_file"]
IMG_PATH = BASE_DIR / "data" / "cakes" / cake["image"]
CAKES = DB["standard_cakes"]