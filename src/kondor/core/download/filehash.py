import hashlib
from pathlib import Path

CHUNK_BYTES = 1 << 20
DEFAULT_ALGORITHM = "sha256"


def digest_of(path: Path, algorithm: str = DEFAULT_ALGORITHM) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def matches_hash(path: Path, expected: str, algorithm: str = DEFAULT_ALGORITHM) -> bool:
    return path.is_file() and digest_of(path, algorithm) == expected.lower()
