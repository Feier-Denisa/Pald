import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from .api_client import identify_plant
from .camera import capture_image_from_camera
from .config import API_KEY  # ✅ importăm cheia pentru Test API


def format_identification_result(image_path: str) -> str:
    """
    Apelează Plant.id pentru imaginea dată și întoarce un string frumos formatat
    pentru afișare în interfață.
    """
    try:
        result = identify_plant(image_path)
    except Exception as e:
        return f"Eroare la apelul Plant.id:\n{e}"

    lines = []
    lines.append(f"Imagine: {image_path}")
    lines.append("")

    if not result["is_plant"]:
        lines.append("Rezultat: imaginea NU pare să fie o plantă (sau modelul nu e sigur).")
        return "\n".join(lines)

    suggestions = result["suggestions"]
    if not suggestions:
        lines.append("Rezultat: este plantă, dar nu am primit sugestii de specie.")
        return "\n".join(lines)

    lines.append("Rezultat: imaginea pare să fie o plantă.")
    lines.append("Sugestii (cele mai probabile specii):")
    lines.append("")

    for i, s in enumerate(suggestions, start=1):
        name = s["name"]
        prob = s["probability"] * 100.0
        commons = s["common_names"]
        url = s["url"]

        lines.append(f"{i}. {name}  ({prob:.2f}% probabilitate)")
        if commons:
            lines.append(f"   Nume comune: {', '.join(commons)}")
        if url:
            lines.append(f"   Info: {url}")
        lines.append("")

    return "\n".join(lines)


class PaldApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("pald - Plant Identifier")
        self.geometry("700x500")

        # Frame pentru butoane
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.btn_camera = tk.Button(
            button_frame,
            text="📷 Fă poză cu camera",
            command=self.on_take_photo,
            width=25,
        )
        self.btn_camera.grid(row=0, column=0, padx=5)

        self.btn_gallery = tk.Button(
            button_frame,
            text="🖼️ Alege poză din galerie",
            command=self.on_choose_from_gallery,
            width=25,
        )
        self.btn_gallery.grid(row=0, column=1, padx=5)

        # ✅ Nou: buton Test API
        self.btn_test_api = tk.Button(
            button_frame,
            text="🔑 Test API",
            command=self.on_test_api,
            width=25,
        )
        # îl punem pe rândul 1, sub celelalte două butoane
        self.btn_test_api.grid(row=1, column=0, columnspan=2, pady=5)

        # Zona de text pentru rezultate
        self.result_text = ScrolledText(self, wrap=tk.WORD, font=("Consolas", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Label mic jos
        self.status_label = tk.Label(
            self,
            text="Folosește .env cu PLANT_ID_API_KEY pentru cheia de API.",
            anchor="w",
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=(0, 5))

    def set_result_text(self, text: str):
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.configure(state=tk.DISABLED)

    def on_take_photo(self):
        """
        Folosește camera pentru a captura o poză.
        Deschide fereastra OpenCV; aplicația Tkinter va părea "înghețată"
        cât timp e deschisă fereastra camerei, dar este normal.
        """
        self.set_result_text("Pornește camera... Închide fereastra de cameră după ce faci poza.")
        self.update_idletasks()

        image_path = capture_image_from_camera()
        if not image_path:
            self.set_result_text("Captură anulată sau a apărut o problemă la cameră.")
            return

        self.set_result_text("Identificare în curs, te rog așteaptă...")
        self.update_idletasks()

        result_text = format_identification_result(image_path)
        self.set_result_text(result_text)

    def on_choose_from_gallery(self):
        """
        Deschide un dialog pentru a alege o imagine de pe disc.
        """
        filetypes = [
            ("Imagini", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("Toate fișierele", "*.*"),
        ]
        filename = filedialog.askopenfilename(
            title="Alege o imagine cu planta",
            filetypes=filetypes,
        )

        if not filename:
            # utilizatorul a apăsat Cancel
            return

        if not os.path.isfile(filename):
            messagebox.showerror("Eroare", "Fișierul selectat nu există.")
            return

        self.set_result_text("Identificare în curs, te rog așteaptă...")
        self.update_idletasks()

        result_text = format_identification_result(filename)
        self.set_result_text(result_text)

    # ✅ Nou: handler pentru butonul Test API
    def on_test_api(self):
        """
        Verifică dacă cheia API este încărcată din config (.env).
        NU consumă credite, doar confirmă că aplicația vede cheia.
        """
        if not API_KEY:
            messagebox.showerror(
                "Test API",
                "Cheia API nu este setată.\n\n"
                "Verifică fișierul .env:\n"
                "PLANT_ID_API_KEY=... și repornește aplicația.",
            )
            return

        masked_start = API_KEY[:4]
        length = len(API_KEY)

        message = (
            "Cheia API a fost găsită și încărcată din .env.\n\n"
            f"Primele caractere: {masked_start}***\n"
            f"Lungime: {length} caractere\n\n"
            "Asta înseamnă că aplicația poate folosi cheia.\n"
            "Pentru a testa complet, încearcă să identifici o poză.\n"
            "Dacă primești eroare 401/403, cheia este greșită sau expirată."
        )

        messagebox.showinfo("Test API", message)


def run():
    app = PaldApp()
    app.mainloop()


if __name__ == "__main__":
    run()
