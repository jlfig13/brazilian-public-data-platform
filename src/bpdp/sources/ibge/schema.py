"""Declarar: o esquema esperado da Fonte IBGE.

Este é o contrato da política de falha ruidosa. Ele é declarado aqui, separado
do SQL de curadoria, para servir ao mesmo tempo de documentação do que o órgão
publica e de verificação executável do que ele entregou.

O endpoint de localidades do IBGE é consumido na visão ``nivelado``, que devolve
um JSON plano — uma linha por município, já com a UF e a região do município em
colunas próprias. Qualquer coluna a mais, a menos ou com tipo diferente derruba
a execução: é exatamente esse o alarme de mudança de layout.
"""

from __future__ import annotations

from ...schema import Column, Schema

MUNICIPIOS = Schema(
    columns=(
        Column("municipio-id", "BIGINT"),
        Column("municipio-nome", "VARCHAR"),
        Column("microrregiao-id", "BIGINT"),
        Column("microrregiao-nome", "VARCHAR"),
        Column("mesorregiao-id", "BIGINT"),
        Column("mesorregiao-nome", "VARCHAR"),
        Column("UF-id", "BIGINT"),
        Column("UF-sigla", "VARCHAR"),
        Column("UF-nome", "VARCHAR"),
        Column("regiao-id", "BIGINT"),
        Column("regiao-sigla", "VARCHAR"),
        Column("regiao-nome", "VARCHAR"),
    )
)
