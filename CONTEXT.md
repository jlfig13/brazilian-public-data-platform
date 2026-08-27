# Plataforma de Dados Públicos Brasileiros

Camada de ingestão e cruzamento de dados públicos brasileiros no eixo
empresa × trabalho × território. Existe para que cada análise nova não recomece o
trabalho de baixar, decodificar e juntar as mesmas bases.

## Language

### Fontes e ingestão

**Fonte**:
Um órgão publicador e o conjunto de arquivos que ele mantém sob um mesmo layout
(Receita Federal/CNPJ, IBGE, Novo CAGED, ComexStat).
_Avoid_: dataset, base, origem

**Extração**:
Uma cópia dos arquivos de uma Fonte tal como ela os publicou, sem transformação.
É descartável: sempre reconstruível a partir da Fonte.
_Avoid_: raw, bronze, dado bruto

**Tabela curada**:
Uma tabela publicada pela plataforma, com esquema estável, tipos corrigidos e
vocabulário deste glossário. É o que os consumidores leem.
_Avoid_: silver, gold, tabela final, dado tratado

**Publicação**:
O ato de tornar um conjunto de Tabelas curadas disponível para consumo, identificado
pela data em que ocorreu.
_Avoid_: release, build, deploy, carga

### Empresas e território

**Empresa**:
A pessoa jurídica identificada pela raiz do CNPJ (8 primeiros dígitos). Não tem
endereço nem atividade próprios — quem os tem é o Estabelecimento.
_Avoid_: matriz, companhia, firma, CNPJ

**Estabelecimento**:
A unidade física identificada pelo CNPJ completo (14 dígitos). É a unidade que tem
município, CNAE e vínculos de emprego, e portanto a unidade de toda análise
territorial ou setorial.
_Avoid_: filial, unidade, local, CNPJ

**CNAE**:
O código de atividade econômica declarado por um Estabelecimento.
_Avoid_: setor, ramo, atividade

**Município**:
Um município brasileiro identificado pelo código do IBGE (7 dígitos). O código do
IBGE é a única chave territorial da plataforma; nomes de município e siglas de UF
são atributos, nunca chaves.
_Avoid_: cidade, localidade, código TOM, código SIAFI

### Trabalho

**Movimentação**:
Uma admissão ou um desligamento declarado por um Estabelecimento em um mês de
referência, conforme o Novo CAGED. É um evento, não um estoque.
_Avoid_: vínculo, emprego, contratação

**Saldo**:
Admissões menos desligamentos em um recorte (Município, CNAE, mês). É a variação
do estoque de emprego, não o estoque em si.
_Avoid_: emprego, estoque, headcount
