# core/renaming.py
from pathlib import Path

def generate_preview(file_paths: list[Path], config: dict) -> list[tuple[Path, str]]:
    """
    Menghasilkan tuple (Path_Lama, Nama_Baru) tanpa mengubah file asli.
    """
    preview_results = []
    
    for index, path in enumerate(file_paths, start=1):
        ext = path.suffix
        old_name_stem = path.stem
        
        if config.get("mode") == "sequential":
            prefix = config.get("prefix", "")
            suffix = config.get("suffix", "")
            digits = int(config.get("digits", 3))
            position = config.get("seq_position", "Awal Nama")
            
            # Membuat angka sekuensial (contoh: 001)
            seq_num = str(index).zfill(digits)
            
            # Atur posisi penempatan nomor urut sesuai konfigurasi
            if position == "Awal Nama":
                # Hasil format: PREFIX_001_SUFFIX.ext
                new_name = f"{prefix}{seq_num}{suffix}{ext}"
            else:
                # Hasil format: PREFIX_SUFFIX_001.ext
                new_name = f"{prefix}{suffix}{seq_num}{ext}"
            
        elif config.get("mode") == "text_operation":
            new_name = old_name_stem
            if config.get("prepend_text"):
                new_name = f"{config['prepend_text']}{new_name}"
            if config.get("append_text"):
                new_name = f"{new_name}{config['append_text']}"
            if config.get("replace_target"):
                new_name = new_name.replace(config["replace_target"], config["replace_replacement"])
            
            new_name = f"{new_name}{ext}"
        else:
            new_name = path.name
            
        preview_results.append((path, new_name))
        
    return preview_results

def detect_conflicts(preview_results: list[tuple[Path, str]]) -> list[str]:
    """Mendeteksi potensi nama kembar atau file overwrite."""
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