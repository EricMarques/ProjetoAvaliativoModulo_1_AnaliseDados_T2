"""
2_transformar.py  -  FASE 2: Transformacao e Camada SILVER
----------------------------------------------------------
Pega os dados "sujos" da camada RAW (tudo texto) e preenche as tabelas SILVER
(ja criadas, com PK/FK, pelo 0_criar_banco.py) com os dados limpos e tipados.

A receita e simples: rodamos alguns comandos SQL, em ordem.
  1. Esvaziamos as tabelas SILVER (para nao duplicar se rodar de novo).
  2. Copiamos da RAW para a SILVER, convertendo os tipos.
  3. Calculamos as colunas derivadas (valor_total, prazo_dias, subtotal).

------------------------------------------------------------------------------
COMO CONVERTEMOS O TEXTO DA CAMADA RAW (esse padrao se repete no SQL abaixo):

  - Dinheiro: "1.234,50" (texto)  ->  1234.50 (numero DECIMAL)
      tira o ponto de milhar, troca a virgula por ponto e faz CAST:
      CAST(REPLACE(REPLACE(NULLIF(TRIM(coluna), ''), '.', ''), ',', '.') AS DECIMAL(10,2))

  - Data: "30/06/2025" (texto)  ->  2025-06-30 (tipo DATE)
      STR_TO_DATE(NULLIF(TRIM(coluna), ''), '%d/%m/%Y')

  Obs.: NULLIF(coluna, '') transforma um campo vazio em NULL (vazio no banco).
------------------------------------------------------------------------------
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config.banco as banco


# 1) Esvaziar as tabelas SILVER (idempotencia).
#    A ordem importa por causa da FK: apagamos as filhas antes da principal.
LIMPAR_SILVER = [
    "DELETE FROM silver_trecho",
    "DELETE FROM silver_pagamento",
    "DELETE FROM silver_passagem",
    "DELETE FROM silver_viagem",
]


# 2) Copiar RAW -> SILVER convertendo os tipos.
#    (silver_viagem é a tabela principaldeve ser carregada primeiro.)
SQL_VIAGEM = '''
    INSERT INTO silver_viagem (
        id_viagem,
        num_proposta,
        situacao,
        viagem_urgente,
        justificativa_viagem,
        cod_orgao_superior,
        nome_orgao_superior,
        cod_orgao_solicitante,
        nome_orgao_solicitante,
        cpf_viajante,
        nome_viajante,
        cargo,
        funcao,
        descricao_funcao,
        data_inicio,
        data_fim,
        destinos,
        motivo,
        valor_diarias,
        valor_passagens, 
        valor_devolucao,
        valor_outros_gastos,
        valor_total,
        duracao_dias
    )
    SELECT
        id_viagem,
        num_proposta,
        situacao,
        viagem_urgente,
        justificativa_viagem,
        cod_orgao_superior,
        nome_orgao_superior,
        cod_orgao_solicitante,
        nome_orgao_solicitante,
        cpf_viajante,
        nome_viajante,
        cargo,
        funcao,
        descricao_funcao,
        STR_TO_DATE(NULLIF(TRIM(data_inicio),  ''), '%d/%m/%Y') as data_inicio,
        STR_TO_DATE(NULLIF(TRIM(data_fim),  ''), '%d/%m/%Y') as data_fim,
        destinos,
        motivo,
        CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_diarias), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
        CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_passagens), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
        CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_devolucao), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
        CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_outros_gastos), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
        (
    		CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_diarias), ''), '.', ''), ',', '.') AS DECIMAL(10,2)) +
    		CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_passagens), ''), '.', ''), ',', '.') AS DECIMAL(10,2)) +
    		CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_outros_gastos), ''), '.', ''), ',', '.') AS DECIMAL(10,2)) -
    		CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_devolucao), ''), '.', ''), ',', '.') AS DECIMAL(10,2))
    	) AS valor_total,
        DATEDIFF(
    		STR_TO_DATE(data_fim, '%d/%m/%Y'),
    		STR_TO_DATE(data_inicio, '%d/%m/%Y')
    	) AS duracao_dias
    FROM raw_viagem;
'''

SQL_PASSAGEM = '''
    INSERT INTO silver_passagem (
        id_viagem,
        meio_transporte,
        pais_origem_ida,
        uf_origem_ida,
        cidade_origem_ida,
        pais_destino_ida,
        uf_destino_ida,
        cidade_destino_ida,
        valor_passagem,
        taxa_servico,
        data_emissao
    )
    SELECT
        id_viagem,
        meio_transporte,
        NULLIF(TRIM(pais_origem_ida), ''),
        NULLIF(TRIM(uf_origem_ida), ''),
        NULLIF(TRIM(cidade_origem_ida), ''),
        NULLIF(TRIM(pais_destino_ida), ''),
        NULLIF(TRIM(uf_destino_ida), ''),
        NULLIF(TRIM(cidade_destino_ida), ''),
        CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_passagem), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
        CAST(REPLACE(REPLACE(NULLIF(TRIM(taxa_servico), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
        STR_TO_DATE(NULLIF(TRIM(data_emissao),  ''), '%d/%m/%Y') as data_emissao
    FROM raw_passagem;
'''
SQL_PAGAMENTO = '''
    INSERT INTO silver_pagamento (
        id_viagem,
        num_proposta,
        nome_orgao_pagador,
        nome_ug_pagadora,
        tipo_pagamento,
        valor
    )
    SELECT
        id_viagem,
        num_proposta,
        NULLIF(TRIM(nome_orgao_pagador), ''),
        NULLIF(TRIM(nome_un_pagadora), ''),
        NULLIF(TRIM(tipo_pagamento), ''),
        CAST(REPLACE(REPLACE(NULLIF(TRIM(valor), ''), '.', ''), ',', '.') AS DECIMAL(10,2))
    FROM raw_pagamento;
'''
SQL_TRECHO = '''
    INSERT INTO silver_trecho (
        id_viagem,
        sequencia_trecho,
        origem_data,
        origem_uf,
        origem_cidade,
        destino_data,
        destino_uf,
        destino_cidade,
        meio_transporte,
        numero_diarias
    )
    SELECT
        id_viagem,
        sequencia_trecho,
        STR_TO_DATE(NULLIF(TRIM(origem_data),  ''), '%d/%m/%Y') as origem_data,
        origem_uf,
        origem_cidade,
        STR_TO_DATE(NULLIF(TRIM(destino_data),  ''), '%d/%m/%Y') as destino_data,
        destino_uf,
        destino_cidade,
        meio_transporte,
        CAST(REPLACE(REPLACE(NULLIF(TRIM(numero_diarias), ''), '.', ''), ',', '.') AS DECIMAL(10,2))    
    FROM raw_trecho;
'''

table_queries = [
    SQL_VIAGEM,
    SQL_PASSAGEM,
    SQL_PAGAMENTO,
    SQL_TRECHO
]

def clean_tables():
    try:
        conexao = banco.conectar()

        print("\t[1/2] Esvaziando as tabelas SILVER...")
        for comando in LIMPAR_SILVER:
            banco.executar(conexao, comando)

        conexao.close()
        print('=== Camada SILVER limpa com sucesso! ===')
    except Exception as erro:
        print("[ERRO] Algo deu errado:", erro)
        raise

def insert_into(table_queries):
    clean_tables()
    print("=== POPULANDO AS TABELAS SILVER ===")
    try:
        conexao = banco.conectar()

        print("\t[2/2] Copiando e convertendo RAW -> SILVER...")
        for query in table_queries:
            banco.executar(conexao, query)
            print(f'\tTabela {query.split()[2]} populada com sucesso!')

        conexao.close()
        print('=== Camada SILVER concluida com sucesso! ===')
    except Exception as erro:
        print("[ERRO] Algo deu errado:", erro)
        raise

def main():
    print('=== FASE 2: TRANSFORMACAO + CAMADA SILVER ===')
    insert_into(table_queries)


if __name__ == "__main__":
    main()
