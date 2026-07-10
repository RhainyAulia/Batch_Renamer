import customtkinter as ctk

class SortingPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.criteria_options = ["(None)", "File Name", "File Extension", "File Size", "Date Modified", "Date Created"]
        self.criteria_map = {
            "(None)": None, "File Name": "name", "File Extension": "extension",
            "File Size": "size", "Date Modified": "modification_date", "Date Created": "creation_date"
        }
        self._create_widgets()
        
    def _create_widgets(self):
        lbl_title = ctk.CTkLabel(self, text="2. File Sorting Priority", font=("Segoe UI", 12, "bold"))
        lbl_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # --- PRIORITAS 1 ---
        ctk.CTkLabel(self, text="Priority 1 (Primary):", font=("Segoe UI", 11)).pack(anchor="w", padx=10)
        
        self.cb_p1 = ctk.CTkComboBox(self, values=self.criteria_options[1:], state="readonly", command=self._update_p2_options)
        self.cb_p1.set("File Name")
        self.cb_p1.pack(fill="x", padx=10, pady=2)
    
        try:
            self.cb_p1._dropdown_menu.configure(min_width=260)
            self.cb_p1._canvas.bind("<Button-1>", lambda e: self.cb_p1._on_button_press())
        except Exception:
            pass
        
        self.var_desc_p1 = ctk.BooleanVar(value=False)
        self.chk_p1 = ctk.CTkCheckBox(self, text="Reverse Order (Z-A / Newest)", variable=self.var_desc_p1, font=("Segoe UI", 11))
        self.chk_p1.pack(anchor="w", padx=10, pady=(0, 10))
        
        # --- PRIORITAS 2 ---
        ctk.CTkLabel(self, text="Priority 2 (Tie-Breaker):", font=("Segoe UI", 11)).pack(anchor="w", padx=10)
        
        self.cb_p2 = ctk.CTkComboBox(self, state="readonly")
        self.cb_p2.pack(fill="x", padx=10, pady=2)
        
        try:
            self.cb_p2._dropdown_menu.configure(min_width=260)
            self.cb_p2._canvas.bind("<Button-1>", lambda e: self.cb_p2._on_button_press())
        except Exception:
            pass
        
        self.var_desc_p2 = ctk.BooleanVar(value=False)
        self.chk_p2 = ctk.CTkCheckBox(self, text="Reverse Order (Z-A / Newest)", variable=self.var_desc_p2, font=("Segoe UI", 11))
        self.chk_p2.pack(anchor="w", padx=10, pady=(0, 10))
        
        self._update_p2_options(None)

    def _update_p2_options(self, choice):
        selected_p1 = self.cb_p1.get()
        filtered_options = [opt for opt in self.criteria_options if opt != selected_p1]
        self.cb_p2.configure(values=filtered_options)
        if self.cb_p2.get() == selected_p1 or not self.cb_p2.get():
            self.cb_p2.set("(None)")

    def get_sorting_priorities(self):
        p1_key = self.criteria_map[self.cb_p1.get()]
        p2_key = self.criteria_map[self.cb_p2.get()]
        
        priorities = [(p1_key, self.var_desc_p1.get())]
        if p2_key:
            priorities.append((p2_key, self.var_desc_p2.get()))
        return priorities