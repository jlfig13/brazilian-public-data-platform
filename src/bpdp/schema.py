"""Declared schemas for source extractions, and the noisy-failure policy.

A schema is the contract between what an agency actually publishes and what the
curation SQL is allowed to assume. It is declared next to the source, away from
the curation code, so it doubles as documentation and as a verifiable contract.
"""

from __future__ import annotations

from dataclasses import dataclass


class SchemaViolation(Exception):
    """Raised when an extraction diverges from the schema declared for it.

    The message always names the source, the column and the nature of the
    divergence, so a failure can be diagnosed without opening the raw file.
    """


@dataclass(frozen=True)
class Column:
    """A column expected in an extraction, with its expected DuckDB type."""

    name: str
    type: str

    def matches(self, actual_type: str) -> bool:
        return self.type.upper() == actual_type.upper()


@dataclass(frozen=True)
class Schema:
    """The full set of columns expected in an extraction."""

    columns: tuple[Column, ...]

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.columns)


def validate(schema: Schema, actual: dict[str, str], *, source: str, extraction: str) -> None:
    """Compare an extraction against its declared schema, or fail loudly.

    ``actual`` maps the column names found in the extraction to their DuckDB
    types. Every divergence found is reported at once, so a layout change is
    diagnosed in a single run instead of one failure at a time.
    """
    problems: list[str] = []

    for column in schema.columns:
        if column.name not in actual:
            problems.append(f"coluna ausente: {column.name!r} (esperada como {column.type})")
        elif not column.matches(actual[column.name]):
            problems.append(
                f"tipo divergente na coluna {column.name!r}: "
                f"esperado {column.type}, encontrado {actual[column.name]}"
            )

    for name in actual:
        if name not in schema.names:
            problems.append(f"coluna inesperada: {name!r} (encontrada como {actual[name]})")

    if problems:
        raise SchemaViolation(
            f"Fonte {source!r}, extração {extraction!r}: "
            f"o que a Fonte entregou diverge do esquema declarado.\n  - "
            + "\n  - ".join(problems)
        )
