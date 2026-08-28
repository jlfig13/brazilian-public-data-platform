"""The local extraction cache.

Extraction writes the agency's files here untransformed. The cache is
disposable and never versioned: it holds bytes that can always be fetched
again. An extraction already in the cache is reused instead of downloaded.
"""

from __future__ import annotations

import os
import shutil
import urllib.request
from pathlib import Path

DEFAULT_CACHE_DIR = Path("data/cache")
CACHE_DIR_ENV = "BPDP_CACHE_DIR"

USER_AGENT = "bpdp/0.1 (+https://github.com/jlfig13/brazilian-public-data-platform)"


def default_cache_dir() -> Path:
    """The cache directory, overridable by environment for CI and for tests."""
    return Path(os.environ.get(CACHE_DIR_ENV) or DEFAULT_CACHE_DIR)


def cached_path(cache_dir: Path, source: str, filename: str) -> Path:
    return cache_dir / source / filename


def fetch(url: str, destination: Path, *, refresh: bool = False, timeout: int = 120) -> Path:
    """Download ``url`` into ``destination`` unless it is already cached."""
    if destination.exists() and not refresh:
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".partial")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response, partial.open("wb") as out:
        shutil.copyfileobj(response, out)
    partial.replace(destination)
    return destination
