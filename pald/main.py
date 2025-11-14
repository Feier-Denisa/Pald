import os
from typing import Optional

from .api_client import identify_plant
from .camera import capture_image_from_camera


def _print_identification_result(image_path: str) -> None:
    print("\n=== Trimit poza la Plant.id pentru identificare... ===\n")

    try:
        result = identify_plant(image_path)
    except Exception as e:
        print(f"Eroare la apelul Plant.id: {e}")
        return

    if not result["is_plant"]:
        print("Rezultat: imaginea NU pare să fie o plantă (sau modelul nu e sigur).")
        return

    suggestions = result["suggestions"]
    if not suggestions:
        print("Nu am primit sugestii de la API.")
        return

    print("Rezultat: imaginea pare să fie o plantă.")
    print("Sugestii (cele mai probabile specii):\n")

    for i, s in enumerate(suggestions, start=1):
        name = s["name"]
        prob = s["probability"] * 100.0
        commons = s["common_names"]
        url = s["url"]

        print(f"{i}. {name}  ({prob:.2f}% probabilitate)")
        if commons:
            print(f"   Nume comune: {', '.join(commons)}")
        if url:
            print(f"   Info: {url}")
        print()


def _choose_image_from_gallery() -> Optional[str]:
    path = input("Introdu calea către imagine (ex: C:\\poze\\plant.jpg): ").strip()
    if not path:
        print("Nu ai introdus nicio cale.")
        return None

    if not os.path.isfile(path):
        print("Fișierul nu există sau calea este greșită.")
        return None

    return path


def main():
    while True:
        print("\n========== pald - Plant Identifier ==========")
        print("1. Fă o poză cu camera (webcam)")
        print("2. Alege o poză din galerie (fișier de pe disc)")
        print("3. Ieșire")
        choice = input("Alege o opțiune (1/2/3): ").strip()

        if choice == "1":
            image_path = capture_image_from_camera()
            if image_path:
                _print_identification_result(image_path)
        elif choice == "2":
            image_path = _choose_image_from_gallery()
            if image_path:
                _print_identification_result(image_path)
        elif choice == "3":
            print("La revedere! 🌿")
            break
        else:
            print("Opțiune invalidă. Încearcă din nou.")


if __name__ == "__main__":
    main()
