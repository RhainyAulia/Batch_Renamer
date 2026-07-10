# ui/components/renaming_panel.py
import tkinter as tk
from tkinter import ttk

class RenamingPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
        
    def _create_widgets(self):
        # --- MODUL 3: ANGKA URUT ---
        self.seq_frame = ttk.LabelFrame(self, text=" 3. Modul Angka Urut ", padding=8)
        self.seq_frame.pack(fill="x", pady=5, anchor="n")
        
        self.var_seq_enabled = tk.BooleanVar(value=True)
        cb_enable_seq = ttk.Checkbutton(self.seq_frame, text="Aktifkan Penomoran Berurutan", 
                                        variable=self.var_seq_enabled, command=self._toggle_views)
        cb_enable_seq.pack(anchor="w", pady=(0,5))
        
        self.seq_inner = ttk.Frame(self.seq_frame)
        self.seq_inner.pack(fill="x")
        
        ttk.Label(self.seq_inner, text="Posisi Nomor Urut:").pack(anchor="w")
        self.cb_seq_position = ttk.Combobox(self.seq_inner, values=["Awal Nama", "Akhir Nama"], state="readonly")
        self.cb_seq_position.set("Awal Nama")
        self.cb_seq_position.pack(fill="x", pady=2)
        
        ttk.Label(self.seq_inner, text="Teks Sebelum Angka (Prefix):").pack(anchor="w", pady=(3,0))
        self.ent_prefix = ttk.Entry(self.seq_inner)
        self.ent_prefix.insert(0, "DOC_")
        self.ent_prefix.pack(fill="x", pady=2)
        
        ttk.Label(self.seq_inner, text="Teks Setelah Angka (Suffix):").pack(anchor="w", pady=(3,0))
        self.ent_suffix = ttk.Entry(self.seq_inner)
        self.ent_suffix.pack(fill="x", pady=2)
        
        ttk.Label(self.seq_inner, text="Format Digit Angka:").pack(anchor="w", pady=(3,0))
        self.ent_digits = ttk.Entry(self.seq_inner, width=10)
        self.ent_digits.insert(0, "3")
        self.ent_digits.pack(anchor="w", pady=2)

        # --- MODUL 4: UBAH TEKS NAMA ---
        self.text_frame = ttk.LabelFrame(self, text=" 4. Modul Ubah Teks Nama ", padding=8)
        self.text_frame.pack(fill="x", pady=8, anchor="n")
        
        self.text_inner = ttk.Frame(self.text_frame)
        self.text_inner.pack(fill="x")
        
        self.var_reset_names = tk.BooleanVar(value=False)
        self.cb_reset_names = ttk.Checkbutton(self.text_inner, text="Reset / Ganti Total Nama Asli", 
                                              variable=self.var_reset_names, command=self._toggle_views)
        self.cb_reset_names.pack(anchor="w", pady=(2, 5))
        
        self.lbl_prepend = ttk.Label(self.text_inner, text="Sisipkan di Depan Nama Asli:")
        self.lbl_prepend.pack(anchor="w")
        self.ent_prepend = ttk.Entry(self.text_inner)
        self.ent_prepend.pack(fill="x", pady=2)
        
        self.lbl_append = ttk.Label(self.text_inner, text="Sisipkan di Belakang Nama Asli:")
        self.lbl_append.pack(anchor="w", pady=(3,0))
        self.ent_append = ttk.Entry(self.text_inner)
        self.ent_append.pack(fill="x", pady=2)
        
        self.lbl_replace_t = ttk.Label(self.text_inner, text="Cari Kata Konten:")
        self.lbl_replace_t.pack(anchor="w", pady=(5,0))
        self.ent_replace_target = ttk.Entry(self.text_inner)
        self.ent_replace_target.pack(fill="x", pady=2)
        
        self.lbl_replace_w = ttk.Label(self.text_inner, text="Ganti Menjadi:")
        self.lbl_replace_w.pack(anchor="w", pady=(3,0))
        self.ent_replace_with = ttk.Entry(self.text_inner)
        self.ent_replace_with.pack(fill="x", pady=2)
        
        self._toggle_views()

    def _toggle_views(self):
        state_seq = "normal" if self.var_seq_enabled.get() else "disabled"
        for child in self.seq_inner.winfo_children():
            child.configure(state=state_seq)
                
        state_text = "disabled" if self.var_reset_names.get() else "normal"
        self.ent_prepend.configure(state=state_text)
        self.ent_append.configure(state=state_text)
        self.ent_replace_target.configure(state=state_text)
        self.ent_replace_with.configure(state=state_text)

    def get_config(self):
        return {
            "seq_enabled": self.var_seq_enabled.get(),
            "text_enabled": True,
            "reset_names": self.var_reset_names.get(),
            "seq_position": self.cb_seq_position.get(),
            "prefix": self.ent_prefix.get(),
            "suffix": self.ent_suffix.get(),
            "digits": self.ent_digits.get(),
            "prepend_text": self.ent_prepend.get(),
            "append_text": self.ent_append.get(),
            "replace_target": self.ent_replace_target.get(),
            "replace_replacement": self.ent_replace_with.get()
        }