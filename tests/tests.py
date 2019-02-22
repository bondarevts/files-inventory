import os.path
import tempfile
from typing import Callable

import pytest

from inventory.hash_utils import hash_bytes
from inventory.hash_utils import hash_file
from inventory.inventory import FilesInventory


@pytest.fixture
def tmp_folder() -> str:
    with tempfile.TemporaryDirectory() as tmp_folder:
        yield tmp_folder


@pytest.fixture
def create_file(tmp_folder: str) -> Callable[[bytes], str]:
    def get_new_name() -> str:
        nonlocal counter
        name = f'file{counter}'
        counter += 1
        return name

    def create(content: bytes) -> str:
        full_file_name = os.path.join(tmp_folder, get_new_name())
        print(full_file_name)
        with open(full_file_name, 'wb') as f:
            f.write(content)
        return full_file_name

    counter = 0
    return create


def test_hash_same_bytes():
    x1 = b'12'
    x2 = b'1' + '2'.encode()  # ensure separate bytes object
    assert x1 == x2 and id(x1) != id(x2)
    assert hash_bytes(x1) == hash_bytes(x2)
    assert hash_bytes(b'') == hash_bytes(b'')


def test_hash_different_bytes():
    assert hash_bytes(b'12') != hash_bytes(b'13')


def test_file_hash_same_content(create_file):
    content = b'content'
    file1_path = create_file(content)
    file2_path = create_file(content)
    assert hash_file(file1_path) == hash_file(file2_path)


def test_file_hash_different_content(create_file):
    file1_path = create_file(b'a')
    file2_path = create_file(b'b')
    assert hash_file(file1_path) != hash_file(file2_path)


class TestFilesInventory:
    def test_find(self, tmp_folder: str, create_file: Callable[[bytes], str]):
        same_content = b'content'
        file1 = create_file(same_content)
        create_file(b'.')
        file3 = create_file(same_content)

        inventory = FilesInventory(tmp_folder)
        test_file = create_file(same_content)
        matches = [str(path) for path in inventory.find(test_file)]
        assert len(matches) == 2
        assert file1 in matches
        assert file3 in matches
