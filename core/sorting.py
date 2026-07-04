# core/sorting.py
from pathlib import Path

def get_file_metadata(file_path: Path) -> dict:
    stat = file_path.stat()
    return {
        "path": file_path,
        "name": file_path.name.lower(),
        "extension": file_path.suffix.lower(),
        "size": stat.st_size,
        "modification_date": stat.st_mtime,
        "creation_date": stat.st_ctime
    }

def sort_files(file_paths: list[Path], priorities: list[tuple[str, bool]]) -> list[Path]:
    """
    Mengurutkan file secara stabil berdasarkan urutan prioritas yang diberikan.
    priorities berisi list of tuple: [ (kriteria_1, reverse_1), (kriteria_2, reverse_2) ]
    Diurutkan dari prioritas paling rendah ke paling tinggi (Stable Sort Property).
    """
    if not priorities:
        return file_paths

    meta_list = [get_file_metadata(p) for p in file_paths]

    # Jalankan Timsort bawaan Python secara terbalik untuk menjaga kestabilan urutan berjenjang
    for criteria, reverse in reversed(priorities):
        meta_list.sort(key=lambda x: x[criteria], reverse=reverse)

    return [meta["path"] for meta in meta_list]