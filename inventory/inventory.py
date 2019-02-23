from pathlib import Path
from typing import Iterable

from inventory.hash_utils import hash_file


class FilesInventory:
    def __init__(self, folder: Path):
        self._inventory = {}
        for file in folder.iterdir():
            self._inventory.setdefault(hash_file(file), []).append(file)

    def find(self, path: Path) -> Iterable[Path]:
        file_hash = hash_file(path)
        return self._inventory[file_hash]

    def find_duplicates(self) -> Iterable[Iterable[Path]]:
        for files in self._inventory.values():
            if len(files) > 1:
                yield files
