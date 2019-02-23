from pathlib import Path
from typing import Iterable

from inventory.hash_utils import hash_file


class FilesInventory:
    def __init__(self, folder: Path):
        self._files_count = 0
        self._inventory = {}
        self._walk_folder(folder)

    def find(self, path: Path) -> Iterable[Path]:
        file_hash = hash_file(path)
        return self._inventory[file_hash]

    def find_duplicates(self) -> Iterable[Iterable[Path]]:
        for files in self._inventory.values():
            if len(files) > 1:
                yield files

    def total_files(self) -> int:
        return self._files_count

    def _walk_folder(self, folder: Path):
        for file in folder.iterdir():
            if file.is_dir():
                self._walk_folder(file)
                continue

            self._inventory.setdefault(hash_file(file), []).append(file)
            self._files_count += 1
