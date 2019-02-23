from tests.files_utils import Folder
from .files_utils import File
from .files_utils import create_files_structure


def assert_file_name_and_content(file: File, name: str, content: str):
    assert file.path.name == name
    assert file.read_content() == content


def assert_folder(folder: Folder, *, name: str, length: int):
    assert folder.path.name == name
    assert len(folder.files) == length


def test_one_file(tmp_path):
    content = 'content'
    folder = create_files_structure(tmp_path, f'file1:{content}')
    assert len(folder.files) == 1
    assert_file_name_and_content(folder.files[0], 'file1', content)


def test_several_files(tmp_path):
    folder = create_files_structure(tmp_path, '''
        file1:1
        file2:2
    ''')
    file1, file2 = folder.files
    assert_file_name_and_content(file1, 'file1', '1')
    assert_file_name_and_content(file2, 'file2', '2')


def test_folder(tmp_path):
    root_folder = create_files_structure(tmp_path, '''
        folder/
            file1:1
            file2:2
        file:3
    ''')

    folder, file = root_folder.files
    assert_file_name_and_content(file, 'file', '3')
    assert folder.path.name == 'folder'
    assert {('file1', '1'), ('file2', '2')} == {
        (file.path.name, file.read_content())
        for file in folder.files
    }


def test_nested_folders(tmp_path):
    root_folder = create_files_structure(tmp_path, '''
        folder1/
            folder2/
                folder3/
                    file:content
    ''')
    assert len(root_folder.files) == 1
    folder1 = root_folder.files[0]
    assert_folder(folder1, name='folder1', length=1)

    folder2 = folder1.files[0]
    assert_folder(folder2, name='folder2', length=1)

    folder3 = folder2.files[0]
    assert_folder(folder3, name='folder3', length=1)
    assert_file_name_and_content(folder3.files[0], 'file', 'content')
