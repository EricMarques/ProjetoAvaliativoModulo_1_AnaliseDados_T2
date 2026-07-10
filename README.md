# Análise de Dados com Python [T2]

## Projeto Avaliativo - Módulo 1

### Aluno: Eric Felipe Barros Marques
### Turma: Análise de Dados com Python [T2]

### 1. CONTEXTUALIZAÇÃO

Você está desenvolvendo uma Análise Exploratória de Dados (AED) aplicada ao varejo para aprender como transformar dados brutos em informações úteis.

A base “Varejo” contém registros reais de compras (datas, clientes, produtos, categorias e valores). Aprender a verificar qualidade, limpar e sumarizar esses dados é uma habilidade prática essencial para quem trabalha com BI e Visualização de Dados.<br>
Neste mini-projeto você vai praticar tarefas comuns no trabalho: identificar problemas nos dados (valores nulos, tipos incorretos, duplicados), tratar esses problemas com ferramentas como pandas e gerar estatísticas  simples e funções de agrupamento, para responder perguntas operacionais (quem compra mais, quais categorias vendem mais, como variam as vendas ao longo do tempo).

O objetivo educacional é que, ao final, você saiba preparar uma base para análises mais avançadas ou para alimentar um dashboard: entender os dados, limpá-los, extrair estatísticas descritivas e comunicar os principais insights de forma objetiva.

 
### 2. DESAFIO

Entregar um script em Python que realize uma **Análise Exploratória** da base `viagens_2025_6meses` seguindo etapas claras, documentadas e reproduzíveis.

#### Etapas obrigatórias

- Carregar a base Varejo.csv com pandas e mostrar: número de registros, colunas e tipos de dados
- Verificar e reportar ao menos dois problemas básicos: valores nulos por coluna, duplicatas, possíveis inconsistências( ex.: datas inválidas ou categorias vazias)
- Fazer as três etapas de limpeza mínima necessária: remover ou imputar nulos (explicar a escolha), eliminar duplicatas relevantes e ajustar tipos de dados (ex.: converter coluna DATA para datetime)
- Gerar estatísticas descritivas básicas para a coluna de número de filhos do cliente (média, mediana, desvio padrão, moda, máximo, mínimo, contagem, quartis)
- Explorar padrões de agrupamento **com pelo menos dois agrupamentos** (por exemplo: gênero com mais vendas, compras), usando groupby() ou pivot_table().
- Produzir um pequeno bloco de conclusões **(3–6 tópicos)** com os principais insights obtidos e possíveis problemas remanescentes na base.

#### Requisitos técnicos mínimos

- O script deve ser executável em VsCode ou Google Colab (arquivo .py).

- Usar pandas; outras bibliotecas são opcionais (NumPy, Matplotlib, Seaborn).


### 6. Execussão do projeto
### Tecnologias utilizadas
- Python
- Pandas

#### Importação da base de dados

A base de dados será baixada de forma automática onde esta está alocada em um diretório do Google Drive

### Execução do projeto
Primeiramente deve-se instalar as dependências utilizando o comando `pip install requirements.txt`

### Limpeza de Dados
Para a limpeza dos dados foram efetuados os seguintes procedimentos:

- Remoção de colunas totalmente vazias (Unnamed: 10 - 13);
- Identificação e remoção de registros duplicados;
- Limpeza de linhas onde as colunas PR_CAT e PR_NOME possuíam valor #N/D
- Conversão das informações da coluna `data` de string para date.
- Padronização dos textos das colunas PR_CAT e PR_NOME pata str.title


## Análise Exploratória dos dados da base `viagens_2025_6meses`

O foco desta análise é identificar possíveis anomalias nos dados, efetuar tratamento  e limpeza destes dados inconsistentes.

A base de dados refere-se a uma relação de compras efetuadas por clientes.

### Informações sobre a base de dados
#### Dimensão
<table>
  <thead>
    <tr>
        <th>Nº</th>
        <th>Informativo</th>
        <th>Quantidade</th>
    </tr>
  </thead>
  <tbody>
    <tr>
        <td>1</td>
        <td>Linhas</td>
        <td>830000</td>
    </tr>
    <tr>
        <td>2</td>
        <td>Colunas</td>
        <td>14</td>
    </tr>
  </tbody>
