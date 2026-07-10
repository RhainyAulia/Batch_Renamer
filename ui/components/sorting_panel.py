# ui/components/sorting_panel.py
import tkinter as tk
from tkinter import ttk

class SortingPanel(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text=" 2. Urutan Prioritas File ", padding=8)
        
        self.criteria_options = ["(Tidak ada)", "Nama File", "Ekstensi File", "Ukuran File", "Tanggal Modifikasi", "Tanggal Dibuat"]
        self.criteria_map = {
            "(Tidak ada)": None, "Nama File": "name", "Ekstensi File": "extension",
            "Ukuran File": "size", "Tanggal Modifikasi": "modification_date", "Tanggal Dibuat": "creation_date"
        }
        self._create_widgets()
        
    def _create_widgets(self):
        ttk.Label(self, text="Prioritas 1 (Utama):").pack(anchor="w", pady=(2,0))
        self.cb_p1 = ttk.Combobox(self, values=self.criteria_options[1:], state="readonly")
        self.cb_p1.set("Nama File")
        self.cb_p1.pack(fill="x", pady=2)
        self.cb_p1.bind("<<ComboboxSelected>>", lambda e: self._update_p2_options())
        
        self.var_desc_p1 = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Urutan Terbalik (Z-A / Terbaru)", variable=self.var_desc_p1).pack(anchor="w", pady=(0,5))
        
        ttk.Label(self, text="Prioritas 2 (Jika Prioritas 1 Sama):").pack(anchor="w")
        self.cb_p2 = ttk.Combobox(self, state="readonly")
        self.cb_p2.pack(fill="x", pady=2)
        
        self.var_desc_p2 = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Urutan Terbalik (Z-A / Terbaru)", variable=self.var_desc_p2).pack(anchor="w")
        
        self._update_p2_options()

    def _update_p2_options(self):
        selected_p1 = self.cb_p1.get()
        # Filter kriteria agar yang sudah dipilih di P1 tidak muncul di P2
        filtered_options = [opt for opt in self.criteria_options if opt != selected_p1]
        self.cb_p2.config(values=filtered_options)
        if self.cb_p2.get() == selected_p1 or not self.cb_p2.get():
            self.cb_p2.set("(Tidak ada)")

    def get_sorting_priorities(self):
        p1_key = self.criteria_map[self.cb_p1.get()]
        p2_key = self.criteria_map[self.cb_p2.get()]
        
        priorities = [(p1_key, self.var_desc_p1.get())]
        if p2_key:
            priorities.append((p2_key, self.var_desc_p2.get()))
        return priorities