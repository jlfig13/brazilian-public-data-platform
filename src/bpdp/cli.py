"""The single entry point: run a source, or list the ones registered."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import cache, registry
from .pipeline import DEFAULT_OUTPUT_DIR, run
from .registry import UnknownSource
from .schema import SchemaViolation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bpdp", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    run_command = commands.add_parser("run", help="executa uma Fonte de ponta a ponta")
    run_command.add_argument("source", help=f"Fonte a executar ({', '.join(registry.names())})")
    run_command.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="diretório do cache de Extração (padrão: data/cache, ou $BPDP_CACHE_DIR)",
    )
    run_command.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="diretório onde as Tabelas curadas são escritas em Parquet",
    )
    run_command.add_argument(
        "--refresh",
        action="store_true",
        help="baixa de novo mesmo que a Extração já esteja no cache",
    )

    commands.add_parser("list", help="lista as Fontes registradas")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "list":
        for name in registry.names():
            print(f"{name}\t{registry.get(name).description}")
        return 0

    try:
        source = registry.get(args.source)
    except UnknownSource as error:
        print(error, file=sys.stderr)
        return 2

    cache_dir = args.cache_dir if args.cache_dir is not None else cache.default_cache_dir()
    try:
        result = run(
            source, cache_dir=cache_dir, output_dir=args.output_dir, refresh=args.refresh
        )
    except SchemaViolation as error:
        print(error, file=sys.stderr)
        print("Nenhuma Tabela curada foi escrita.", file=sys.stderr)
        return 1

    for name, path in result.tables.items():
        print(f"{name} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
