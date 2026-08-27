# Tabelas curadas são publicadas como assets de release, não versionadas no Git

O Git guarda toda versão de todo arquivo para sempre e rejeita arquivos acima de
100MB, então commitar Parquet a cada Publicação inflaria o repositório
irreversivelmente. As Tabelas curadas são publicadas como assets de release do
GitHub (até 2GB por arquivo, sem custo), com tag pela data da Publicação; o
repositório guarda apenas código.

## Consequences

- Consumidores leem por URL e conseguem fixar uma Publicação antiga; o Power BI
  consome o Parquet direto do release.
- Extrações nunca são versionadas nem publicadas: são cache local descartável.
- Esta decisão pressupõe que o cruzamento pode ser divulgado publicamente. Se
  alguma Fonte ou combinação passar a ter restrição de divulgação, o armazém precisa
  mudar para um bucket privado e este ADR deve ser substituído.
