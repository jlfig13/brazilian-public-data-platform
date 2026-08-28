"""Seam de teste offline: rodar o pipeline com o cache apontado para amostras.

Os testes entram pela mesma porta que o CI usa — executar uma Fonte com o cache
de Extração apontado para o diretório de amostras versionadas — e observam
apenas os Parquet que saem. Nenhum teste conhece parser, função de leitura ou
organização interna do SQL de curadoria.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

SAMPLES_DIR = Path(__file__).parent / "samples"


@pytest.fixture
def samples_dir() -> Path:
    return SAMPLES_DIR


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    """Uma cópia gravável das amostras, no formato do cache de Extração."""
    destination = tmp_path / "cache"
    shutil.copytree(SAMPLES_DIR, destination)
    return destination


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "tables"


@pytest.fixture
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Garante que a suíte não toca a rede: qualquer download falha o teste."""

    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("a suíte offline tentou acessar a rede")

    monkeypatch.setattr("urllib.request.urlopen", refuse)
