import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime

from ui.components.folder_selector import FolderSelector
from ui.components.sorting_panel import SortingPanel
from ui.components.renaming_panel import RenamingPanel
from ui.components.file_table import FileTable

from core.sorting import sort_files
from core.renaming import generate_preview, detect_conflicts
from core.history import HistoryManager

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Rhainy's Batch Renamer")
        self.geometry("1240x740")
        self.minsize(1050, 600)
        
        try:
            self.iconbitmap("app_icon.ico")
        except Exception:
            pass
            
        self.selected_folder = None
        self.current_files = []      
        self.preview_data = []       
        self.history_manager = HistoryManager()
        
        self._create_widgets()
        
    def _create_widgets(self):
        self.folder_selector = FolderSelector(self, on_folder_selected=self._handle_folder_selected)
        self.folder_selector.pack(fill="x", padx=15, pady=(15, 8))

        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=15, pady=5)
        
        left_panel = ctk.CTkScrollableFrame(workspace, width=320, label_text="Renaming Options", label_font=("Segoe UI", 12, "bold"))
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)
        
        self.sorting_panel = SortingPanel(left_panel)
        self.sorting_panel.pack(fill="x", pady=(0, 10), anchor="n")
        
        self.renaming_panel = RenamingPanel(left_panel)
        self.renaming_panel.pack(fill="x", pady=0, anchor="n")
        
        self.file_table = FileTable(workspace)
        self.file_table.pack(side="right", fill="both", expand=True)
        
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", side="bottom", padx=15, pady=15)
        
        self.lbl_status = ctk.CTkLabel(bottom_frame, text="Status: Ready.", font=("Segoe UI", 12, "italic"))
        self.lbl_status.pack(side="left", padx=5)
        
        self.btn_undo = ctk.CTkButton(bottom_frame, text="Undo Rename", fg_color="#d32f2f", hover_color="#b71c1c", command=self._execute_undo, state="disabled")
        self.btn_undo.pack(side="right", padx=5)
        
        self.btn_rename = ctk.CTkButton(bottom_frame, text="Apply Changes", fg_color="#2e7d32", hover_color="#1b5e20", command=self._execute_rename, state="disabled")
        self.btn_rename.pack(side="right", padx=5)
        
        self.btn_preview = ctk.CTkButton(bottom_frame, text="Preview New Names", command=self._update_preview, state="disabled")
        self.btn_preview.pack(side="right", padx=5)

    def _handle_folder_selected(self, folder_path):
        self.selected_folder = folder_path
        self._refresh_file_list()

    def _refresh_file_list(self):
        if not self.selected_folder: return
        self.current_files = [p for p in self.selected_folder.iterdir() if p.is_file()]
        
        self.file_table.clear()
        for p in self.current_files:
            stat = p.stat()
            size_kb = f"{max(1, stat.st_size // 1024)} KB"
            c_date = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M')
            m_date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            self.file_table.insert_file(p.name, "-", size_kb, p.suffix.upper(), c_date, m_date)
            
        self.lbl_status.configure(text=f"Status: Successfully loaded {len(self.current_files)} files.")
        self.btn_preview.configure(state="normal" if self.current_files else "disabled")
        self.btn_rename.configure(state="disabled")
        
        history = self.history_manager.load_last_history()
        if history and Path(history[0]["new_path"]).parent == self.selected_folder:
            self.btn_undo.configure(state="normal")
        else:
            self.btn_undo.configure(state="disabled")

    def _update_preview(self):
        if not self.current_files: return
            
        priorities = self.sorting_panel.get_sorting_priorities()
        sorted_paths = sort_files(self.current_files, priorities)
        config = self.renaming_panel.get_config()
        
        self.preview_data = generate_preview(sorted_paths, config)
        conflicts = detect_conflicts(self.preview_data)
        
        if conflicts:
            translated_conflicts = []
            for c in conflicts:
                if "Duplication Conflict" in c:
                    translated_conflicts.append(c.replace("Duplication Conflict: More than one file is projected to be named", "Duplication Conflict: Multiple files are projected to be named"))
                elif "Overwrite Conflict" in c:
                    translated_conflicts.append(c.replace("Overwrite Conflict: A file named", "Overwrite Conflict: A file named").replace("already exists in the target folder.", "already exists in the target folder."))
                else:
                    translated_conflicts.append(c)
                    
            error_msg = "\n".join(translated_conflicts[:5])
            messagebox.showerror("Preview Failed", f"Naming conflicts detected:\n\n{error_msg}")
            self.btn_rename.configure(state="disabled")
            return
            
        self.file_table.clear()
        for old_path, new_name in self.preview_data:
            stat = old_path.stat()
            size_kb = f"{max(1, stat.st_size // 1024)} KB"
            c_date = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M')
            m_date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            self.file_table.insert_file(old_path.name, new_name, size_kb, old_path.suffix.upper(), c_date, m_date)
            
        self.lbl_status.configure(text="Status: Preview generated successfully.")
        self.btn_rename.configure(state="normal")

    def _execute_rename(self):
        if not self.preview_data: return
        if not messagebox.askyesno("Confirmation", f"Rename {len(self.preview_data)} files now?"): return
            
        executed_pairs = []
        try:
            for old_path, new_name in self.preview_data:
                target_path = old_path.parent / new_name
                old_path.rename(target_path)
                executed_pairs.append((str(old_path), str(target_path)))
                
            self.history_manager.save_history(executed_pairs)
            messagebox.showinfo("Success", "Batch renaming process completed!")
            
            self.btn_undo.configure(state="normal")
            self.btn_rename.configure(state="disabled")
            self._refresh_file_list()
            self.preview_data = []
        except Exception as e:
            messagebox.showerror("System Error", f"An error occurred:\n{str(e)}")
            self._refresh_file_list()

    def _execute_undo(self):
        history = self.history_manager.load_last_history()
        if not history or not messagebox.askyesno("Confirm Undo", f"Rollback names for {len(history)} files?"): return
            
        rollback_count = 0
        for item in history:
            current_path = Path(item["new_path"])
            original_path = Path(item["old_path"])
            if current_path.exists():
                current_path.rename(original_path)
                rollback_count += 1
                
        self.history_manager.clear_history()
        self.btn_undo.configure(state="disabled")
        messagebox.showinfo("Undo Success", f"Successfully restored {rollback_count} files.")
        self._refresh_file_list()