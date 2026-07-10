# ui/components/folder_selector.py
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

class FolderSelector(ttk.LabelFrame):
    def __init__(self, parent, on_folder_selected):
        super().__init__(parent, text=" 1. Pilih Sumber File ", padding=10)
        self.on_folder_selected = on_folder_selected
        self._create_widgets()
        
    def _create_widgets(self):
        self.btn_browse = ttk.Button(self, text="Buka Folder...", command=self._browse_folder)
        self.btn_browse.pack(side="left", padx=5)
        
        self.lbl_folder_path = ttk.Label(self, text="Belum ada folder yang dipilih.", foreground="gray")
        self.lbl_folder_path.pack(side="left", padx=10, fill="x", expand=True)

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.lbl_folder_path.config(text=str(folder), foreground="black")
            self.on_folder_selected(Path(folder))