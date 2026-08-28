"""A Fonte IBGE de ponta a ponta, observada apenas pelos Parquet que produz."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pytest

from bpdp import cli, pipeline, registry

pytestmark = pytest.mark.usefixtures("no_network")


@pytest.fixture
def municipio(cache_dir: Path, output_dir: Path) -> Path:
    result = pipeline.run(registry.get("ibge"), cache_dir=cache_dir, output_dir=output_dir)
    return result.tables["municipio"]


def query(parquet: Path, sql: str) -> list[tuple]:
    escaped = str(parquet).replace("'", "''")
    with duckdb.connect() as connection:
        return connection.execute(sql.format(t=f"read_parquet('{escaped}')")).fetchall()


def test_source_writes_only_the_municipio_table(municipio: Path, output_dir: Path) -> None:
    assert municipio.exists()
    assert sorted(path.name for path in output_dir.iterdir()) == ["municipio.parquet"]


def test_municipio_has_the_declared_columns_and_types(municipio: Path) -> None:
    described = query(municipio, "DESCRIBE SELECT * FROM {t}")
    assert [(row[0], row[1]) for row in described] == [
        ("codigo_municipio", "INTEGER"),
        ("nome_municipio", "VARCHAR"),
        ("sigla_uf", "VARCHAR"),
    ]


def test_municipio_grain_is_one_row_per_seven_digit_ibge_code(
    municipio: Path, samples_dir: Path
) -> None:
    sample = json.loads((samples_dir / "ibge" / "municipios.json").read_text(encoding="utf-8"))
    rows, distinct_codes, seven_digits = query(
        municipio,
        "SELECT count(*), count(DISTINCT codigo_municipio),"
        " count(*) FILTER (codigo_municipio BETWEEN 1000000 AND 9999999) FROM {t}",
    )[0]
    assert rows == len(sample)
    assert distinct_codes == rows
    assert seven_digits == rows


def test_municipio_carries_name_and_uf_as_attributes(municipio: Path) -> None:
    assert query(
        municipio,
        "SELECT * FROM {t} WHERE codigo_municipio IN (3550308, 2611606) ORDER BY codigo_municipio",
    ) == [
        (2611606, "Recife", "PE"),
        (3550308, "São Paulo", "SP"),
    ]


@pytest.mark.parametrize(
    ("codigo", "nome", "sigla_uf"),
    [
        (2100055, "Açailândia", "MA"),
        (1507300, "São Félix do Xingu", "PA"),
        (3202801, "Itaguaçu", "ES"),
        (3539806, "Poá", "SP"),
    ],
)
def test_accented_municipality_names_survive_the_pipeline(
    municipio: Path, codigo: int, nome: str, sigla_uf: str
) -> None:
    assert query(municipio, f"SELECT * FROM {{t}} WHERE codigo_municipio = {codigo}") == [
        (codigo, nome, sigla_uf)
    ]


def test_a_cached_extraction_is_reused_without_downloading_again(
    cache_dir: Path, output_dir: Path
) -> None:
    # `no_network` já falharia qualquer download; rodar duas vezes mostra que a
    # segunda execução também se serve do cache.
    for _ in range(2):
        pipeline.run(registry.get("ibge"), cache_dir=cache_dir, output_dir=output_dir)
    assert (output_dir / "municipio.parquet").exists()


def test_the_entry_point_runs_the_source_by_name(
    capsys: pytest.CaptureFixture[str], cache_dir: Path, output_dir: Path
) -> None:
    exit_code = cli.main(
        ["run", "ibge", "--cache-dir", str(cache_dir), "--output-dir", str(output_dir)]
    )
    assert exit_code == 0
    assert "municipio" in capsys.readouterr().out
    assert (output_dir / "municipio.parquet").exists()


def test_the_registry_discovers_the_source_without_naming_it_in_the_pipeline() -> None:
    assert "ibge" in registry.names()
