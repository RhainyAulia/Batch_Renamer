# core/renaming.py
from pathlib import Path

def generate_preview(file_paths: list[Path], config: dict) -> list[tuple[Path, str]]:
    """
    Menghasilkan tuple (Path_Lama, Nama_Baru) dengan fitur reset nama asli.
    """
    preview_results = []
    
    for index, path in enumerate(file_paths, start=1):
        ext = path.suffix
        new_name = path.stem
        
        # --- LANGKAH 1: Jalankan Operasi Teks / Reset Nama ---
        if config.get("text_enabled"):
            # Jika user memilih untuk mereset/menghapus nama asli file
            if config.get("reset_names"):
                new_name = ""
            else:
                if config.get("prepend_text"):
                    new_name = f"{config['prepend_text']}{new_name}"
                if config.get("append_text"):
                    new_name = f"{new_name}{config['append_text']}"
                if config.get("replace_target"):
                    new_name = new_name.replace(config["replace_target"], config["replace_replacement"])
        
        # --- LANGKAH 2: Jalankan Pola Angka Urut ---
        if config.get("seq_enabled"):
            prefix = config.get("prefix", "")
            suffix = config.get("suffix", "")
            digits = int(config.get("digits", 3))
            position = config.get("seq_position", "Awal Nama")
            
            seq_num = str(index).zfill(digits)
            
            # Penggabungan nama berdasarkan posisi nomor urut
            if position == "Awal Nama":
                new_name = f"{prefix}{seq_num}{suffix}{new_name}"
            else:
                new_name = f"{new_name}{prefix}{suffix}{seq_num}"
                
        # Jika setelah diproses nama file benar-benar kosong (karena nama direset dan modul angka mati)
        if not new_name:
            new_name = f"file_{index}"
            
        final_name = f"{new_name}{ext}"
        preview_results.append((path, final_name))
        
    return preview_results

def detect_conflicts(preview_results: list[tuple[Path, str]]) -> list[str]:
    conflicts = []
    seen_names = set()
    
    for old_path, new_name in preview_results:
        target_path = old_path.parent / new_name
        
        if target_path in seen_names:
            conflicts.append(f"Konflik Duplikasi: Lebih dari satu file akan diubah menjadi '{new_name}'")
        seen_names.add(target_path)
        
        if target_path.exists() and target_path != old_path:
            conflicts.append(f"Konflik Overwrite: File '{new_name}' sudah ada di folder tujuan.")
            
    return list(set(conflicts))