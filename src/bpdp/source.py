"""The anatomy every source copies: extract, declare, curate.

A source is a package that declares three things and nothing else:

* which files the agency publishes and where they live (*extract*);
* which columns those files are expected to carry (*declare*);
* which curated tables come out of them, in DuckDB SQL (*curate*).

Orchestration is written once, in :mod:`bpdp.pipeline`, and is the same for
every source. Adding the next source is filling this mold in, not designing a
new pipeline.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from . import cache
from .schema import Schema


def download(extraction: "Extraction", destination: Path, *, refresh: bool) -> Path:
    """Default extraction: fetch the published file as-is into the cache."""
    return cache.fetch(extraction.url, destination, refresh=refresh)


@dataclass(frozen=True)
class Extraction:
    """One file published by the agency, plus how to read and validate it.

    ``relation_sql`` is the DuckDB expression that turns the cached file into a
    relation; it receives the cached path as ``{path}``. Encoding, separator and
    every other quirk of the published file lives there, so that curation SQL
    never has to know about them.
    """

    name: str
    url: str
    filename: str
    relation_sql: str
    schema: Schema
    fetch: Callable[["Extraction", Path, bool], Path] = field(default=download, repr=False)

    def read_sql(self, path: Path) -> str:
        return self.relation_sql.format(path=str(path).replace("'", "''"))


@dataclass(frozen=True)
class CuratedTable:
    """One curated table, produced by a SQL file that reads the extractions.

    The SQL refers to each extraction by its ``name``, which the pipeline
    registers as a view before running the query.
    """

    name: str
    sql_path: Path

    def sql(self) -> str:
        return self.sql_path.read_text(encoding="utf-8")


@dataclass(frozen=True)
class Source:
    """A data source: its extractions and the curated tables they produce."""

    name: str
    description: str
    extractions: tuple[Extraction, ...]
    tables: tuple[CuratedTable, ...]
