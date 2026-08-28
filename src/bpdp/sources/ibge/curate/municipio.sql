-- Curar: a dimensão `municipio`.
--
-- Grão: um município do IBGE. A chave é o código do IBGE de 7 dígitos; nome do
-- município e sigla da UF são atributos, nunca chaves de junção.
SELECT
    CAST("municipio-id" AS INTEGER) AS codigo_municipio,
    "municipio-nome"                AS nome_municipio,
    "UF-sigla"                      AS sigla_uf
FROM ibge_municipios
ORDER BY codigo_municipio
