"""Extrair: os arquivos publicados pelo IBGE.

Nada é transformado aqui. O arquivo publicado pelo órgão vai para o cache local
como veio, e uma Extração já baixada é reaproveitada nas execuções seguintes.
"""

from __future__ import annotations

from ...source import Extraction
from .schema import MUNICIPIOS

MUNICIPIOS_URL = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?view=nivelado"
)

EXTRACTIONS = (
    Extraction(
        name="ibge_municipios",
        url=MUNICIPIOS_URL,
        filename="municipios.json",
        relation_sql="read_json('{path}', format='array')",
        schema=MUNICIPIOS,
    ),
)
