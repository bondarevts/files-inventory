import hashlib
from pathlib import Path

HASH_ALGORITHM = hashlib.md5


def hash_bytes(data: bytes) -> str:
    hash_processor = HASH_ALGORITHM()
    hash_processor.update(data)
    return hash_processor.hexdigest()


def hash_file(file: Path) -> str:
    return hash_bytes(file.read_bytes())
