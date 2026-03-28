import json
from pathlib import Path
from decouple import config as env


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "db.json"


with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    DB = json.load(f)


PD_PDF_PATH = BASE_DIR/"data"/DB["meta"]["pd_agreement"]["pdf_file"]
IMG_PATH = BASE_DIR / "data" / "cakes"
CAKES = DB["standard_cakes"]
CAKE_OPTIONS = DB["cake_options"]
ORDERS = DB["orders"]
CUSTOMERS = DB["customers"]
PROMO_CODES = DB["promo_codes"]
ADMINS = DB["admins"]
ADMIN_IDS = [admin["telegram_id"] for admin in ADMINS]