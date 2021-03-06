from pathlib import Path
from typing import Callable
from typing import List

import pytest

from inventory.hash_utils import hash_bytes
from inventory.hash_utils import hash_file
from inventory.inventory import FilesInventory
from tests.files_utils import create_files_structure


@pytest.fixture
def create_file(tmp_path: Path) -> Callable[[bytes], Path]:
    def get_new_name() -> str:
        nonlocal counter
        name = f'file{counter}'
        counter += 1
        return name

    def create(content: bytes) -> Path:
        full_file_name = tmp_path / get_new_name()
        full_file_name.write_bytes(content)
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
    def test_find(self, tmp_path: Path):
        same_content = 'content'
        test_folder, test_file = create_files_structure(tmp_path, f'''
            test_folder/
                file1:{same_content}
                file2:X
                file3:{same_content}
            test_file:{same_content}
        ''').files
        inventory = FilesInventory(test_folder.path)
        matches: List[Path] = list(inventory.find(test_file.path))
        assert len(matches) == 2
        assert test_folder.file1.path in matches
        assert test_folder.file3.path in matches

    def test_find_in_nested_folders(self, tmp_path):
        same_content = 'content'
        test_folder, test_file = create_files_structure(tmp_path, f'''
            test_folder/
                nested_folder/
                    file1:{same_content}
                    file2:X
                file3:{same_content}
            test_file:{same_content}
        ''').files
        inventory = FilesInventory(test_folder.path)
        matches: List[Path] = list(inventory.find(test_file.path))
        assert inventory.total_files() == 3
        assert len(matches) == 2
        assert {matches[0].name, matches[1].name} == {'file1', 'file3'}

    def test_hidden_files(self, tmp_path):
        test_files = create_files_structure(tmp_path, '''
            file1:1
            .file2:2
            file3:3
        ''')
        assert FilesInventory(test_files.path).total_files() == 2
        assert FilesInventory(test_files.path, hidden=True).total_files() == 3

    def test_files_count_empty_inventory(self, tmp_path):
        inventory = FilesInventory(tmp_path)
        assert inventory.total_files() == 0

    def test_files_count_empty_folders(self, tmp_path):
        inventory = FilesInventory(create_files_structure(tmp_path, '''
            empty1/
            empty2/
        ''').path)
        assert inventory.total_files() == 0

    def test_files_count(self, tmp_path):
        inventory = FilesInventory(create_files_structure(tmp_path, '''
            file1:1
            file2:2
            file3:3
        ''').path)
        assert inventory.total_files() == 3

    def test_find_duplicates(self, tmp_path):
        files = create_files_structure(tmp_path, '''
            file1:group1
            file2:group2
            file3:group2
            file4:group1
            file5:group1
            file6:group3
        ''')
        inventory = FilesInventory(tmp_path)
        assert len(files.files) == 6
        expected_group1 = {files.file1.path, files.file4.path, files.file5.path}
        expected_group2 = {files.file2.path, files.file3.path}

        duplicates = list(inventory.find_duplicates())
        assert len(duplicates) == 2
        group1, group2 = map(set, duplicates)
        assert (group1 == expected_group1 and group2 == expected_group2
                or group1 == expected_group2 and group2 == expected_group1)
