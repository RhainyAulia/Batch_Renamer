# ui/main_window.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from core.sorting import sort_files
from core.renaming import generate_preview, detect_conflicts
from core.history import HistoryManager

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistem Automasi Batch-Renaming File")
        self.geometry("1150x720")
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

    def _create_widgets(self):
        # 1. ATAS: PILIH FOLDER
        top_frame = ttk.LabelFrame(self, text=" 1. Pilih Sumber File ", padding=10)
        top_frame.pack(fill="x", padx=15, pady=8)
        
        self.btn_browse = ttk.Button(top_frame, text="Buka Folder...", command=self._browse_folder)
        self.btn_browse.pack(side="left", padx=5)
        
        self.lbl_folder_path = ttk.Label(top_frame, text="Belum ada folder yang dipilih.", foreground="gray")
        self.lbl_folder_path.pack(side="left", padx=10, fill="x", expand=True)

        # 2. TENGAH: WORKSPACE
        workspace = ttk.Frame(self, padding=5)
        workspace.pack(fill="both", expand=True, padx=10)
        
# Panel Kiri (Scrollable untuk konfigurasi bertumpuk)
        left_canvas = tk.Canvas(workspace, borderwidth=0, highlightthickness=0, width=340)
        left_scrollbar = ttk.Scrollbar(workspace, orient="vertical", command=left_canvas.yview)
        left_panel = ttk.Frame(left_canvas, padding=5)
        
        left_panel.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=left_panel, anchor="nw", width=340)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        left_canvas.pack(side="left", fill="y", padx=5)
        left_scrollbar.pack(side="left", fill="y")
        
        # --- [BARU] FITUR MOUSE WHEEL SCROLL ---
        # Fungsi untuk menggerakkan canvas saat mouse wheel diputar
        def _on_mousewheel(event):
            # Windows menggunakan event.delta, Linux biasanya menggunakan event.num
            if event.delta:
                left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                if event.num == 4:
                    left_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    left_canvas.yview_scroll(1, "units")

        # Ikat event mousewheel ke Canvas dan seluruh area di dalamnya
        left_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Khusus OS Linux (Ubuntu/Debian) menggunakan Button-4 dan Button-5
        left_canvas.bind_all("<Button-4>", _on_mousewheel)
        left_canvas.bind_all("<Button-5>", _on_mousewheel)
        
        # Panel Kanan: Tabel
        right_panel = ttk.Frame(workspace, padding=5)
        right_panel.pack(side="right", fill="both", expand=True, padx=5)
        
        self._build_priority_sorting_panel(left_panel)
        self._build_combined_renaming_panel(left_panel)
        self._build_table_panel(right_panel)
        
        # 3. BAWAH: AKSI
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
        
        if self.history_manager.load_last_history():
            self.btn_undo.config(state="normal")

    def _build_priority_sorting_panel(self, parent):
        sort_frame = ttk.LabelFrame(parent, text=" 2. Urutan Prioritas File (Maks 2) ", padding=8)
        sort_frame.pack(fill="x", pady=5, anchor="n")
        
        criteria_options = ["(Tidak ada)", "Nama File", "Ekstensi File", "Ukuran File", "Tanggal Modifikasi", "Tanggal Dibuat"]
        self.criteria_map = {
            "(Tidak ada)": None, "Nama File": "name", "Ekstensi File": "extension",
            "Ukuran File": "size", "Tanggal Modifikasi": "modification_date", "Tanggal Dibuat": "creation_date"
        }
        
        ttk.Label(sort_frame, text="Prioritas 1 (Utama):").pack(anchor="w", pady=(2,0))
        self.cb_p1 = ttk.Combobox(sort_frame, values=criteria_options[1:], state="readonly")
        self.cb_p1.set("Nama File")
        self.cb_p1.pack(fill="x", pady=2)
        
        self.var_desc_p1 = tk.BooleanVar(value=False)
        ttk.Checkbutton(sort_frame, text="Urutan Terbalik (Z-A / Terbaru)", variable=self.var_desc_p1).pack(anchor="w", pady=(0,5))
        
        ttk.Label(sort_frame, text="Prioritas 2 (Opsional):").pack(anchor="w")
        self.cb_p2 = ttk.Combobox(sort_frame, values=criteria_options, state="readonly")
        self.cb_p2.set("(Tidak ada)")
        self.cb_p2.pack(fill="x", pady=2)
        
        self.var_desc_p2 = tk.BooleanVar(value=False)
        ttk.Checkbutton(sort_frame, text="Urutan Terbalik (Z-A / Terbaru)", variable=self.var_desc_p2).pack(anchor="w")

    def _build_combined_renaming_panel(self, parent):
        # --- PANEL MODUL 1: ANGKA URUT ---
        self.seq_frame = ttk.LabelFrame(parent, text=" 3. Modul Angka Urut ", padding=8)
        self.seq_frame.pack(fill="x", pady=8, anchor="n")
        
        self.var_seq_enabled = tk.BooleanVar(value=True)
        cb_enable_seq = ttk.Checkbutton(self.seq_frame, text="Aktifkan Penomoran Berurutan", 
                                        variable=self.var_seq_enabled, command=self._toggle_module_views)
        cb_enable_seq.pack(anchor="w", pady=(0,5))
        
        self.seq_inner_frame = ttk.Frame(self.seq_frame)
        self.seq_inner_frame.pack(fill="x")
        
        ttk.Label(self.seq_inner_frame, text="Posisi Nomor Urut:").pack(anchor="w")
        self.cb_seq_position = ttk.Combobox(self.seq_inner_frame, values=["Awal Nama", "Akhir Nama"], state="readonly")
        self.cb_seq_position.set("Awal Nama")
        self.cb_seq_position.pack(fill="x", pady=2)
        
        ttk.Label(self.seq_inner_frame, text="Teks Sebelum Angka (Prefix):").pack(anchor="w", pady=(3,0))
        self.ent_prefix = ttk.Entry(self.seq_inner_frame)
        self.ent_prefix.insert(0, "DOC_")
        self.ent_prefix.pack(fill="x", pady=2)
        
        ttk.Label(self.seq_inner_frame, text="Teks Setelah Angka (Suffix):").pack(anchor="w", pady=(3,0))
        self.ent_suffix = ttk.Entry(self.seq_inner_frame)
        self.ent_suffix.pack(fill="x", pady=2)
        
        ttk.Label(self.seq_inner_frame, text="Format Digit Angka (Contoh: 3 -> 001):").pack(anchor="w", pady=(3,0))
        self.ent_digits = ttk.Entry(self.seq_inner_frame, width=10)
        self.ent_digits.insert(0, "3")
        self.ent_digits.pack(anchor="w", pady=2)

        # --- PANEL MODUL 2: OPERASI MODIFIKASI TEKS ---
        self.text_frame = ttk.LabelFrame(parent, text=" 4. Modul Ubah Teks Nama ", padding=8)
        self.text_frame.pack(fill="x", pady=5, anchor="n")
        
        self.var_text_enabled = tk.BooleanVar(value=False)
        cb_enable_text = ttk.Checkbutton(self.text_frame, text="Aktifkan Pembersihan/Ubah Teks", 
                                         variable=self.var_text_enabled, command=self._toggle_module_views)
        cb_enable_text.pack(anchor="w", pady=(0,5))
        
        self.text_inner_frame = ttk.Frame(self.text_frame)
        self.text_inner_frame.pack(fill="x")
        
        # [BARU] Opsi reset nama asli file
        self.var_reset_names = tk.BooleanVar(value=False)
        self.cb_reset_names = ttk.Checkbutton(self.text_inner_frame, text="Reset / Ganti Total Nama Asli", 
                                              variable=self.var_reset_names, command=self._toggle_module_views)
        self.cb_reset_names.pack(anchor="w", pady=(0, 5))
        
        self.lbl_prepend = ttk.Label(self.text_inner_frame, text="Sisipkan di Depan Nama Asli:")
        self.lbl_prepend.pack(anchor="w")
        self.ent_prepend = ttk.Entry(self.text_inner_frame)
        self.ent_prepend.pack(fill="x", pady=2)
        
        self.lbl_append = ttk.Label(self.text_inner_frame, text="Sisipkan di Belakang Nama Asli:")
        self.lbl_append.pack(anchor="w", pady=(3,0))
        self.ent_append = ttk.Entry(self.text_inner_frame)
        self.ent_append.pack(fill="x", pady=2)
        
        self.lbl_replace_t = ttk.Label(self.text_inner_frame, text="Cari Kata Konten:")
        self.lbl_replace_t.pack(anchor="w", pady=(5,0))
        self.ent_replace_target = ttk.Entry(self.text_inner_frame)
        self.ent_replace_target.pack(fill="x", pady=2)
        
        self.lbl_replace_w = ttk.Label(self.text_inner_frame, text="Ganti Menjadi:")
        self.lbl_replace_w.pack(anchor="w", pady=(3,0))
        self.ent_replace_with = ttk.Entry(self.text_inner_frame)
        self.ent_replace_with.pack(fill="x", pady=2)
        
        self._toggle_module_views()

    def _toggle_module_views(self):
        """Menghidupkan/mematikan input field berdasarkan status checkbox."""
        # Kontrol modul angka urut
        if self.var_seq_enabled.get():
            for child in self.seq_inner_frame.winfo_children():
                child.configure(state="normal")
        else:
            for child in self.seq_inner_frame.winfo_children():
                child.configure(state="disabled")
                
        # Kontrol modul teks
        if self.var_text_enabled.get():
            self.cb_reset_names.configure(state="normal")
            
            # Jika opsi reset nama dicentang, nonaktifkan operasi teks penambah karena nama aslinya sudah dibuang
            if self.var_reset_names.get():
                self.ent_prepend.configure(state="disabled")
                self.ent_append.configure(state="disabled")
                self.ent_replace_target.configure(state="disabled")
                self.ent_replace_with.configure(state="disabled")
            else:
                self.ent_prepend.configure(state="normal")
                self.ent_append.configure(state="normal")
                self.ent_replace_target.configure(state="normal")
                self.ent_replace_with.configure(state="normal")
        else:
            self.cb_reset_names.configure(state="disabled")
            self.ent_prepend.configure(state="disabled")
            self.ent_append.configure(state="disabled")
            self.ent_replace_target.configure(state="disabled")
            self.ent_replace_with.configure(state="disabled")

    def _build_table_panel(self, parent):
        columns = ("old_name", "new_name", "size", "type")
        self.table = ttk.Treeview(parent, columns=columns, show="headings")
        
        self.table.heading("old_name", text="Nama File Asli")
        self.table.heading("new_name", text="Nama File Baru (Preview)")
        self.table.heading("size", text="Ukuran")
        self.table.heading("type", text="Ekstensi")
        
        self.table.column("old_name", width=320, anchor="w")
        self.table.column("new_name", width=320, anchor="w")
        self.table.column("size", width=85, anchor="e")
        self.table.column("type", width=75, anchor="center")
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # --- KONTROLLER ---

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.selected_folder = Path(folder)
        self.lbl_folder_path.config(text=str(self.selected_folder), foreground="black")
        self._refresh_file_list()

    def _refresh_file_list(self):
        if not self.selected_folder:
            return
        self.current_files = [p for p in self.selected_folder.iterdir() if p.is_file()]
        
        for row in self.table.get_children():
            self.table.delete(row)
            
        for p in self.current_files:
            size_kb = f"{max(1, p.stat().st_size // 1024)} KB"
            self.table.insert("", "end", values=(p.name, "-", size_kb, p.suffix.upper()))
            
        self.lbl_status.config(text=f"Status: Berhasil memuat {len(self.current_files)} file.")
        self.btn_preview.config(state="normal" if self.current_files else "disabled")
        self.btn_rename.config(state="disabled")

    def _update_preview(self):
        if not self.current_files:
            return
            
        if not self.var_seq_enabled.get() and not self.var_text_enabled.get():
            messagebox.showwarning("Peringatan", "Pilih minimal salah satu modul konfigurasi nama.")
            return
            
        p1_key = self.criteria_map[self.cb_p1.get()]
        p2_key = self.criteria_map[self.cb_p2.get()]
        
        if p2_key and p1_key == p2_key:
            messagebox.showwarning("Aturan Salah", "Prioritas 1 dan Prioritas 2 tidak boleh memilih kriteria yang sama.")
            return

        priorities = [(p1_key, self.var_desc_p1.get())]
        if p2_key:
            priorities.append((p2_key, self.var_desc_p2.get()))
            
        sorted_paths = sort_files(self.current_files, priorities)
        
        config = {
            "seq_enabled": self.var_seq_enabled.get(),
            "text_enabled": self.var_text_enabled.get(),
            "reset_names": self.var_reset_names.get(), # [BARU] Meneruskan parameter reset
            "seq_position": self.cb_seq_position.get(),
            "prefix": self.ent_prefix.get(),
            "suffix": self.ent_suffix.get(),
            "digits": self.ent_digits.get(),
            "prepend_text": self.ent_prepend.get(),
            "append_text": self.ent_append.get(),
            "replace_target": self.ent_replace_target.get(),
            "replace_replacement": self.ent_replace_with.get()
        }
        
        self.preview_data = generate_preview(sorted_paths, config)
        conflicts = detect_conflicts(self.preview_data)
        
        if conflicts:
            error_msg = "\n".join(conflicts[:5])
            if len(conflicts) > 5:
                error_msg += f"\n... dan {len(conflicts) - 5} masalah keamanan lainnya."
            messagebox.showerror("Gagal Preview", f"Ditemukan konflik penamaan:\n\n{error_msg}")
            self.btn_rename.config(state="disabled")
            return
            
        for row in self.table.get_children():
            self.table.delete(row)
            
        for old_path, new_name in self.preview_data:
            size_kb = f"{max(1, old_path.stat().st_size // 1024)} KB"
            self.table.insert("", "end", values=(old_path.name, new_name, size_kb, old_path.suffix.upper()))
            
        self.lbl_status.config(text="Status: Preview berhasil dibuat.")
        self.btn_rename.config(state="normal")

    def _execute_rename(self):
        if not self.preview_data:
            return
            
        if not messagebox.askyesno("Konfirmasi", f"Ganti nama {len(self.preview_data)} file sekarang?"):
            return
            
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
            messagebox.showerror("Gagal Sistem", f"Proses terhenti di tengah jalan:\n{str(e)}")
            self._refresh_file_list()

    def _execute_undo(self):
        history = self.history_manager.load_last_history()
        if not history:
            messagebox.showwarning("Kosong", "Tidak ada riwayat operasi yang bisa dibatalkan.")
            return
            
        if not messagebox.askyesno("Konfirmasi Undo", f"Kembalikan nama {len(history)} file ke format asal?"):
            return
            
        rollback_count = 0
        for item in history:
            current_modified_path = Path(item["new_path"])
            original_path = Path(item["old_path"])
            
            if current_modified_path.exists():
                current_modified_path.rename(original_path)
                rollback_count += 1
                
        self.history_manager.clear_history()
        self.btn_undo.config(state="disabled")
        
        messagebox.showinfo("Undo Sukses", f"Berhasil mengembalikan {rollback_count} file ke kondisi semula.")
        self._refresh_file_list()