# ui/main_window.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Import engine internal
from core.sorting import sort_files
from core.renaming import generate_preview, detect_conflicts
from core.history import HistoryManager

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistem Automasi Batch-Renaming File")
        
        # Jendela dibuat lebar dari awal agar seluruh tabel langsung kelihatan utuh
        self.geometry("1100x650")
        self.minsize(1000, 550)
        
        # State Data Aplikasi
        self.selected_folder = None
        self.current_files = []      # Menyimpan list of Path asli
        self.preview_data = []       # Menyimpan list of tuple (Path, nama_baru_str)
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
        # ==========================================
        # 1. BAGIAN ATAS: PEMILIHAN FOLDER
        # ==========================================
        top_frame = ttk.LabelFrame(self, text=" 1. Pilih Sumber File ", padding=10)
        top_frame.pack(fill="x", padx=15, pady=8)
        
        self.btn_browse = ttk.Button(top_frame, text="Buka Folder...", command=self._browse_folder)
        self.btn_browse.pack(side="left", padx=5)
        
        self.lbl_folder_path = ttk.Label(top_frame, text="Belum ada folder yang dipilih.", foreground="gray")
        self.lbl_folder_path.pack(side="left", padx=10, fill="x", expand=True)

        # ==========================================
        # 2. BAGIAN TENGAH: RUANG KERJA UTAMA (SPLIT)
        # ==========================================
        workspace = ttk.Frame(self, padding=5)
        workspace.pack(fill="both", expand=True, padx=10)
        
        # --- Panel Kiri: Kontrol & Kriteria (Lebar Terkunci 320px) ---
        left_panel = ttk.Frame(workspace, padding=5, width=320)
        left_panel.pack(side="left", fill="y", padx=5)
        left_panel.pack_propagate(False) 
        
        self._build_priority_sorting_panel(left_panel)
        self._build_friendly_renaming_panel(left_panel)
        
        # --- Panel Kanan: Tabel Informasi File ---
        right_panel = ttk.Frame(workspace, padding=5)
        right_panel.pack(side="right", fill="both", expand=True, padx=5)
        
        self._build_table_panel(right_panel)
        
        # ==========================================
        # 3. BAGIAN BAWAH: STATUS & TOMBOL AKSI
        # ==========================================
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
        
        # Aktifkan tombol undo jika terdeteksi ada file history log lama
        if self.history_manager.load_last_history():
            self.btn_undo.config(state="normal")

    def _build_priority_sorting_panel(self, parent):
        sort_frame = ttk.LabelFrame(parent, text=" 2. Urutan Prioritas File (Maks 2) ", padding=8)
        sort_frame.pack(fill="x", pady=5)
        
        criteria_options = ["(Tidak ada)", "Nama File", "Ekstensi File", "Ukuran File", "Tanggal Modifikasi", "Tanggal Dibuat"]
        self.criteria_map = {
            "(Tidak ada)": None, "Nama File": "name", "Ekstensi File": "extension",
            "Ukuran File": "size", "Tanggal Modifikasi": "modification_date", "Tanggal Dibuat": "creation_date"
        }
        
        # Kriteria Prioritas Pertama (Utama)
        ttk.Label(sort_frame, text="Prioritas 1 (Utama):").pack(anchor="w", pady=(2,0))
        self.cb_p1 = ttk.Combobox(sort_frame, values=criteria_options[1:], state="readonly")
        self.cb_p1.set("Nama File")
        self.cb_p1.pack(fill="x", pady=2)
        
        self.var_desc_p1 = tk.BooleanVar(value=False)
        ttk.Checkbutton(sort_frame, text="Urutan Terbalik (Z-A / Terbaru / Terbesar)", variable=self.var_desc_p1).pack(anchor="w", pady=(0,5))
        
        # Kriteria Prioritas Kedua (Opsional)
        ttk.Label(sort_frame, text="Prioritas 2 (Jika Prioritas 1 Sama):").pack(anchor="w")
        self.cb_p2 = ttk.Combobox(sort_frame, values=criteria_options, state="readonly")
        self.cb_p2.set("(Tidak ada)")
        self.cb_p2.pack(fill="x", pady=2)
        
        self.var_desc_p2 = tk.BooleanVar(value=False)
        ttk.Checkbutton(sort_frame, text="Urutan Terbalik (Z-A / Terbaru / Terbesar)", variable=self.var_desc_p2).pack(anchor="w")

    def _build_friendly_renaming_panel(self, parent):
        # Antarmuka Tab-based agar pengguna awam fokus pada opsi yang mereka inginkan tanpa tercampur
        self.rename_notebook = ttk.Notebook(parent)
        self.rename_notebook.pack(fill="both", expand=True, pady=10)
        
        # --- TAB 1: Pola Sekuensial / Angka Urut ---
        tab_seq = ttk.Frame(self.rename_notebook, padding=10)
        self.rename_notebook.add(tab_seq, text=" Pola Angka Urut ")
        
        ttk.Label(tab_seq, text="Posisi Nomor Urut:").pack(anchor="w", pady=(2,0))
        self.cb_seq_position = ttk.Combobox(tab_seq, values=["Awal Nama", "Akhir Nama"], state="readonly")
        self.cb_seq_position.set("Awal Nama")
        self.cb_seq_position.pack(fill="x", pady=2)
        
        ttk.Label(tab_seq, text="Teks Sebelum Angka (Prefix):").pack(anchor="w", pady=(5,0))
        self.ent_prefix = ttk.Entry(tab_seq)
        self.ent_prefix.insert(0, "DOC_")
        self.ent_prefix.pack(fill="x", pady=2)
        
        ttk.Label(tab_seq, text="Teks Setelah Angka (Suffix):").pack(anchor="w", pady=(5,0))
        self.ent_suffix = ttk.Entry(tab_seq)
        self.ent_suffix.pack(fill="x", pady=2)
        
        ttk.Label(tab_seq, text="Format Digit Angka (Contoh: 3 -> 001):").pack(anchor="w", pady=(5,0))
        self.ent_digits = ttk.Entry(tab_seq, width=10)
        self.ent_digits.insert(0, "3")
        self.ent_digits.pack(anchor="w", pady=2)
        
        # --- TAB 2: Operasi Modifikasi Teks ---
        tab_text = ttk.Frame(self.rename_notebook, padding=10)
        self.rename_notebook.add(tab_text, text=" Ubah Teks Nama ")
        
        ttk.Label(tab_text, text="Sisipkan di Depan Nama Asli:").pack(anchor="w", pady=(2,0))
        self.ent_prepend = ttk.Entry(tab_text)
        self.ent_prepend.pack(fill="x", pady=2)
        
        ttk.Label(tab_text, text="Sisipkan di Belakang Nama Asli:").pack(anchor="w", pady=(5,0))
        self.ent_append = ttk.Entry(tab_text)
        self.ent_append.pack(fill="x", pady=2)
        
        ttk.Separator(tab_text, orient="horizontal").pack(fill="x", pady=10)
        
        ttk.Label(tab_text, text="Cari Kata yang Ingin Diganti:").pack(anchor="w")
        self.ent_replace_target = ttk.Entry(tab_text)
        self.ent_replace_target.pack(fill="x", pady=2)
        
        ttk.Label(tab_text, text="Diganti Menjadi:").pack(anchor="w", pady=(5,0))
        self.ent_replace_with = ttk.Entry(tab_text)
        self.ent_replace_with.pack(fill="x", pady=2)

    def _build_table_panel(self, parent):
        columns = ("old_name", "new_name", "size", "type")
        self.table = ttk.Treeview(parent, columns=columns, show="headings")
        
        self.table.heading("old_name", text="Nama File Asli")
        self.table.heading("new_name", text="Nama File Baru (Preview)")
        self.table.heading("size", text="Ukuran")
        self.table.heading("type", text="Ekstensi")
        
        # Pengaturan lebar kolom presisi agar tidak terpotong saat jendela dibuka pertama kali
        self.table.column("old_name", width=310, anchor="w")
        self.table.column("new_name", width=310, anchor="w")
        self.table.column("size", width=85, anchor="e")
        self.table.column("type", width=75, anchor="center")
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ==========================================
    # KOORDINATOR LOGIKA & EVENT HANDLING
    # ==========================================

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
        # Membaca data file mentah di folder terpilih
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
            
        # 1. Validasi Pemilihan Kriteria Duplikat (Maksimal 2 Kriteria)
        p1_text = self.cb_p1.get()
        p2_text = self.cb_p2.get()
        
        p1_key = self.criteria_map[p1_text]
        p2_key = self.criteria_map[p2_text]
        
        if p2_key and p1_key == p2_key:
            messagebox.showwarning("Aturan Salah", "Prioritas 1 dan Prioritas 2 tidak boleh memilih kriteria yang sama.")
            return

        # Daftarkan aturan prioritas pengurutan
        priorities = [(p1_key, self.var_desc_p1.get())]
        if p2_key:
            priorities.append((p2_key, self.var_desc_p2.get()))
            
        # 2. Jalankan Proses Sorting Engine
        sorted_paths = sort_files(self.current_files, priorities)
        
        # 3. Kumpulkan Data Pengaturan dari Tab Aktif
        active_tab_index = self.rename_notebook.index(self.rename_notebook.select())
        config = {}
        
        if active_tab_index == 0:  # Tab Pola Angka Urut
            config.update({
                "mode": "sequential",
                "seq_position": self.cb_seq_position.get(),
                "prefix": self.ent_prefix.get(),
                "suffix": self.ent_suffix.get(),
                "digits": self.ent_digits.get()
            })
        else:                      # Tab Ubah Teks Nama
            config.update({
                "mode": "text_operation",
                "prepend_text": self.ent_prepend.get(),
                "append_text": self.ent_append.get(),
                "replace_target": self.ent_replace_target.get(),
                "replace_replacement": self.ent_replace_with.get()
            })
            
        # 4. Ambil Preview Nama & Deteksi Masalah Konflik Duplikasi
        self.preview_data = generate_preview(sorted_paths, config)
        conflicts = detect_conflicts(self.preview_data)
        
        if conflicts:
            error_msg = "\n".join(conflicts[:5])
            if len(conflicts) > 5:
                error_msg += f"\n... dan {len(conflicts) - 5} masalah keamanan lainnya."
            messagebox.showerror("Gagal Preview", f"Ditemukan konflik penamaan:\n\n{error_msg}")
            self.btn_rename.config(state="disabled")
            return
            
        # 5. Render Hasil Perubahan Sementara ke View Tabel
        for row in self.table.get_children():
            self.table.delete(row)
            
        for old_path, new_name in self.preview_data:
            size_kb = f"{max(1, old_path.stat().st_size // 1024)} KB"
            self.table.insert("", "end", values=(old_path.name, new_name, size_kb, old_path.suffix.upper()))
            
        self.lbl_status.config(text="Status: Preview berhasil dibuat. Silakan periksa tabel sebelum eksekusi.")
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