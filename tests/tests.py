import os.path
import tempfile

from inventory.hash_utils import hash_bytes
from inventory.hash_utils import hash_file


import pytest


@pytest.fixture
def tmp_folder():
    with tempfile.TemporaryDirectory() as tmp_folder:
        yield tmp_folder


@pytest.fixture
def create_file(tmp_folder):
    def get_new_name():
        nonlocal counter
        name = f'file{counter}'
        counter += 1
        return name

    def create(content: bytes):
        full_file_name = os.path.join(tmp_folder, get_new_name())
        print(full_file_name)
        with open(full_file_name, 'wb') as f:
            f.write(content)
        return full_file_name

    counter = 0
    return create


def test_hash_same_bytes():
    x1 = b'12345'
    x2 = b'1234' + '5'.encode()
    assert x1 == x2 and id(x1) != id(x2)
    assert hash_bytes(x1) == hash_bytes(x2)
    assert hash_bytes(b'') == hash_bytes(b'')


def test_hash_different_bytes():
    assert hash_bytes(b'12345') != hash_bytes(b'12344')


def test_file_hash_same_content(create_file):
    content = b'content'
    file1_path = create_file(content)
    file2_path = create_file(content)
    assert hash_file(file1_path) == hash_file(file2_path)


def test_file_hash_different_content(create_file):
    file1_path = create_file(b'content1')
    file2_path = create_file(b'content2')
    assert hash_file(file1_path) != hash_file(file2_path)
