# ui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime

# Impor Sub-komponen Modular
from ui.components.folder_selector import FolderSelector
from ui.components.sorting_panel import SortingPanel
from ui.components.renaming_panel import RenamingPanel
from ui.components.file_table import FileTable

# Impor Core Engine
from core.sorting import sort_files
from core.renaming import generate_preview, detect_conflicts
from core.history import HistoryManager

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Batch File Renamer -nya RHAINY")
        self.geometry("1200x720")
        self.minsize(1050, 600)
        
        self.selected_folder = None
        self.current_files = []      
        self.preview_data = []       
        self.history_manager = HistoryManager()
        
        self._setup_styles()
        self._create_widgets()
        
    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TButton", padding=6, font=("Segoe UI", 9))
        self.style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"))
        self.style.configure("Status.TLabel", font=("Segoe UI", 9, "italic"))
        
        self.style.configure("TCheckbutton", font=("Segoe UI", 9), indicatorbackground="white")

    def _create_widgets(self):
        # 1. ATAS
        self.folder_selector = FolderSelector(self, on_folder_selected=self._handle_folder_selected)
        self.folder_selector.pack(fill="x", padx=15, pady=8)

        # 2. TENGAH
        workspace = ttk.Frame(self, padding=5)
        workspace.pack(fill="both", expand=True, padx=10)
        
        # Panel Kiri Scrollable & Mousewheel
        left_canvas = tk.Canvas(workspace, borderwidth=0, highlightthickness=0, width=340)
        left_scrollbar = ttk.Scrollbar(workspace, orient="vertical", command=left_canvas.yview)
        left_panel = ttk.Frame(left_canvas, padding=5)
        
        left_panel.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=left_panel, anchor="nw", width=340)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        left_canvas.pack(side="left", fill="y", padx=5)
        left_scrollbar.pack(side="left", fill="y")
        
        def _on_mousewheel(event):
            if event.delta: left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        left_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.sorting_panel = SortingPanel(left_panel)
        self.sorting_panel.pack(fill="x", pady=5, anchor="n")
        
        self.renaming_panel = RenamingPanel(left_panel)
        self.renaming_panel.pack(fill="x", pady=5, anchor="n")
        
        # Panel Kanan
        self.file_table = FileTable(workspace)
        self.file_table.pack(side="right", fill="both", expand=True, padx=5)
        
        # 3. BAWAH
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.pack(fill="x", side="bottom", padx=15, pady=5)
        
        self.lbl_status = ttk.Label(bottom_frame, text="Status: Siap.", style="Status.TLabel")
        self.lbl_status.pack(side="left")
        
        self.btn_undo = ttk.Button(bottom_frame, text="Undo (Batalkan Rename)", command=self._execute_undo, state="disabled")
        self.btn_undo.pack(side="right", padx=5)
        
        self.btn_rename = ttk.Button(bottom_frame, text="Mulai Simpan Perubahan", command=self._execute_rename, state="disabled")
        self.btn_rename.pack(side="right", padx=5)
        
        self.btn_preview = ttk.Button(bottom_frame, text="Lihat Preview Nama Baru", command=self._update_preview, state="disabled")
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
            
        self.lbl_status.config(text=f"Status: Berhasil memuat {len(self.current_files)} file.")
        self.btn_preview.config(state="normal" if self.current_files else "disabled")
        self.btn_rename.config(state="disabled")
        
        # Pengecekan mitigasi keamanan tombol Undo lokal
        history = self.history_manager.load_last_history()
        if history and Path(history[0]["new_path"]).parent == self.selected_folder:
            self.btn_undo.config(state="normal")
        else:
            self.btn_undo.config(state="disabled")

    def _update_preview(self):
        if not self.current_files: return
            
        priorities = self.sorting_panel.get_sorting_priorities()
        sorted_paths = sort_files(self.current_files, priorities)
        config = self.renaming_panel.get_config()
        
        self.preview_data = generate_preview(sorted_paths, config)
        conflicts = detect_conflicts(self.preview_data)
        
        if conflicts:
            error_msg = "\n".join(conflicts[:5])
            messagebox.showerror("Gagal Preview", f"Ditemukan konflik penamaan:\n\n{error_msg}")
            self.btn_rename.config(state="disabled")
            return
            
        self.file_table.clear()
        for old_path, new_name in self.preview_data:
            stat = old_path.stat()
            size_kb = f"{max(1, stat.st_size // 1024)} KB"
            c_date = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M')
            m_date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            self.file_table.insert_file(old_path.name, new_name, size_kb, old_path.suffix.upper(), c_date, m_date)
            
        self.lbl_status.config(text="Status: Preview berhasil dibuat.")
        self.btn_rename.config(state="normal")

    def _execute_rename(self):
        if not self.preview_data: return
        if not messagebox.askyesno("Konfirmasi", f"Ganti nama {len(self.preview_data)} file sekarang?"): return
            
        executed_pairs = []
        try:
            for old_path, new_name in self.preview_data:
                target_path = old_path.parent / new_name
                old_path.rename(target_path)
                executed_pairs.append((str(old_path), str(target_path)))
                
            self.history_manager.save_history(executed_pairs)
            messagebox.showinfo("Sukses", "Batch renaming selesai diproses!")
            
            self.btn_undo.config(state="normal")
            self.btn_rename.config(state="disabled")
            self._refresh_file_list()
            self.preview_data = []
        except Exception as e:
            messagebox.showerror("Gagal Sistem", f"Terjadi galat:\n{str(e)}")
            self._refresh_file_list()

    def _execute_undo(self):
        history = self.history_manager.load_last_history()
        if not history or not messagebox.askyesno("Konfirmasi Undo", f"Kembalikan nama {len(history)} file?"): return
            
        rollback_count = 0
        for item in history:
            current_path = Path(item["new_path"])
            original_path = Path(item["old_path"])
            if current_path.exists():
                current_path.rename(original_path)
                rollback_count += 1
                
        self.history_manager.clear_history()
        self.btn_undo.config(state="disabled")
        messagebox.showinfo("Undo Sukses", f"Berhasil mengembalikan {rollback_count} file.")
        self._refresh_file_list()