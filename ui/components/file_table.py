# ui/components/file_table.py
import tkinter as tk
from tkinter import ttk

class FileTable(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
        
    def _create_widgets(self):
        columns = ("old_name", "new_name", "size", "type", "created_date", "modified_date")
        self.table = ttk.Treeview(self, columns=columns, show="headings")
        
        self.table.heading("old_name", text="Nama File Asli")
        self.table.heading("new_name", text="Nama File Baru (Preview)")
        self.table.heading("size", text="Ukuran")
        self.table.heading("type", text="Ekstensi")
        self.table.heading("created_date", text="Tanggal Dibuat")
        self.table.heading("modified_date", text="Tanggal Modifikasi")
        
        self.table.column("old_name", width=220, anchor="w")
        self.table.column("new_name", width=220, anchor="w")
        self.table.column("size", width=70, anchor="e")
        self.table.column("type", width=65, anchor="center")
        self.table.column("created_date", width=140, anchor="center")
        self.table.column("modified_date", width=140, anchor="center")
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def clear(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def insert_file(self, old_name, new_name, size_kb, ext, created_date, modified_date):
        self.table.insert("", "end", values=(old_name, new_name, size_kb, ext, created_date, modified_date))