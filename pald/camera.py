import cv2
import os
import tempfile
from typing import Optional


def capture_image_from_camera() -> Optional[str]:
    """
    Deschide camera și captează o imagine când utilizatorul apasă SPACE.
    ESC = anulare.

    Returnează calea imaginii salvate sau None dacă utilizatorul renunță.
    """

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Nu s-a putut deschide camera!")
        return None

    print("Camera pornită. Apasă SPACE pentru a face poza, ESC pentru a renunța.")

    img_path = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Nu pot citi frame de la camera.")
            break

        cv2.imshow("pald - Camera", frame)
        key = cv2.waitKey(1) & 0xFF

        # SPACE
        if key == 32:
            # salvăm într-un fișier temporar
            fd, temp_path = tempfile.mkstemp(suffix=".jpg", prefix="pald_")
            os.close(fd)  # nu ne mai trebuie descriptorul, doar calea
            cv2.imwrite(temp_path, frame)
            img_path = temp_path
            print(f"Poză salvată în: {img_path}")
            break

        # ESC
        if key == 27:
            print("Captură anulată de utilizator.")
            break

    cap.release()
    cv2.destroyAllWindows()

    return img_path