</table>

#### Tipos de dados
<table>
  <thead>
    <tr>
        <th colspan="2">TIPOS DE DADOS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
        <td>DATA</td>
        <td>str</td>
    </tr>
    <tr>
        <td>CO_ID</td>
        <td>int64</td>
    </tr>
        <tr>
        <td>CL_ID</td>
        <td>int64</td>
    </tr>
        <tr>
        <td>CL_GENERO</td>
        <td>str</td>
    </tr>
        <tr>
        <td>CL_EC</td>
        <td>int64</td>
    </tr>
        <tr>
        <td>CL_FLH</td>
        <td>int64</td>
    </tr>
        <tr>
        <td>CL_SEG</td>
        <td>str</td>
    </tr>
        <tr>
        <td>PR_ID</td>
        <td>int64</td>
    </tr>
        <tr>
        <td>PR_CAT</td>
        <td>str</td>
    </tr>
        <tr>
        <td>PR_NOME</td>
        <td>str</td>
    </tr>
    <tr>
        <td>Unnamed: 10</td>
        <td>float64</td>
    </tr>
    <tr>
        <td>Unnamed: 11</td>
        <td>float64</td>
    </tr>
    <tr>
        <td>Unnamed: 12</td>
        <td>float64</td>
    </tr>
    <tr>
        <td>Unnamed: 13</td>
        <td>float64</td>
    </tr>
  </tbody>
</table>

#### Colunas totalmente vazias(lixo)
Unnamed: 10, Unnamed: 11, Unnamed: 12 e Unnamed: 13

#### Registros nulos
<table>
  <thead>
    <tr>
        <th>Tipo de dado</th>
        <th>Qtd. Nulos</th>
        <th>%</th>
    </tr>
  </thead>
  <tbody>
    <tr>
        <td>DATA</td>
        <td>0</td>
        <td>0.0</td>
    </tr>
    <tr>
        <td>CO_ID</td>
        <td>0</td>
        <td>0.0</td>
    </tr>
        <tr>
        <td>CL_ID</td>
        <td>0</td>
        <td>0.0</td>
    </tr>
        <tr>
        <td>CL_GENERO</td>
        <td>0</td>
        <td>0.0</td>
    </tr>
        <tr>
        <td>CL_EC</td>
        <td>0</td>
        <td>0.0</td>
    </tr>
        <tr>
        <td>CL_FLH</td>
        <td>0</td>
        <td>0.0</td>
    </tr>
        <tr>
        <td>CL_SEG</td>
        <td>0</td>
        <td>0.0</td>
    </tr>
        <tr>
        <td>PR_ID</td>
        <td>0</td>
        <td>0.0</td>
    </tr>
        <tr>
        <td>PR_CAT</td>
        <td>0</td>
        <td>0.0</td>
    </tr>
        <tr>
        <td>PR_NOME</td>
        <td>0</td>
        <td>0.0</td>
    </tr>
    <tr>
        <td>Unnamed: 10</td>
        <td>8300000</td>
        <td>100.00</td>
    </tr>
    <tr>
        <td>Unnamed: 11</td>
        <td>8300000</td>
        <td>100.00</td>
    </tr>
    <tr>
        <td>Unnamed: 12</td>
        <td>8300000</td>
        <td>100.00</td>
    </tr>
    <tr>
        <td>Unnamed: 13</td>
        <td>8300000</td>
        <td>100.00</td>
    </tr>
  </tbody>
</table>

#### Duplicidades
Foram identificadas 96.553 linhas duplicadas (11.63% da base).

Considerando que a recorrência de um mesmo produto em um pedido pode indicar a compra de múltiplas unidades, esses registros foram mantidos para evitar impactos nas análises de vendas e comportamento de consumo.

### Análises Exploratórias:
#### Análises




### Conclusões
- CONCLUSÃO 1

### Sugestões para Análises Futuras
- SUGESTÕES 1