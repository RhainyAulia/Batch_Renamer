import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path

class FolderSelector(ctk.CTkFrame):
    def __init__(self, parent, on_folder_selected):
        super().__init__(parent)
        self.on_folder_selected = on_folder_selected
        self._create_widgets()
        
    def _create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        
        self.btn_browse = ctk.CTkButton(self, text="Browse Folder...", width=120, command=self._browse_folder)
        self.btn_browse.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.lbl_folder_path = ctk.CTkLabel(self, text="No folder selected yet.", text_color="gray")
        self.lbl_folder_path.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.lbl_folder_path.configure(text=str(folder), text_color=("#1c1c1c", "#e0e0e0"))
            self.on_folder_selected(Path(folder))