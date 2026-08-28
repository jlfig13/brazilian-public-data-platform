"""Running a source end to end: extract, validate, curate, write Parquet.

The order matters and is the failure policy of the platform: every extraction is
validated against its declared schema *before* any curated table is written, so
a source whose layout changed leaves the previous output untouched instead of
overwriting it with something half correct.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb

from . import cache, schema
from .source import Extraction, Source

DEFAULT_OUTPUT_DIR = Path("data/tables")


@dataclass(frozen=True)
class Result:
    """What one run of a source produced."""

    source: str
    extractions: dict[str, Path]
    tables: dict[str, Path]


def run(
    source: Source,
    *,
    cache_dir: Path | None = None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    refresh: bool = False,
) -> Result:
    cache_dir = cache_dir if cache_dir is not None else cache.default_cache_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted = {
        extraction.name: _extract(source, extraction, cache_dir, refresh=refresh)
        for extraction in source.extractions
    }

    connection = duckdb.connect()
    try:
        for extraction in source.extractions:
            _register(connection, extraction, extracted[extraction.name])
            _validate(connection, source, extraction)

        written = {
            table.name: _write(connection, table.name, table.sql(), output_dir)
            for table in source.tables
        }
    finally:
        connection.close()

    return Result(source=source.name, extractions=extracted, tables=written)


def _extract(source: Source, extraction: Extraction, cache_dir: Path, *, refresh: bool) -> Path:
    destination = cache.cached_path(cache_dir, source.name, extraction.filename)
    return extraction.fetch(extraction, destination, refresh=refresh)


def _register(connection: duckdb.DuckDBPyConnection, extraction: Extraction, path: Path) -> None:
    connection.execute(
        f'CREATE OR REPLACE VIEW "{extraction.name}" AS SELECT * FROM {extraction.read_sql(path)}'
    )


def _validate(connection: duckdb.DuckDBPyConnection, source: Source, extraction: Extraction) -> None:
    described = connection.execute(f'DESCRIBE SELECT * FROM "{extraction.name}"').fetchall()
    actual = {row[0]: row[1] for row in described}
    schema.validate(extraction.schema, actual, source=source.name, extraction=extraction.name)


def _write(
    connection: duckdb.DuckDBPyConnection, name: str, sql: str, output_dir: Path
) -> Path:
    destination = output_dir / f"{name}.parquet"
    escaped = str(destination).replace("'", "''")
    connection.execute(f"COPY ({sql}) TO '{escaped}' (FORMAT PARQUET)")
    return destination
