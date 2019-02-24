from __future__ import annotations

import dataclasses
from pathlib import Path
from textwrap import dedent
from typing import List
from typing import Union

OFFSET = ' ' * 4


@dataclasses.dataclass
class File:
    path: Path

    def read_content(self) -> str:
        with open(self.path, 'rb') as f:
            return f.read().decode()


@dataclasses.dataclass
class Folder:
    path: Path
    files: List[Union[File, Folder]] = dataclasses.field(default_factory=list)

    def __getattr__(self, item):
        for file in self.files:
            if file.path.name == item:
                return file
        raise AttributeError


def create_files_structure(root_path: Path, description: str) -> Folder:
    def get_depth(line: str) -> int:
        result = 0
        while line.startswith(OFFSET):
            line = line[len(OFFSET):]  # slow but simple
            result += 1
        return result

    def populate(parent: Folder, depth: int, current_line: int) -> int:
        while current_line < len(lines):
            line = lines[current_line]
            if get_depth(line) != depth:
                return current_line

            if line.endswith('/'):
                folder = Folder(parent.path / line.strip())
                folder.path.mkdir()
                current_line = populate(folder, depth + 1, current_line + 1)
                parent.files.append(folder)
                continue

            assert line.count(':') == 1
            file_name, content = line.strip().split(':')
            file_path = parent.path / file_name
            with open(file_path, 'wb') as file:
                file.write(content.encode())
            parent.files.append(File(file_path))
            current_line += 1
        return current_line

    lines = dedent(description).strip().splitlines()
    root = Folder(root_path)
    populate(root, depth=0, current_line=0)
    return root
