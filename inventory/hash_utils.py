import hashlib
from pathlib import Path
from typing import Union

HASH_ALGORITHM = hashlib.md5
PathType = Union[str, Path]


def hash_bytes(data: bytes) -> str:
    hash_processor = HASH_ALGORITHM()
    hash_processor.update(data)
    return hash_processor.hexdigest()


def hash_file(file: PathType) -> str:
    with open(file, 'rb') as f:
        return hash_bytes(f.read())