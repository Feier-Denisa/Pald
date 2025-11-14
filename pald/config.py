from dotenv import load_dotenv
import os

load_dotenv()  # încarcă automat valorile din fișierul .env

API_KEY = os.getenv("PLANT_ID_API_KEY")

if not API_KEY:
    raise RuntimeError("Cheia de API nu este setată!")
