"""
2_transformar.py  -  FASE 2: Transformacao e Camada SILVER
----------------------------------------------------------
Pega os dados "sujos" da camada RAW (tudo texto) e preenche as tabelas SILVER
(ja criadas, com PK/FK, pelo 0_criar_banco.txt) com os dados limpos e tipados.

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

import banco


# 1) Esvaziar as tabelas SILVER (idempotencia).
#    A ordem importa por causa da FK: apagamos a filha (itens) antes da principal.
LIMPAR_SILVER = [
    "DELETE FROM silver_itens",
    "DELETE FROM silver_vendas",
]


# 2) Copiar RAW -> SILVER convertendo os tipos.
#    (silver_vendas e a tabela principal; carregamos ela primeiro.)
SQL_VENDAS = """
INSERT INTO silver_vendas (
    id_venda, data_pedido, data_entrega, nome_cliente,
    nome_loja, cidade, forma_pagamento, valor_bruto, valor_desconto
)
SELECT
    id_venda,
    STR_TO_DATE(NULLIF(TRIM(data_pedido),  ''), '%d/%m/%Y'),
    STR_TO_DATE(NULLIF(TRIM(data_entrega), ''), '%d/%m/%Y'),
    NULLIF(TRIM(nome_cliente), ''),
    nome_loja, cidade, forma_pagamento,
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_bruto),    ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_desconto), ''), '.', ''), ',', '.') AS DECIMAL(10,2))
FROM raw_vendas
"""

SQL_ITENS = """
INSERT INTO silver_itens (
    id_venda, sequencia_item, produto, categoria, quantidade, preco_unitario
)
SELECT
    id_venda,
    CAST(NULLIF(TRIM(sequencia_item), '') AS UNSIGNED),
    produto, categoria,
    CAST(NULLIF(TRIM(quantidade), '') AS UNSIGNED),
    CAST(REPLACE(REPLACE(NULLIF(TRIM(preco_unitario), ''), '.', ''), ',', '.') AS DECIMAL(10,2))
FROM raw_itens
WHERE id_venda IN (SELECT id_venda FROM silver_vendas)
"""


# 3) Calcular as colunas derivadas.
#    Agora que os valores ja sao numeros e as datas ja sao DATE, a conta fica facil.
#    COALESCE(coluna, 0) usa 0 quando o valor for NULL (vazio), para nao quebrar a soma.
SQL_CALC_VENDAS = """
UPDATE silver_vendas
SET valor_total = COALESCE(valor_bruto, 0) - COALESCE(valor_desconto, 0),
    prazo_dias  = DATEDIFF(data_entrega, data_pedido)
"""

SQL_CALC_ITENS = """
UPDATE silver_itens
SET subtotal = COALESCE(quantidade, 0) * COALESCE(preco_unitario, 0)
"""


def main():
    print("=== FASE 2: TRANSFORMACAO + CAMADA SILVER ===")
    try:
        conexao = banco.conectar()

        print("[1/3] Esvaziando as tabelas SILVER...")
        for comando in LIMPAR_SILVER:
            banco.executar(conexao, comando)

        print("[2/3] Copiando e convertendo RAW -> SILVER...")
        banco.executar(conexao, SQL_VENDAS)
        print("      silver_vendas OK")
        banco.executar(conexao, SQL_ITENS)
        print("      silver_itens  OK")

        print("[3/3] Calculando valor_total, prazo_dias e subtotal...")
        banco.executar(conexao, SQL_CALC_VENDAS)
        banco.executar(conexao, SQL_CALC_ITENS)

        conexao.close()
        print("=== Camada SILVER concluida com sucesso! ===")
    except Exception as erro:
        print("[ERRO] Algo deu errado:", erro)
        raise


if __name__ == "__main__":
    main()
