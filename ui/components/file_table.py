import customtkinter as ctk
from tkinter import ttk

class FileTable(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
        
    def _create_widgets(self):
        columns = ("old_name", "new_name", "size", "type", "created_date", "modified_date")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        fieldbackground="#2b2b2b", 
                        foreground="#ffffff",
                        rowheight=26,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading", 
                        background="#3a3a3a", 
                        foreground="#ffffff", 
                        relief="flat",
                        font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[('selected', '#1f538d')])

        self.table = ttk.Treeview(self, columns=columns, show="headings")
        
        self.table.heading("old_name", text="Original Name")
        self.table.heading("new_name", text="New File   Name (Preview)")
        self.table.heading("size", text="Size")
        self.table.heading("type", text="Type")
        self.table.heading("created_date", text="Date Created")
        self.table.heading("modified_date", text="Date Modified")
        
        self.table.column("old_name", width=220, anchor="w")
        self.table.column("new_name", width=220, anchor="w")
        self.table.column("size", width=70, anchor="e")
        self.table.column("type", width=65, anchor="center")
        self.table.column("created_date", width=140, anchor="center")
        self.table.column("modified_date", width=140, anchor="center")
        
        scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        
        self.table.pack(side="left", fill="both", expand=True, padx=(2,0), pady=2)
        scrollbar.pack(side="right", fill="y", padx=(0,2), pady=2)

    def clear(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def insert_file(self, old_name, new_name, size_kb, type, created_date, modified_date):
        self.table.insert("", "end", values=(old_name, new_name, size_kb, type, created_date, modified_date))