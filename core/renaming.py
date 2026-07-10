# core/renaming.py
import re
from pathlib import Path

def generate_preview(file_paths: list[Path], config: dict) -> list[tuple[Path, str]]:

    preview_results = []
    
    for index, path in enumerate(file_paths, start=1):
        ext = path.suffix
        base_word = path.stem
        
        #Operasi Teks / Reset Nama ---
        if config.get("reset_names"):
            base_word = ""
        else:
            if config.get("prepend_text"):
                base_word = f"{config['prepend_text']}{base_word}"
            if config.get("append_text"):
                base_word = f"{base_word}{config['append_text']}"
                
            #regex \b (Word Boundary) 
            target = config.get("replace_target")
            replacement = config.get("replace_replacement", "")
            
            if target:
                # re.escape karakter unik 
                pattern = r'\b' + re.escape(target) + r'\b'
                base_word = re.sub(pattern, replacement, base_word)
        
        # Pola Angka Urut
        if config.get("seq_enabled"):
            prefix = config.get("prefix", "")
            suffix = config.get("suffix", "")
            
            try:
                digits = int(config.get("digits", 3))
            except ValueError:
                digits = 3
                
            position = config.get("seq_position", "Awal Nama")
            
            # Generate nomor urut berdasarkan format digit
            seq_num = str(index).zfill(digits)
            
            # Gabungkan nomor dengan prefix dan suffix-nya sendiri terlebih dahulu
            num_block = f"{prefix}{seq_num}{suffix}"
            
            # num_block thd Kata Utama
            if position == "Awal Nama":
                final_stem = f"{num_block}{base_word}"
            else:
                final_stem = f"{base_word}{num_block}"
        else:
            final_stem = base_word
                
        # Proteksi jika hasil nama benar-benar kosong agar file tidak tidak memiliki nama
        if not final_stem:
            final_stem = f"file_{index}"
            
        final_name = f"{final_stem}{ext}"
        preview_results.append((path, final_name))
        
    return preview_results


def detect_conflicts(preview_results: list[tuple[Path, str]]) -> list[str]:
    """
    Mendeteksi potensi bahaya data terhapus (Overwrite) atau dua file menjadi nama yang sama (Duplikasi)
    sebelum eksekusi perubahan nama dilakukan secara permanen di hardisk.
    """
    conflicts = []
    seen_names = set()
    
    for old_path, new_name in preview_results:
        target_path = old_path.parent / new_name
        
        # Antrean internal menghasilkan nama yang kembar identik
        if target_path in seen_names:
            conflicts.append(f"Konflik Duplikasi: Lebih dari satu file diproyeksikan berubah menjadi '{new_name}'")
        seen_names.add(target_path)
        
        # Nama baru menabrak file yang sudah ada di folder tersebut
        if target_path.exists() and target_path != old_path:
            conflicts.append(f"Konflik Overwrite: File dengan nama '{new_name}' sudah eksis di folder tujuan.")
            
    return list(set(conflicts))