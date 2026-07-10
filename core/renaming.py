# core/renaming.py
import re
from pathlib import Path

def generate_preview(file_paths: list[Path], config: dict) -> list[tuple[Path, str]]:
    preview_results = []
    
    for index, path in enumerate(file_paths, start=1):
        ext = path.suffix
        base_word = path.stem
        
        # --- STEP 1: TEXT MANIPULATION OR RESET ---
        if config.get("reset_names"):
            base_word = ""
        else:
            if config.get("prepend_text"):
                base_word = f"{config['prepend_text']}{base_word}"
            if config.get("append_text"):
                base_word = f"{base_word}{config['append_text']}"
                
            target = config.get("replace_target")
            
            if config.get("action_mode") == "Delete Text Only":
                replacement = ""
            else:
                replacement = config.get("replace_replacement", "")
            
            if target:
                if re.search(r'[a-zA-Z0-9]', target):
                    pattern = r'(?<![a-zA-Z])' + re.escape(target) + r'(?![a-zA-Z])'
                else:
                    pattern = re.escape(target)
                    
                base_word = re.sub(pattern, replacement, base_word)
        
        # --- STEP 2: SEQUENTIAL NUMBER PATTERN ---
        if config.get("seq_enabled"):
            prefix = config.get("prefix", "")
            suffix = config.get("suffix", "")
            
            try:
                digits = int(config.get("digits", 3))
            except ValueError:
                digits = 3
                
            position = config.get("seq_position", "Awal Nama")
            seq_num = str(index).zfill(digits)
            num_block = f"{prefix}{seq_num}{suffix}"
            
            if position == "Awal Nama":
                final_stem = f"{num_block}{base_word}"
            else:
                final_stem = f"{base_word}{num_block}"
        else:
            final_stem = base_word
                
        if not final_stem:
            final_stem = f"file_{index}"
            
        final_name = f"{final_stem}{ext}"
        preview_results.append((path, final_name))
        
    return preview_results


def detect_conflicts(preview_results: list[tuple[Path, str]]) -> list[str]:
    """
    Detects potential data loss conflicts and provides smart, actionable 
    solutions directly to the user interface.
    """
    conflicts = []
    seen_names = set()
    has_duplication = False
    has_overwrite = False
    
    # Analyze the files to detect which specific conflict types occur
    for old_path, new_name in preview_results:
        target_path = old_path.parent / new_name
        
        if target_path in seen_names:
            has_duplication = True
        seen_names.add(target_path)
        
        if target_path.exists() and target_path != old_path:
            has_overwrite = True
            
    if has_duplication:
        msg_dup = (
            "[Duplication Conflict]\n"
            "Multiple files in the queue are generating the exact same new name.\n\n"
            "💡 How to Fix:\n"
            "1. Enable the 'Sequential Number Module' (Module 3) to ensure every file gets a unique index (001, 002, etc.).\n"
            "2. If numbering is disabled, make sure your Prepend/Append texts in Module 4 do not create uniform names."
        )
        conflicts.append(msg_dup)
        
    if has_overwrite:
        msg_ovr = (
            "[Overwrite Conflict]\n"
            "The projected file name already exists and belongs to another file in this folder.\n\n"
            "💡 How to Fix:\n"
            "1. Change the 'Prefix' or 'Suffix' text in Module 3 (e.g., change 'DOC_' to 'NEW_').\n"
            "2. Increase the 'Number Digits Format' or change the number position (Start/End) to avoid overlapping with existing files."
        )
        conflicts.append(msg_ovr)
            
    return conflicts