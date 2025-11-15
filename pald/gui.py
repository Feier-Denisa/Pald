import os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk

from PIL import Image, ImageTk  # pip install pillow

from .api_client import identify_plant
from .camera import capture_image_from_camera
from .config import API_KEY


# ---------- FORMATĂM REZULTATUL PENTRU TEXT ----------

def format_identification_result_from_data(image_path: str, result: dict) -> str:
    """
    Primește calea imaginii + dictul rezultat de la identify_plant
    și întoarce un text frumos pentru afișare.
    """
    lines = []
    lines.append(f"Imagine: {image_path}")
    lines.append("")

    if not result.get("is_plant"):
        lines.append("Rezultat: imaginea NU pare să fie o plantă (sau modelul nu e sigur).")
        return "\n".join(lines)

    suggestions = result.get("suggestions") or []
    if not suggestions:
        lines.append("Rezultat: este plantă, dar nu am primit sugestii de specie.")
        return "\n".join(lines)

    lines.append("Rezultat: imaginea pare să fie o plantă.")
    lines.append("Sugestii (cele mai probabile specii):")
    lines.append("")

    for i, s in enumerate(suggestions, start=1):
        name = s.get("name")
        prob = float(s.get("probability", 0.0)) * 100.0
        commons = s.get("common_names") or []
        url = s.get("url")

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

        self.title("Pald • Plant Identifier")
        self.geometry("950x600")
        self.minsize(850, 500)

        # Centrare aproximativă pe ecran
        self.update_idletasks()
        w, h = 950, 600
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = int((sw - w) / 2)
        y = int((sh - h) / 3)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # ---------- STIL ----------
        self.configure(bg="#f3f4f6")

        style = ttk.Style(self)
        style.theme_use("clam")

        accent = "#e32b0a"
        accent_hover = "#8e1e0b"

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8,
            relief="flat",
            borderwidth=0,
            foreground="white",
            background=accent,
        )
        style.map(
            "Accent.TButton",
            background=[("active", accent_hover), ("pressed", accent_hover)],
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=8,
            relief="flat",
            borderwidth=0,
            background="white",
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#e5e7eb"), ("pressed", "#e5e7eb")],
        )

        style.configure(
            "Card.TFrame",
            background="white",
            relief="flat",
            borderwidth=0,
        )

        # ---------- LAYOUT PRINCIPAL ----------
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # HEADER
        header = tk.Frame(self, bg="#f3f4f6")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 4))
        header.columnconfigure(0, weight=1)

        title_label = tk.Label(
            header,
            text="PALD • Plant Identifier",
            bg="#f3f4f6",
            fg="#111827",
            font=("Segoe UI", 16, "bold"),
        )
        title_label.grid(row=0, column=0, sticky="w")

        subtitle_label = tk.Label(
            header,
            text="A picture away from knowing all about your plant",
            bg="#f3f4f6",
            fg="#4b5563",
            font=("Segoe UI", 9),
        )
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # ---------- CONTENT ----------
        content = tk.Frame(self, bg="#f3f4f6")
        content.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        # --------- CARD STÂNGA: IMAGINE + BUTOANE ----------
        left_card = ttk.Frame(content, style="Card.TFrame")
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=4)
        left_card.columnconfigure(0, weight=1)

        left_title = tk.Label(
            left_card,
            text="Imagine plantă",
            bg="white",
            fg="#111827",
            font=("Segoe UI", 11, "bold"),
        )
        left_title.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        self.image_frame = tk.Frame(left_card, bg="#f9fafb", bd=1, relief="solid")
        self.image_frame.grid(row=1, column=0, padx=14, pady=(4, 8), sticky="nsew")
        left_card.rowconfigure(1, weight=1)

        self.image_label = tk.Label(
            self.image_frame,
            text="Nicio imagine încă.\nAlege sau fă o poză.",
            bg="#f9fafb",
            fg="#6b7280",
            font=("Segoe UI", 9),
            justify="center",
        )
        self.image_label.pack(expand=True, fill="both")

        self._current_image_tk = None

        buttons_frame = tk.Frame(left_card, bg="white")
        buttons_frame.grid(row=2, column=0, padx=14, pady=(4, 12), sticky="ew")
        buttons_frame.columnconfigure((0, 1), weight=1)

        self.btn_camera = ttk.Button(
            buttons_frame,
            text="📷 Fă poză cu camera",
            command=self.on_take_photo,
            style="Accent.TButton",
        )
        self.btn_camera.grid(row=0, column=0, padx=(0, 4), pady=2, sticky="ew")

        self.btn_gallery = ttk.Button(
            buttons_frame,
            text="🖼️ Alege din galerie",
            command=self.on_choose_from_gallery,
            style="Secondary.TButton",
        )
        self.btn_gallery.grid(row=0, column=1, padx=(4, 0), pady=2, sticky="ew")

        self.btn_test_api = ttk.Button(
            buttons_frame,
            text="🔑 Test API",
            command=self.on_test_api,
            style="Secondary.TButton",
        )
        self.btn_test_api.grid(row=1, column=0, columnspan=2, pady=(6, 0), sticky="ew")

        # ---------- CARD DREAPTA: TEXT + ISTORIC ----------
        right_card = ttk.Frame(content, style="Card.TFrame")
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=4)
        right_card.columnconfigure(0, weight=1)
        right_card.rowconfigure(1, weight=3)
        right_card.rowconfigure(3, weight=2)

        right_title = tk.Label(
            right_card,
            text="Rezultat identificare",
            bg="white",
            fg="#111827",
            font=("Segoe UI", 11, "bold"),
        )
        right_title.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        self.result_text = ScrolledText(
            right_card,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#f9fafb",
            fg="#111827",
            borderwidth=0,
        )
        self.result_text.grid(
            row=1, column=0, sticky="nsew", padx=14, pady=(4, 8)
        )
        self.result_text.configure(state=tk.DISABLED)

        # ---- ISTORIC ----
        history_label = tk.Label(
            right_card,
            text="Istoric identificări (dublu-click pentru a revedea)",
            bg="white",
            fg="#111827",
            font=("Segoe UI", 10, "bold"),
        )
        history_label.grid(row=2, column=0, sticky="w", padx=14, pady=(0, 2))

        history_frame = tk.Frame(right_card, bg="white")
        history_frame.grid(row=3, column=0, sticky="nsew", padx=14, pady=(0, 12))
        history_frame.rowconfigure(0, weight=1)
        history_frame.columnconfigure(0, weight=1)

        self.history_listbox = tk.Listbox(
            history_frame,
            bg="#f9fafb",
            fg="#111827",
            font=("Segoe UI", 9),
            borderwidth=0,
            activestyle="none",
        )
        self.history_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(history_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_listbox.yview)

        # 🔹 aici facem LISTA clicabilă
        self.history_listbox.bind("<Double-1>", self.on_history_double_click)

        # listă internă cu datele fiecărei identificări
        self.history_entries = []

        # ---------- STATUS ----------
        status_bar = tk.Frame(self, bg="#f3f4f6")
        status_bar.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

        self.status_label = tk.Label(
            status_bar,
            # text="Folosește fișierul .env cu PLANT_ID_API_KEY pentru cheia de API.",
            bg="#f3f4f6",
            fg="#6b7280",
            font=("Segoe UI", 8),
            anchor="w",
        )
        self.status_label.pack(fill="x")

    # ------------ UTILS ------------

    def set_result_text(self, text: str):
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.configure(state=tk.DISABLED)

    def show_image_preview(self, image_path: str):
        try:
            img = Image.open(image_path)
            img.thumbnail((350, 350))
            self._current_image_tk = ImageTk.PhotoImage(img)
        except Exception as e:
            self._current_image_tk = None
            self.image_label.config(
                text=f"Nu pot încărca imaginea.\n{e}",
                image="",
            )
            return

        self.image_label.config(image=self._current_image_tk, text="")

    def add_to_history(self, image_path: str, result: dict):
        """
        Adaugă o intrare în panoul de istoric.
        """
        suggestions = result.get("suggestions") or []
        if suggestions:
            top = suggestions[0]
            name = top.get("name", "Necunoscut")
            prob = float(top.get("probability", 0.0)) * 100.0
            main_text = f"{name} ({prob:.1f}%)"
        else:
            main_text = "Fără sugestii"

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        filename = os.path.basename(image_path)

        entry_text = f"[{timestamp}] {main_text}  —  {filename}"
        # cel mai nou sus
        self.history_listbox.insert(0, entry_text)

        self.history_entries.insert(
            0,
            {
                "time": timestamp,
                "image": image_path,
                "summary": main_text,
                "raw": result,
            },
        )

    # ------------ HANDLERE BUTOANE ------------

    def on_take_photo(self):
        self.set_result_text("Pornește camera... Închide fereastra de cameră după ce faci poza.")
        self.update_idletasks()

        image_path = capture_image_from_camera()
        if not image_path:
            self.set_result_text("Captură anulată sau a apărut o problemă la cameră.")
            return

        self.show_image_preview(image_path)

        self.set_result_text("Identificare în curs, te rog așteaptă...")
        self.update_idletasks()

        try:
            result = identify_plant(image_path)
        except Exception as e:
            self.set_result_text(f"Eroare la apelul Plant.id:\n{e}")
            return

        text = format_identification_result_from_data(image_path, result)
        self.set_result_text(text)
        self.add_to_history(image_path, result)

    def on_choose_from_gallery(self):
        filetypes = [
            ("Imagini", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("Toate fișierele", "*.*"),
        ]
        filename = filedialog.askopenfilename(
            title="Alege o imagine cu planta",
            filetypes=filetypes,
        )

        if not filename:
            return

        if not os.path.isfile(filename):
            messagebox.showerror("Eroare", "Fișierul selectat nu există.")
            return

        self.show_image_preview(filename)

        self.set_result_text("Identificare în curs, te rog așteaptă...")
        self.update_idletasks()

        try:
            result = identify_plant(filename)
        except Exception as e:
            self.set_result_text(f"Eroare la apelul Plant.id:\n{e}")
            return

        text = format_identification_result_from_data(filename, result)
        self.set_result_text(text)
        self.add_to_history(filename, result)

    def on_test_api(self):
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

    # ---------- HANDLER DUBLU-CLICK PE ISTORIC ----------

    def on_history_double_click(self, event):
        """
        La dublu-click pe o intrare din istoric:
        - reafișăm poza
        - reafișăm rezultatul complet
        """
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
        else:
            # dacă dintr-un motiv nu e selectat nimic, luăm linia cea mai apropiată de click
            index = self.history_listbox.nearest(event.y)

        if index < 0 or index >= len(self.history_entries):
            return

        entry = self.history_entries[index]
        image_path = entry["image"]
        result = entry["raw"]

        if os.path.isfile(image_path):
            self.show_image_preview(image_path)

        text = format_identification_result_from_data(image_path, result)
        self.set_result_text(text)


def run():
    app = PaldApp()
    app.mainloop()


if __name__ == "__main__":
    run()