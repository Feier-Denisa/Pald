# import os
# import tkinter as tk
# from tkinter import ttk
# from PIL import Image, ImageTk

# from .gui import run as run_main_gui


# class StartScreen(tk.Tk):
#     def __init__(self):
#         super().__init__()

#         self.title("pald • Bine ai venit")
#         self.geometry("900x550")
#         self.minsize(700, 400)

#         # Rădăcina proiectului: folderul care conține `assets` și folderul `pald`
#         project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#         bg_path = os.path.join(project_root, "assets", "background.jpg")

#         # Canvas pentru fundal
#         self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg="#064e3b")  # verde smarald în spate
#         self.canvas.pack(fill="both", expand=True)

#         # === ÎNCĂRCARE POZĂ ORIGINALĂ (fără scalare) ===
#         self._bg_image_orig = None   # imaginea originală PIL
#         self._bg_image_tk = None     # imaginea scalată pentru Tkinter
#         self.canvas_bg = None

#         if os.path.isfile(bg_path):
#             img = Image.open(bg_path).convert("RGB")
#             self._bg_image_orig = img
#         else:
#             print("ATENȚIE: nu am găsit assets/background.jpg")

#         # Frame pentru buton în mijloc
#         self.button_frame = tk.Frame(self.canvas, bg="", padx=20, pady=20)
#         self.button_window = self.canvas.create_window(0, 0, window=self.button_frame)

#         # === STIL BUTON: mai mare, verde ===
#         style = ttk.Style(self)
#         style.theme_use("clam")

#         emerald = "#059669"
#         emerald_dark = "#047857"

#         style.configure(
#             "Start.TButton",
#             font=("Segoe UI", 17, "bold"),
#             padding=18,
#             background=emerald,
#             foreground="white",
#             relief="flat",
#             borderwidth=0,
#         )
#         style.map(
#             "Start.TButton",
#             background=[
#                 ("active", emerald_dark),
#                 ("pressed", emerald_dark),
#             ],
#         )

#         start_button = ttk.Button(
#             self.button_frame,
#             text="Începeți",
#             style="Start.TButton",
#             command=self.on_start_clicked,
#         )
#         start_button.pack()

#         # Nu mai avem text sub buton

#         # Facem un prim layout corect
#         self.update_idletasks()
#         w = self.winfo_width()
#         h = self.winfo_height()
#         self.update_background_image(w, h)
#         self.canvas.coords(self.button_window, w / 2, h / 2)

#         # La orice resize, refacem poziția + (opțional) mărimea imaginii
#         self.bind("<Configure>", self.on_resize)

#     # ---------- BACKGROUND CU RAPORT DE ASPECT PĂSTRAT ----------

#     def update_background_image(self, win_w: int, win_h: int):
#         """
#         Scalează imaginea de fundal astfel încât:
#         - să încapă în fereastră
#         - să-și păstreze proporțiile (fără deformare)
#         - să fie centrată (letterbox)
#         """
#         if not self._bg_image_orig:
#             return

#         if win_w <= 0 or win_h <= 0:
#             return

#         orig_w, orig_h = self._bg_image_orig.size

#         # factorul de scalare = cât de mult putem mări fără să depășim fereastra
#         scale = min(win_w / orig_w, win_h / orig_h)
#         new_w = int(orig_w * scale)
#         new_h = int(orig_h * scale)

#         if new_w <= 0 or new_h <= 0:
#             return

#         img_resized = self._bg_image_orig.resize((new_w, new_h), Image.LANCZOS)
#         self._bg_image_tk = ImageTk.PhotoImage(img_resized)

#         if self.canvas_bg is None:
#             # prima dată: o creăm
#             self.canvas_bg = self.canvas.create_image(
#                 win_w // 2,
#                 win_h // 2,
#                 image=self._bg_image_tk,
#                 anchor="center",
#             )
#         else:
#             # ulterior: doar actualizăm imaginea și poziția
#             self.canvas.itemconfigure(self.canvas_bg, image=self._bg_image_tk)
#             self.canvas.coords(self.canvas_bg, win_w // 2, win_h // 2)

#     # ---------- HANDLERE ----------

#     def on_resize(self, event):
#         """
#         La resize:
#         - recalculăm dimensiunea imaginii (păstrând aspectul)
#         - repoziționăm imaginea și butonul în centru
#         """
#         w = event.width
#         h = event.height

#         self.update_background_image(w, h)
#         self.canvas.coords(self.button_window, w / 2, h / 2)

#     def on_start_clicked(self):
#         self.destroy()
#         run_main_gui()


# def run():
#     app = StartScreen()
#     app.mainloop()


# if __name__ == "__main__":
#     run()
