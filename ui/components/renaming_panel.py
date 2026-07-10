# ui/components/renaming_panel.py
import customtkinter as ctk

class RenamingPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent") 
        self._create_widgets()
        
    def _create_widgets(self):
        # --- MODULE 3: SEQUENTIAL NUMBER ---
        self.seq_frame = ctk.CTkFrame(self)
        self.seq_frame.pack(fill="x", pady=(0, 10), anchor="n")
        
        lbl_seq_title = ctk.CTkLabel(self.seq_frame, text="3. Sequential Number Module", font=("Segoe UI", 12, "bold"))
        lbl_seq_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.var_seq_enabled = ctk.BooleanVar(value=True)
        self.cb_enable_seq = ctk.CTkCheckBox(self.seq_frame, text="Enable Sequential Numbering", 
                                            variable=self.var_seq_enabled, command=self._toggle_views, font=("Segoe UI", 11))
        self.cb_enable_seq.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.seq_inner = ctk.CTkFrame(self.seq_frame, fg_color="transparent")
        self.seq_inner.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(self.seq_inner, text="Number Position:", font=("Segoe UI", 11)).pack(anchor="w")
        self.cb_seq_position = ctk.CTkComboBox(self.seq_inner, values=["Start of Name", "End of Name"], state="readonly")
        self.cb_seq_position.set("Start of Name")
        self.cb_seq_position.pack(fill="x", pady=2)
        
        try:
            self.cb_seq_position._dropdown_menu.configure(min_width=260)
            self.cb_seq_position._entry.bind("<Button-1>", lambda e: self.cb_seq_position._on_button_press())
            self.cb_seq_position._canvas.bind("<Button-1>", lambda e: self.cb_seq_position._on_button_press())
        except Exception:
            pass
        
        ctk.CTkLabel(self.seq_inner, text="Text Before Number (Prefix):", font=("Segoe UI", 11)).pack(anchor="w", pady=(3, 0))
        self.ent_prefix = ctk.CTkEntry(self.seq_inner)
        self.ent_prefix.insert(0, "DOC_")
        self.ent_prefix.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.seq_inner, text="Text After Number (Suffix):", font=("Segoe UI", 11)).pack(anchor="w", pady=(3, 0))
        self.ent_suffix = ctk.CTkEntry(self.seq_inner)
        self.ent_suffix.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.seq_inner, text="Number Digits Format:", font=("Segoe UI", 11)).pack(anchor="w", pady=(3, 0))
        self.ent_digits = ctk.CTkEntry(self.seq_inner, width=80)
        self.ent_digits.insert(0, "3")
        self.ent_digits.pack(anchor="w", pady=2)

        # --- MODULE 4: TEXT MANIPULATION (DENGAN OPSI DELETE) ---
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.pack(fill="x", pady=5, anchor="n")
        
        lbl_text_title = ctk.CTkLabel(self.text_frame, text="4. Name Text Modification Module", font=("Segoe UI", 12, "bold"))
        lbl_text_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.var_reset_names = ctk.BooleanVar(value=False)
        self.cb_reset_names = ctk.CTkCheckBox(self.text_frame, text="Reset / Replace Original Name Entirely", 
                                            variable=self.var_reset_names, command=self._toggle_views, font=("Segoe UI", 11))
        self.cb_reset_names.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.text_inner = ctk.CTkFrame(self.text_frame, fg_color="transparent")
        self.text_inner.pack(fill="x", padx=10, pady=(0, 10))
        
        # DROPDOWN AKSI BARU
        ctk.CTkLabel(self.text_inner, text="Action Mode:", font=("Segoe UI", 11)).pack(anchor="w")
        self.cb_action_mode = ctk.CTkComboBox(self.text_inner, values=["Replace Text", "Delete Text Only"], 
                                            state="readonly", command=lambda v: self._toggle_views())
        self.cb_action_mode.set("Replace Text")
        self.cb_action_mode.pack(fill="x", pady=2)
        
        try:
            self.cb_action_mode._dropdown_menu.configure(min_width=260)
            self.cb_action_mode._entry.bind("<Button-1>", lambda e: self.cb_action_mode._on_button_press())
            self.cb_action_mode._canvas.bind("<Button-1>", lambda e: self.cb_action_mode._on_button_press())
        except Exception:
            pass
        
        self.lbl_replace_t = ctk.CTkLabel(self.text_inner, text="Find Word Content:", font=("Segoe UI", 11))
        self.lbl_replace_t.pack(anchor="w", pady=(3, 0))
        self.ent_replace_target = ctk.CTkEntry(self.text_inner)
        self.ent_replace_target.pack(fill="x", pady=2)
        
        self.lbl_replace_w = ctk.CTkLabel(self.text_inner, text="Replace With:", font=("Segoe UI", 11))
        self.lbl_replace_w.pack(anchor="w", pady=(3, 0))
        self.ent_replace_with = ctk.CTkEntry(self.text_inner)
        self.ent_replace_with.pack(fill="x", pady=2)

        self.lbl_prepend = ctk.CTkLabel(self.text_inner, text="Prepend to Original Name:", font=("Segoe UI", 11))
        self.lbl_prepend.pack(anchor="w", pady=(5, 0))
        self.ent_prepend = ctk.CTkEntry(self.text_inner)
        self.ent_prepend.pack(fill="x", pady=2)
        
        self.lbl_append = ctk.CTkLabel(self.text_inner, text="Append to Original Name:", font=("Segoe UI", 11))
        self.lbl_append.pack(anchor="w", pady=(3, 0))
        self.ent_append = ctk.CTkEntry(self.text_inner)
        self.ent_append.pack(fill="x", pady=2)
        
        self._toggle_views()

    def _toggle_views(self):
        bg_normal = "#343638"
        bg_disabled = "#2A2A2A"

        # 1. Handle Module 3 (Sequential Numbering) Visual State
        state_seq = "normal" if self.var_seq_enabled.get() else "disabled"
        bg_seq = bg_normal if self.var_seq_enabled.get() else bg_disabled
        
        for child in self.seq_inner.winfo_children():
            if isinstance(child, (ctk.CTkEntry, ctk.CTkComboBox)):
                child.configure(state=state_seq)
                if isinstance(child, ctk.CTkEntry):
                    child.configure(fg_color=bg_seq)
                
        # 2. Handle Module 4 (Text Manipulation) Visual State
        if self.var_reset_names.get():
            state_text = "disabled"
            state_replace_w = "disabled"
            self.cb_action_mode.configure(state="disabled")
            
            bg_prepend = bg_disabled
            bg_append = bg_disabled
            bg_target = bg_disabled
            bg_replace_w = bg_disabled
        else:
            state_text = "normal"
            self.cb_action_mode.configure(state="readonly")
            
            if self.cb_action_mode.get() == "Delete Text Only":
                state_replace_w = "disabled"
                bg_replace_w = bg_disabled
            else:
                state_replace_w = "normal"
                bg_replace_w = bg_normal
                
            bg_prepend = bg_normal
            bg_append = bg_normal
            bg_target = bg_normal
            
        self.ent_prepend.configure(state=state_text, fg_color=bg_prepend)
        self.ent_append.configure(state=state_text, fg_color=bg_append)
        self.ent_replace_target.configure(state=state_text, fg_color=bg_target)
        self.ent_replace_with.configure(state=state_replace_w, fg_color=bg_replace_w)

    def get_config(self):
        pos_map = {"Start of Name": "Awal Nama", "End of Name": "Akhir Nama"}
        return {
            "seq_enabled": self.var_seq_enabled.get(),
            "text_enabled": True,
            "reset_names": self.var_reset_names.get(),
            "seq_position": pos_map.get(self.cb_seq_position.get(), "Awal Nama"),
            "prefix": self.ent_prefix.get(),
            "suffix": self.ent_suffix.get(),
            "digits": self.ent_digits.get(),
            "prepend_text": self.ent_prepend.get(),
            "append_text": self.ent_append.get(),
            "replace_target": self.ent_replace_target.get(),
            "action_mode": self.cb_action_mode.get(),
            "replace_replacement": self.ent_replace_with.get()
        }