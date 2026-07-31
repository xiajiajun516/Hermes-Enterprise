"""Exclusive immutable artifact writes and SHA-256."""
import hashlib
import os
from pathlib import Path

from artifact_naming import artifact_path


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def create_new_utf8(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
    except BaseException:
        raise


def create_timestamped_artifact(root, slug, name, instant, text):
    for sequence in [None, *range(1, 1000)]:
        rel = artifact_path(slug, name, instant, sequence)
        try:
            create_new_utf8(Path(root) / rel, text)
            return rel, sha256_file(Path(root) / rel)
        except FileExistsError:
            continue
    raise FileExistsError("timestamp sequence exhausted")
