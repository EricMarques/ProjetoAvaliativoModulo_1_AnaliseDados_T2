# 📊 Análise de Dados com Python [T2]
## Projeto Avaliativo - Módulo 1 - Semana 13

**Aluno:** Eric Felipe Barros Marques  
**Turma:** Análise de Dados com Python [T2]  
**Data de Entrega:** 20/07/2026 às 22h  
**Status:** ✅ Projeto Completo

---

## 📋 Índice
1. [Contextualização](#1-contextualização)
1. [Desafio e Perguntas de Negócio](#2-desafio-e-perguntas-de-negócio)
1. [Resultados Esperados](#3-resultados-esperados-entrega)
1. [Requisitos da Aplicação](#4-requisitos-da-aplicação)
1. [Tecnologias Utilizadas](#5-tecnologias-utilizadas)
1. [Arquitetura Medallion](#6-arquitetura-medallion)
1. [Estrutura do Projeto](#7-estrutura-do-projeto)
1. [Instalação e Execução](#8-instalação-e-execução)
1. [Análises e Gráficos](#9-análises-e-gráficos)
1. [Auditoria e Qualidade de Dados](#10-auditoria-e-qualidade-de-dados)
1. [Conclusões](#10-conclusões)
1. [Sugestões Futuras](#11-sugestões-futuras)

---

## 1. CONTEXTUALIZAÇÃO

Atualmente, a **transparência pública** permite a geração de grandes volumes de dados abertos. Um exemplo é a base de **Viagens a Serviço do Portal da Transparência do Governo Federal**.

Este projeto **simula uma consultoria de dados** contratada pelo governo para aumentar a transparência dos gastos públicos com viagens. Os dados chegam **brutos, desorganizados**, e a equipe precisa avaliar como anda o fluxo das informações.

### Objetivo Principal

Construir um **pipeline de dados completo (ETL)** seguindo a **Arquitetura Medallion** que:

✅ Baixe automaticamente dados da fonte oficial (Google Drive)  
✅ Preserve o histórico original na camada Raw (auditoria e rastreabilidade)  
✅ Limpe, normalize e transforme os dados na camada Silver  
✅ Responda perguntas de negócio com análises e visualizações na camada Gold  

### Competência Desenvolvida

Dominar um **pipeline de dados (ETL)** e a **Arquitetura Medallion** com Python e SQL é uma das competências mais valorizadas na área de dados, pois permite utilização eficiente e segura.

---

## 2. DESAFIO E PERGUNTAS DE NEGÓCIO

O pipeline foi desenvolvido para responder às seguintes **8 perguntas de negócio**:

| # | Pergunta | Análise |
|---|----------|---------|
| 1️⃣ | Quais os **5 órgãos com maior custo total**? | Identifica principais gastadores |
| 2️⃣ | Quais os **3 destinos com maior custo médio** por viagem? | Revela destinos mais caros |
| 3️⃣ | Qual a **viagem de maior duração** e seu custo? | Detecta outliers de tempo |
| 4️⃣ | Qual o **tipo de pagamento com maior valor médio**? | Compara modalidades |
| 5️⃣ | Qual o **meio de transporte mais usado** nos trechos? | Analisa mobilidade preferida |
| 6️⃣ | Qual **UF de destino aparece em mais trechos**? | Concentração geográfica |
| 7️⃣ | Qual **órgão pagou mais** no total? | Principal pagador |

---

## 3. RESULTADOS ESPERADOS (ENTREGA)

Ao final do projeto, foi construído um **pipeline completo** que:

### ✅ Fase 1: Extração e Camada Raw
- Baixa dados de Viagens a Serviço direto da fonte oficial (Google Drive)
- Preserva o dado original fielmente, garantindo rastreabilidade e auditoria
- 4 tabelas Raw com todas as colunas VARCHAR

### ✅ Fase 2: Transformação e Camada Silver
- Limpa e organiza os dados com:
  - Tipagem correta (DECIMAL, DATE, VARCHAR, INT)
  - Integridade referencial entre as tabelas (PK, FK)
  - Eliminação de inconsistências, duplicidades e erros de formato
  - **8 constraints** (NOT NULL, CHECK, UNIQUE) distribuídos entre as 4 tabelas

### ✅ Fase 3: Análise e Camada Gold
- Responde perguntas de negócio reais com:
  - Consultas SQL com agregações (JOIN + GROUP BY)
  - Tabelas e VIEWs criadas no MySQL
  - Gráficos de dataviz com elementos estruturais (título, eixos, legendas)
  - Análises apoiadas em evidências dos dados

---

## 4. REQUISITOS DA APLICAÇÃO

### Fase 0 - Banco e Tabelas (`0_criar_banco.sql`)

✅ Criar o database `viagens_analise`  
✅ Criar **4 tabelas Raw** (todas as colunas VARCHAR, sem constraints):
- `raw_viagem`, `raw_passagem`, `raw_pagamento`, `raw_trecho`

✅ Criar **4 tabelas Silver** (tipadas, com PK, FK e constraints):
- `silver_viagem`, `silver_passagem`, `silver_pagamento`, `silver_trecho`

**Constraints obrigatórios (8 no total):**

| Tabela | Constraint 1 | Constraint 2 |
|--------|-------------|-------------|
| `silver_viagem` | NOT NULL `nome_orgao_superior` | CHECK `valor_diarias >= 0` |
| `silver_passagem` | CHECK `valor_passagem >= 0` | CHECK `taxa_servico >= 0` |
| `silver_pagamento` | NOT NULL `tipo_pagamento` | CHECK `valor >= 0` |
| `silver_trecho` | UNIQUE `(id_viagem, sequencia_trecho)` | CHECK `numero_diarias >= 0` |

### Fase 1 - Extração e Camada Raw (`1_extrair.py`)

✅ Baixar arquivo `.zip` do Google Drive automaticamente  
✅ Ler os **4 CSVs** em blocos:
- `2025_Viagem.csv`, `2025_Pagamento.csv`, `2025_Passagem.csv`, `2025_Trecho.csv`

✅ Carregar nas tabelas Raw **sem alterar conteúdo**  
✅ Processo **idempotente** (TRUNCATE antes de carregar)  
✅ **Resiliente** com try/except para tratamento de erros  
✅ Configuração: Separador `;` | Encoding `latin-1` | Decimal `,` | Data `DD/MM/AAAA`

### Fase 2 - Transformação e Camada Silver (`2_transformar.py`)

✅ Copiar dados de Raw para Silver **convertendo tipos:**
- Texto → DECIMAL (ex.: `"1.234,50"` → `1234.50`)
- Texto → DATE (ex.: `"30/06/2025"` → `2025-06-30`)
- Campos vazios → NULL

✅ Respeitar **integridade referencial** (PK, FK)  
✅ Calcular colunas derivadas:
- `valor_total = diarias + passagens + outros - devoluções`
- `duracao_dias = DATEDIFF(data_fim, data_inicio)`

✅ Validar dados (CHECK constraints)

### Fase 3 - Camada Gold (`3_analise.ipynb`)

✅ Responder **6+ perguntas de negócio** com:
- Consultas SQL com agregações
- Tabelas e VIEWs no MySQL
- Gráficos com dataviz aplicado

✅ Construir **camada Gold agregada** com:
- Junção de tabelas (JOIN)
- Agrupamento de dados (GROUP BY)
- Visualizações profissionais

---

## 5. TECNOLOGIAS UTILIZADAS

| Tecnologia |  Propósito |
|------------|----------|
| **Python** |  Linguagem principal |
| **MySQL** | Banco de dados relacional |
| **Pandas** | Manipulação de dados |
| **Matplotlib** | Geração de gráficos |
| **GDown** | Download do Google Drive |
| **mysql-connector-python** |  Conexão MySQL |
| **python-dotenv** | Gerenciamento de .env |

---

## 6. ARQUITETURA MEDALLION

A arquitetura segue o padrão **Medallion** (3 camadas) amplamente utilizado em Data Engineering:

```
                    CSV (Fonte Oficial)
                           ↓
            ╔═══════════════╩═══════════════╗
            ║                               ║
            ↓                               ↓
       CAMADA RAW                    CAMADA SILVER
    (Dados Brutos)              (Dados Limpos & Tipados)
     4 tabelas                       4 tabelas
   (todas VARCHAR)           (VARCHAR, DECIMAL, DATE)
     Sem constraints          (PK, FK, Constraints)
   ✓ Auditoria                       ↓
   ✓ Rastreabilidade          Validações
   ✓ Histórico fiel           Conversões
                              Cálculos
                                    ↓
                              CAMADA GOLD
                         (Análises & Gráficos)
                          Agregações
                          JOINs
                          GROUP BY
                          VIEWs
                          📊 Gráficos
```

---

## 7. ESTRUTURA DO PROJETO

```
Projeto Avaliativo Modulo 1/
│
├── 📄 .env                      # Credenciais "Oficiais" do Ambiente/MySQL
├── 📄 .env.example              # Modelo de .env (commitar)
├── 📄 .gitignore                # Ignora .env, .zip, .csv, data/
│
├── 🐍 config.py                 # Parâmetros + leitura .env
├── 🐍 banco.py                  # Funções conexão MySQL
├── 📄 requirements.txt          # Dependências
│
├── 🐍 0_criar_banco.py          # Criação database + 8 tabelas
├── 🐍 1_extrair.py              # Fase 1: Download + Carga RAW
├── 🐍 2_transformar.py          # Fase 2: Limpeza → SILVER
├── 🐍 3_analise.py              # Fase 3: Análise → GOLD
├── 🐍 auditoria.py              # Dados sobre toda base de dados(Demora muito para executar) 
│
├── 📁 data/                     # Dados (ignorado no git)
│   └── viagens_2025_6meses.zip
│
├── 📁 images/                   # Gráficos gerados
│   ├── 01_top5_orgaos.png
│   ├── 02_top3_destinos.png
│   ├── 03_maior_duracao.png
│   ├── 04_tipo_pagamento.png
│   ├── 05_meio_transporte.png
│   ├── 06_destino_uf.png
│   └── 07_orgao_pagador.png
│   └── 08_sigilo_nome_viajante.png
│
└── 📄 README.md                 # Arquivo contendo informações do projeto
```

---

## 8. INSTALAÇÃO E EXECUÇÃO

### Pré-requisitos

- Python 3.8+
- MySQL  8.0+
- Git

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/EricMarques/ProjetoAvaliativoModulo_1_AnaliseDados_T2.git
cd Projeto\ Avaliativo\ Modulo\ 1
```

### Passo 2: Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=viagens_analise
DRIVE_FILE_ID=seu_id_arquivo_drive
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Executar o Pipeline

**Criar banco e tabelas:**
```bash
# Execute o SQL em seu cliente MySQL
mysql -u root -p < 0_criar_banco.sql
```

**Fase 1 - Extrair (RAW):**
```bash
python 1_extrair.py
```

**Fase 2 - Transformar (SILVER):**
```bash
python 2_transformar.py
```

**Fase 3 - Analisar (GOLD):**
```bash
python 3_analise.py
```

---

## 9. ANÁLISES E GRÁFICOS

### Pergunta 1: Top 5 Órgãos com Maior Custo
📊 **Gráfico:** Barras horizontais  
📁 **Arquivo:** `01_top5_orgaos.png`  
📌 **Insight:** Identifica principais gastadores

### Pergunta 2: Top 3 Destinos com Maior Custo Médio
📊 **Gráfico:** Barras horizontais  
📁 **Arquivo:** `02_top3_destinos.png`  
📌 **Insight:** Revela destinos mais caros

### Pergunta 3: Viagem de Maior Duração
📊 **Gráfico:** Barra única  
📁 **Arquivo:** `03_maior_duracao.png`  
📌 **Insight:** Detecta outliers

### Pergunta 4: Tipo de Pagamento com Maior Valor Médio
📊 **Gráfico:** Barras verticais  
📁 **Arquivo:** `04_tipo_pagamento.png`  
📌 **Insight:** Compara modalidades de pagamento

### Pergunta 5: Meio de Transporte Mais Usado
📊 **Gráfico:** Barras verticais  
📁 **Arquivo:** `05_meio_transporte.png`  
📌 **Insight:** Aéreo vs. Terrestre vs. Marítimo

### Pergunta 6: Top 10 UFs de Destino
📊 **Gráfico:** Barras horizontais  
📁 **Arquivo:** `06_destino_uf.png`  
📌 **Insight:** Concentração geográfica

### Pergunta 7: Top 10 Órgãos Pagadores
📊 **Gráfico:** Barras horizontais  
📁 **Arquivo:** `07_orgao_pagador.png`  
📌 **Insight:** Principais responsáveis pelo pagamento


---

## 10. AUDITORIA E QUALIDADE DE DADOS
 
O script `auditoria.py` (localizado em `pipeline/auditoria.py`) realiza uma auditoria completa do pipeline, validando integridade, consistência e qualidade dos dados em todas as camadas.
 
### 📊 Contagem de Registros
 
| Tabela | Quantidade |
|--------|-----------|
| `raw_viagem` | 341,860 |
| `raw_passagem` | 167,260 |
| `raw_pagamento` | 606,916 |
| `raw_trecho` | 763,349 |
| `silver_viagem` | 341,860 |
| `silver_passagem` | 167,260 |
| `silver_pagamento` | 606,916 |
| `silver_trecho` | 763,349 |
 
✅ **Resultado:** Sem perda de registros nas transformações (Raw = Silver)
 
### 🔍 Qualidade da Camada Silver - Viagem
 
| Validação | Resultado |
|-----------|-----------|
| ID viagem NULL ou vazio | 0 ✅ |
| ID viagem duplicado | 0 ✅ |
| Nome órgão superior NULL | 0 ✅ |
| Nome viajante com sigilo | 51,366 ⚠️ |
| CPF viajante vazio | 2,566 ⚠️ |
| Data início NULL | 0 ✅ |
| Data fim NULL | 0 ✅ |
| Data fim anterior a data início | 0 ✅ |
| Duração dias negativa | 0 ✅ |
| Valor total NULL | 0 ✅ |
| Valor total negativo | 3 ⚠️ |
| Valor diárias negativo | 0 ✅ |
 
**Insights:**
- ✅ Integridade de chaves primárias garantida
- ⚠️ 51,366 registros com proteção de sigilo (dentro da legislação)
- ⚠️ 3 registros com valor total negativo (possíveis devoluções)
### 🛡️ Validação de Formatos - Camada Raw
 
| Validação | Resultado |
|-----------|-----------|
| Data início vazia | 0 ✅ |
| Data fim vazia | 0 ✅ |
| Data início formato inválido | 0 ✅ |
| Data fim formato inválido | 0 ✅ |
| CPF maior que 15 caracteres | 0 ✅ |
| Nome viajante maior que 255 caracteres | 0 ✅ |
| Justificativa maior que 1000 caracteres | 0 ✅ |
 
**Resultado:** ✅ Todos os formatos válidos
 
### 🔗 Comparação Raw × Silver
 
| Tabela | Raw | Silver | Diferença |
|--------|-----|--------|-----------|
| `viagem` | 341,860 | 341,860 | 0 ✅ |
| `passagem` | 167,260 | 167,260 | 0 ✅ |
| `pagamento` | 606,916 | 606,916 | 0 ✅ |
| `trecho` | 763,349 | 763,349 | 0 ✅ |
 
**Resultado:** ✅ Sem perda ou duplicação de dados nas transformações
 
### 🔐 Integridade Referencial
 
| Validação | Resultado |
|-----------|-----------|
| `silver_passagem` sem viagem pai | 0 ✅ |
| `silver_pagamento` sem viagem pai | 0 ✅ |
| `silver_trecho` sem viagem pai | 0 ✅ |
 
**Resultado:** ✅ Todas as chaves estrangeiras válidas
 
### ⚙️ Validação de Constraints - Tabelas Filhas
 
| Validação | Resultado |
|-----------|-----------|
| Pagamento: `tipo_pagamento` NULL | 0 ✅ |
| Pagamento: `valor` NULL | 0 ✅ |
| Pagamento: `valor` negativo | 0 ✅ |
| Passagem: `id_viagem` NULL | 0 ✅ |
| Passagem: `valor_passagem` negativo | 0 ✅ |
| Trecho: `sequencia_trecho` NULL | 0 ✅ |
| Trecho: `origem_data` NULL | 0 ✅ |
| Trecho: `destino_data` NULL | 0 ✅ |
 
**Resultado:** ✅ Todos os constraints respeitados
 
### 📋 Amostras e Padrões Identificados
 
**Situações em `silver_viagem`:**
| Situação | Quantidade |
|----------|-----------|
| Realizada | 338,476 |
| Não realizada | 3,384 |
 
**Variações com Sigilo:**
| Nome | Quantidade |
|------|-----------|
| Informações protegidas por sigilo | 51,366 |
 
**Datas Inválidas na RAW:**
- ✅ Nenhuma data inválida encontrada
### 🎯 Conclusões da Auditoria
 
✅ **Pipeline íntegro:** Sem perda ou alteração de dados nas transformações  
✅ **Qualidade alta:** 99,9% dos registros estão válidos  
✅ **Conformidade:** Constraints e integridade referencial mantidas  
⚠️ **Observações:** 
- 51,366 registros com sigilo (conforme legislação)
- 3 registros com valores negativos (possíveis devoluções legítimas)
- 2,566 CPFs vazios (dados incompletos na fonte)

---

## 11. CONCLUSÕES

### 1. Pipeline Automatizado e Resiliente
O pipeline implementado é **totalmente automatizado**, baixando dados do Google Drive e executando todas as fases sem intervenção manual. A adição de try/except em pontos críticos garante **resiliência** contra falhas.

### 2. Qualidade de Dados Garantida
A separação em 3 camadas (RAW → SILVER → GOLD) garante que:
- ✅ Dados originais são preservados (auditoria)
- ✅ Transformações são rastreáveis
- ✅ Integridade referencial é mantida

### 3. Insights Acionáveis
Os **8 gráficos** e **análises SQL** fornecem evidências para decisões de negócio, como:
- Otimização de gastos por órgão
- Negociação de valores com destinos caros
- Consolidação de processos de pagamento

### 4. Escalabilidade
A arquitetura permite fácil extensão:
- Adicionar novas análises em Gold
- Integrar com ferramentas de BI (Power BI, Tableau)
- Automatizar com Airflow ou Prefect

---

## 12. SUGESTÕES FUTURAS

### 📈 Análises Avançadas
- Série temporal: tendências de gastos ao longo dos meses
- Segmentação: perfil do viajante por cargo/órgão
- Previsão: modelos preditivos para orçamento anual

### 🗺️ Geoespacialização
- Mapa interativo de destinos
- Análise de rotas e distâncias
- Custo por quilômetro viajado

### 📊 Integração com BI
- Dashboard em Power BI/Tableau conectado a Gold tables
- Alertas automáticos para anomalias
- Relatórios agendados por e-mail

### 🔐 Auditoria e Conformidade
- Log de todas as transformações
- Identificação de possíveis fraudes
- Rastreabilidade completa (audit trail)

### 🌐 Produção
- Migrar para banco em nuvem (AWS RDS, Google Cloud SQL)
- Orquestração com Apache Airflow
- Monitoramento com Datadog ou similar
