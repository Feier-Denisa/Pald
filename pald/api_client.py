import base64
from typing import List, Dict, Any

import requests

from .config import API_KEY


PLANT_ID_ENDPOINT = "https://api.plant.id/v3/identification"


def encode_image_to_base64(image_path: str) -> str:
    """
    Citește o imagine de pe disc și o convertește în string base64 (ASCII),
    format cerut de Plant.id.
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def identify_plant(image_path: str, max_suggestions: int = 3) -> Dict[str, Any]:
    """
    Trimite imaginea la Plant.id și întoarce un rezultat simplificat.

    Returnează un dict cu:
    {
        "is_plant": bool,
        "suggestions": [
            {
                "name": str,
                "probability": float,  # 0..1
                "common_names": List[str],
                "url": str | None
            },
            ...
        ]
    }
    """
    image_b64 = encode_image_to_base64(image_path)
    images = [image_b64]

    # param 'details' -> ce info suplimentar vrem (url, nume comune etc.)
    params = {
        "details": "url,common_names",
    }

    headers = {
        "Api-Key": API_KEY,
    }

    payload = {
        "images": images,
        # poți adăuga și alte opțiuni dacă vrei, de ex.:
        # "classification_level": "species"
    }

    response = requests.post(
        PLANT_ID_ENDPOINT,
        params=params,
        headers=headers,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    # Parsăm răspunsul într-o formă mai ușor de folosit
    result = data.get("result", {})
    is_plant = bool(result.get("is_plant", {}).get("binary", False))

    suggestions_raw = (
        result.get("classification", {}).get("suggestions", []) or []
    )

    suggestions = []
    for suggestion in suggestions_raw[:max_suggestions]:
        details = suggestion.get("details", {}) or {}
        suggestions.append(
            {
                "name": suggestion.get("name"),
                "probability": float(suggestion.get("probability", 0.0)),
                "common_names": details.get("common_names", []) or [],
                "url": details.get("url"),
            }
        )

    return {
        "is_plant": is_plant,
        "suggestions": suggestions,
    }