"""A política de falha ruidosa, observada pela mesma porta do CI.

Quando o que a Fonte entregou diverge do esquema declarado, a execução cai antes
de escrever qualquer Tabela curada — a Publicação anterior, velha porém correta,
continua sendo a verdade.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bpdp import cli, pipeline, registry
from bpdp.schema import SchemaViolation

pytestmark = pytest.mark.usefixtures("no_network")

EXTRACTION = Path("ibge") / "municipios.json"


def rewrite_sample(cache_dir: Path, mutate) -> None:
    path = cache_dir / EXTRACTION
    rows = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(
        json.dumps([mutate(dict(row)) for row in rows], ensure_ascii=False), encoding="utf-8"
    )


def run(cache_dir: Path, output_dir: Path) -> None:
    pipeline.run(registry.get("ibge"), cache_dir=cache_dir, output_dir=output_dir)


def test_a_missing_column_fails_the_run(cache_dir: Path, output_dir: Path) -> None:
    rewrite_sample(cache_dir, lambda row: {k: v for k, v in row.items() if k != "UF-sigla"})

    with pytest.raises(SchemaViolation) as failure:
        run(cache_dir, output_dir)

    message = str(failure.value)
    assert "'ibge'" in message
    assert "UF-sigla" in message
    assert "ausente" in message


def test_a_renamed_column_names_both_the_missing_and_the_unexpected_one(
    cache_dir: Path, output_dir: Path
) -> None:
    def rename(row: dict) -> dict:
        row["uf_sigla"] = row.pop("UF-sigla")
        return row

    rewrite_sample(cache_dir, rename)

    message = str(pytest.raises(SchemaViolation, run, cache_dir, output_dir).value)
    assert "coluna ausente: 'UF-sigla'" in message
    assert "coluna inesperada: 'uf_sigla'" in message


def test_a_changed_type_names_the_column_and_both_types(
    cache_dir: Path, output_dir: Path
) -> None:
    def stringify_code(row: dict) -> dict:
        row["municipio-id"] = str(row["municipio-id"])
        return row

    rewrite_sample(cache_dir, stringify_code)

    message = str(pytest.raises(SchemaViolation, run, cache_dir, output_dir).value)
    assert "municipio-id" in message
    assert "BIGINT" in message and "VARCHAR" in message


def test_no_curated_table_is_written_when_the_schema_diverges(
    cache_dir: Path, output_dir: Path
) -> None:
    rewrite_sample(cache_dir, lambda row: {k: v for k, v in row.items() if k != "municipio-nome"})

    with pytest.raises(SchemaViolation):
        run(cache_dir, output_dir)

    assert list(output_dir.iterdir()) == []


def test_the_entry_point_reports_the_divergence_and_fails(
    capsys: pytest.CaptureFixture[str], cache_dir: Path, output_dir: Path
) -> None:
    rewrite_sample(cache_dir, lambda row: {k: v for k, v in row.items() if k != "UF-sigla"})

    exit_code = cli.main(
        ["run", "ibge", "--cache-dir", str(cache_dir), "--output-dir", str(output_dir)]
    )

    assert exit_code == 1
    stderr = capsys.readouterr().err
    assert "UF-sigla" in stderr
    assert "Nenhuma Tabela curada foi escrita." in stderr
