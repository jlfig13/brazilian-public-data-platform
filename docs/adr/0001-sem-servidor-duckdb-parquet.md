# Pipeline sem servidor: Python, DuckDB, Parquet e GitHub Actions

A plataforma processa dezenas de milhões de linhas, o que normalmente pede um banco
analítico e um orquestrador (Postgres/BigQuery + Airflow). Decidimos não ter nenhum
dos dois: o processamento é Python + DuckDB sobre arquivos Parquet, disparado pelo
GitHub Actions, sem serviço rodando entre as execuções.

## Considered Options

- **Banco analítico gerenciado + Airflow**: o caminho óbvio, e o motivo de este ADR
  existir. Rejeitado por custo recorrente e por exigir operação contínua antes de a
  plataforma ter qualquer usuário.
- **Notebooks locais sem automação**: barato, mas não reproduzível nem agendável, e
  fecharia a porta para virar ferramenta interna.

## Consequences

- O ambiente local e o de CI são o mesmo: qualquer pessoa reproduz uma Publicação
  inteira num laptop, sem credencial.
- Não há estado entre execuções. Toda Publicação é reconstruída a partir das
  Extrações; não existe "atualizar uma linha".
- O teto é a memória de um runner do Actions. Se uma Fonte crescer além disso, o
  processamento precisa ser fatiado — não é motivo para trocar a arquitetura.
