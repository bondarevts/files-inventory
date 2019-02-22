from pathlib import Path
from typing import List

from inventory.hash_utils import hash_file
from inventory.types import PathType


class FilesInventory:
    def __init__(self, folder: PathType):
        folder = Path(folder)
        self._inventory = {}
        for file in folder.iterdir():
            self._inventory.setdefault(hash_file(file), []).append(file)

    def find(self, path: PathType) -> List[Path]:
        file_hash = hash_file(path)
        return self._inventory[file_hash]
