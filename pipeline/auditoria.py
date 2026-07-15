import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import banco

TEXTO_SIGILO = "Informações protegidas por sigilo"


def q(conexao, sql):
    return pd.read_sql(sql, conexao)


def contar(conexao, sql):
    return int(q(conexao, sql).iloc[0, 0])


def main():
    conexao = banco.conectar()

    print("=== CONTAGEM DE REGISTROS ===")
    tabelas = [
        "raw_viagem",
        "raw_passagem",
        "raw_pagamento",
        "raw_trecho",
        "silver_viagem",
        "silver_passagem",
        "silver_pagamento",
        "silver_trecho",
    ]
    for tabela in tabelas:
        try:
            total = contar(conexao, f"SELECT COUNT(*) FROM {tabela}")
            print(f"{tabela}: {total:,}")
        except Exception as erro:
            print(f"{tabela}: ERRO - {erro}")

    print("\n=== SILVER_VIAGEM - QUALIDADE ===")
    checks_viagem = [
        ("id_viagem NULL ou vazio", "SELECT COUNT(*) FROM silver_viagem WHERE id_viagem IS NULL OR TRIM(id_viagem) = ''"),
        ("id_viagem duplicado", "SELECT COUNT(*) - COUNT(DISTINCT id_viagem) FROM silver_viagem"),
        ("nome_orgao_superior NULL", "SELECT COUNT(*) FROM silver_viagem WHERE nome_orgao_superior IS NULL"),
        ("nome_viajante com sigilo", f"SELECT COUNT(*) FROM silver_viagem WHERE TRIM(nome_viajante) = '{TEXTO_SIGILO}'"),
        ("cpf_viajante vazio", "SELECT COUNT(*) FROM silver_viagem WHERE cpf_viajante IS NULL OR TRIM(cpf_viajante) = ''"),
        ("data_inicio NULL", "SELECT COUNT(*) FROM silver_viagem WHERE data_inicio IS NULL"),
        ("data_fim NULL", "SELECT COUNT(*) FROM silver_viagem WHERE data_fim IS NULL"),
        ("data_fim anterior a data_inicio", "SELECT COUNT(*) FROM silver_viagem WHERE data_inicio IS NOT NULL AND data_fim IS NOT NULL AND data_fim < data_inicio"),
        ("duracao_dias negativa", "SELECT COUNT(*) FROM silver_viagem WHERE duracao_dias < 0"),
        ("valor_total NULL", "SELECT COUNT(*) FROM silver_viagem WHERE valor_total IS NULL"),
        ("valor_total negativo", "SELECT COUNT(*) FROM silver_viagem WHERE valor_total < 0"),
        ("valor_diarias negativo", "SELECT COUNT(*) FROM silver_viagem WHERE valor_diarias < 0"),
    ]
    for nome, sql in checks_viagem:
        try:
            total = contar(conexao, sql)
            alerta = " ***" if total > 0 else ""
            print(f"  {nome}: {total:,}{alerta}")
        except Exception as erro:
            print(f"  {nome}: ERRO - {erro}")

    print("\n=== RAW_VIAGEM - DATAS E VALORES SUSPEITOS ===")
    raw_checks = [
        ("data_inicio vazia", "SELECT COUNT(*) FROM raw_viagem WHERE data_inicio IS NULL OR TRIM(data_inicio) = ''"),
        ("data_fim vazia", "SELECT COUNT(*) FROM raw_viagem WHERE data_fim IS NULL OR TRIM(data_fim) = ''"),
        ("data_inicio formato invalido", "SELECT COUNT(*) FROM raw_viagem WHERE TRIM(data_inicio) <> '' AND data_inicio NOT REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'"),
        ("data_fim formato invalido", "SELECT COUNT(*) FROM raw_viagem WHERE TRIM(data_fim) <> '' AND data_fim NOT REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'"),
        ("cpf_viajante maior que 15 chars", "SELECT COUNT(*) FROM raw_viagem WHERE LENGTH(cpf_viajante) > 15"),
        ("nome_viajante maior que 255 chars", "SELECT COUNT(*) FROM raw_viagem WHERE LENGTH(nome_viajante) > 255"),
        ("justificativa maior que 1000 chars", "SELECT COUNT(*) FROM raw_viagem WHERE LENGTH(justificativa_viagem) > 1000"),
    ]
    for nome, sql in raw_checks:
        total = contar(conexao, sql)
        alerta = " ***" if total > 0 else ""
        print(f"  {nome}: {total:,}{alerta}")

    print("\n=== COMPARACAO RAW x SILVER ===")
    pares = [
        ("raw_viagem", "silver_viagem"),
        ("raw_passagem", "silver_passagem"),
        ("raw_pagamento", "silver_pagamento"),
        ("raw_trecho", "silver_trecho"),
    ]
    for raw, silver in pares:
        raw_total = contar(conexao, f"SELECT COUNT(*) FROM {raw}")
        silver_total = contar(conexao, f"SELECT COUNT(*) FROM {silver}")
        diff = raw_total - silver_total
        alerta = " ***" if diff != 0 else ""
        print(f"  {raw} ({raw_total:,}) vs {silver} ({silver_total:,}) | diff={diff:,}{alerta}")

    print("\n=== INTEGRIDADE REFERENCIAL ===")
    for tabela in ["silver_passagem", "silver_pagamento", "silver_trecho"]:
        total = contar(
            conexao,
            f"""
            SELECT COUNT(*) FROM {tabela} f
            LEFT JOIN silver_viagem p ON f.id_viagem = p.id_viagem
            WHERE p.id_viagem IS NULL
            """,
        )
        alerta = " ***" if total > 0 else ""
        print(f"  {tabela} sem viagem pai: {total:,}{alerta}")

    print("\n=== SILVER FILHAS - PROBLEMAS ===")
    filhas = [
        ("pagamento tipo_pagamento NULL", "SELECT COUNT(*) FROM silver_pagamento WHERE tipo_pagamento IS NULL"),
        ("pagamento valor NULL", "SELECT COUNT(*) FROM silver_pagamento WHERE valor IS NULL"),
        ("pagamento valor negativo", "SELECT COUNT(*) FROM silver_pagamento WHERE valor < 0"),
        ("passagem id_viagem NULL", "SELECT COUNT(*) FROM silver_passagem WHERE id_viagem IS NULL"),
        ("passagem valor_passagem negativo", "SELECT COUNT(*) FROM silver_passagem WHERE valor_passagem < 0"),
        ("trecho sequencia_trecho NULL", "SELECT COUNT(*) FROM silver_trecho WHERE sequencia_trecho IS NULL"),
        ("trecho origem_data NULL", "SELECT COUNT(*) FROM silver_trecho WHERE origem_data IS NULL"),
        ("trecho destino_data NULL", "SELECT COUNT(*) FROM silver_trecho WHERE destino_data IS NULL"),
    ]
    for nome, sql in filhas:
        total = contar(conexao, sql)
        alerta = " ***" if total > 0 else ""
        print(f"  {nome}: {total:,}{alerta}")

    print("\n=== AMOSTRAS ===")
    print("Situacoes em silver_viagem:")
    print(q(conexao, "SELECT situacao, COUNT(*) AS qtd FROM silver_viagem GROUP BY situacao ORDER BY qtd DESC LIMIT 5").to_string(index=False))

    print("\nVariacoes de nome com sigilo:")
    print(
        q(
            conexao,
            """
            SELECT nome_viajante, COUNT(*) AS qtd
            FROM silver_viagem
            WHERE nome_viajante LIKE '%sigilo%' OR nome_viajante LIKE '%protegid%'
            GROUP BY nome_viajante
            ORDER BY qtd DESC
            LIMIT 10
            """,
        ).to_string(index=False)
    )

    print("\nExemplos de datas invalidas na RAW:")
    print(
        q(
            conexao,
            """
            SELECT data_inicio, data_fim, COUNT(*) AS qtd
            FROM raw_viagem
            WHERE (TRIM(data_inicio) <> '' AND data_inicio NOT REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$')
               OR (TRIM(data_fim) <> '' AND data_fim NOT REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$')
            GROUP BY data_inicio, data_fim
            ORDER BY qtd DESC
            LIMIT 5
            """,
        ).to_string(index=False)
    )

    conexao.close()


if __name__ == "__main__":
    main()
