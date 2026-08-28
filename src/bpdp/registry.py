"""The central registry of available sources.

The entry point asks the registry which sources exist; it never names one.
Adding the next source is adding it to :data:`SOURCES`, with no change to the
orchestration.
"""

from __future__ import annotations

from .source import Source
from .sources.ibge import SOURCE as IBGE

SOURCES: dict[str, Source] = {source.name: source for source in (IBGE,)}


class UnknownSource(Exception):
    pass


def get(name: str) -> Source:
    try:
        return SOURCES[name]
    except KeyError:
        known = ", ".join(sorted(SOURCES)) or "nenhuma"
        raise UnknownSource(f"Fonte desconhecida: {name!r}. Fontes registradas: {known}.") from None


def names() -> list[str]:
    return sorted(SOURCES)
