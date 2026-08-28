"""A Fonte IBGE: cadastro territorial brasileiro."""

from __future__ import annotations

from pathlib import Path

from ...source import CuratedTable, Source
from .extract import EXTRACTIONS

CURATE_DIR = Path(__file__).parent / "curate"

SOURCE = Source(
    name="ibge",
    description="IBGE — cadastro de municípios (dimensão `municipio`)",
    extractions=EXTRACTIONS,
    tables=(CuratedTable(name="municipio", sql_path=CURATE_DIR / "municipio.sql"),),
)
