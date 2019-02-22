import tempfile
from pathlib import Path
from typing import Callable
from typing import List
from typing import Tuple

import pytest

from inventory.hash_utils import hash_bytes
from inventory.hash_utils import hash_file
from inventory.inventory import FilesInventory


@pytest.fixture
def tmp_folder() -> Path:
    with tempfile.TemporaryDirectory() as tmp_folder:
        yield Path(tmp_folder)


@pytest.fixture
def create_file(tmp_folder: Path) -> Callable[[bytes], Path]:
    def get_new_name() -> str:
        nonlocal counter
        name = f'file{counter}'
        counter += 1
        return name

    def create(content: bytes) -> Path:
        full_file_name = tmp_folder / get_new_name()
        with open(full_file_name, 'wb') as f:
            f.write(content)
        return full_file_name

    counter = 0
    return create


@pytest.fixture
def inventory_with_files(
        tmp_folder: Path, create_file: Callable[[bytes], Path]) -> Callable[..., Tuple[FilesInventory, List[Path]]]:
    def create_inventory(*contents: bytes) -> Tuple[FilesInventory, List[Path]]:
        file_names = [create_file(content) for content in contents]
        inventory = FilesInventory(tmp_folder)
        return inventory, file_names

    return create_inventory


def test_hash_same_bytes():
    x1 = b'12'
    x2 = b'1' + '2'.encode()  # ensure separate bytes object
    assert x1 == x2 and id(x1) != id(x2)
    assert hash_bytes(x1) == hash_bytes(x2)
    assert hash_bytes(b'') == hash_bytes(b'')


def test_hash_different_bytes():
    assert hash_bytes(b'12') != hash_bytes(b'13')


def test_file_hash_same_content(create_file: Callable[[bytes], Path]):
    content = b'content'
    file1_path = create_file(content)
    file2_path = create_file(content)
    assert hash_file(file1_path) == hash_file(file2_path)


def test_file_hash_different_content(create_file: Callable[[bytes], Path]):
    file1_path = create_file(b'a')
    file2_path = create_file(b'b')
    assert hash_file(file1_path) != hash_file(file2_path)


class TestFilesInventory:
    def test_find(self, inventory_with_files, create_file: Callable[[bytes], Path]):
        same_content = b'content'
        inventory, file_names = inventory_with_files(same_content, b'.', same_content)
        test_file = create_file(same_content)
        matches = list(inventory.find(test_file))
        assert len(matches) == 2
        assert file_names[0] in matches
        assert file_names[2] in matches
