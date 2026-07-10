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
    if not priorities:
        return file_paths

    meta_list = [get_file_metadata(p) for p in file_paths]

    for criteria, reverse in reversed(priorities):
        meta_list.sort(key=lambda x: x[criteria], reverse=reverse)

    return [meta["path"] for meta in meta_list]