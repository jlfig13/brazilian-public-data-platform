# brazilian-public-data-platform

Tabelas curadas de dados públicos brasileiros, em Parquet, produzidas por um
comando que roda igual na sua máquina e no CI — sem credencial e sem serviço.

Esta fatia entrega a dimensão **`municipio`** a partir da Fonte IBGE: código do
IBGE de 7 dígitos como chave, nome do município e sigla da UF como atributos.

## Da clonagem à primeira execução

```bash
git clone https://github.com/jlfig13/brazilian-public-data-platform.git
cd brazilian-public-data-platform
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

bpdp list                 # Fontes registradas
bpdp run ibge             # baixa, valida e escreve data/tables/municipio.parquet
```

A Extração vai para `data/cache/` e a Tabela curada para `data/tables/`. Nada
disso é versionado (ADR-0002): uma Extração já baixada é reaproveitada nas
execuções seguintes, e `--refresh` força baixar de novo.

Sem rede? Rode sobre as amostras versionadas:

```bash
bpdp run ibge --cache-dir tests/samples --output-dir /tmp/tables
```

## Testes

```bash
pytest
```

A suíte roda em segundos e não toca a rede: ela executa o pipeline com o cache
de Extração apontado para `tests/samples/` e observa apenas os Parquet que saem.

## Anatomia de uma Fonte

Cada Fonte é um pacote em `src/bpdp/sources/<fonte>/` com três partes:

| Parte | Onde | O que faz |
| --- | --- | --- |
| **Extrair** | `extract.py` | Declara os arquivos publicados pelo órgão e como lê-los. Nada é transformado. |
| **Declarar** | `schema.py` | Declara colunas e tipos esperados. É o contrato da política de falha. |
| **Curar** | `curate/*.sql` | SQL DuckDB que produz cada Tabela curada, com os nomes de `CONTEXT.md`. |

O `__init__.py` da Fonte junta as três partes em um `Source`, e
`src/bpdp/registry.py` é o registro central que a entrada consulta. Adicionar a
próxima Fonte é preencher esse molde e registrá-la — a orquestração
(`src/bpdp/pipeline.py`) não muda.

## Política de falha

Toda Extração é validada contra o esquema declarado **antes** de qualquer Tabela
curada ser escrita. Divergência derruba a execução, e a mensagem diz qual Fonte,
qual coluna e qual a natureza da divergência:

```
Fonte 'ibge', extração 'ibge_municipios': o que a Fonte entregou diverge do esquema declarado.
  - coluna ausente: 'UF-sigla' (esperada como VARCHAR)
```

## Vocabulário

Nomes de tabela e coluna seguem o glossário em [`CONTEXT.md`](CONTEXT.md);
código é em inglês. Decisões de arquitetura estão em [`docs/adr/`](docs/adr).
