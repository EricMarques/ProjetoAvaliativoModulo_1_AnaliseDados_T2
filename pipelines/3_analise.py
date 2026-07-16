import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import banco

ROOT_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT_DIR / "reports/figures"
TEXTO_SIGILO = "Informações protegidas por sigilo"


def criar_gold(conexao, cursor, nome_tabela, sql):
    cursor.execute(f"DROP VIEW IF EXISTS vw_gold_{nome_tabela}")
    cursor.execute(f"DROP TABLE IF EXISTS gold_{nome_tabela}")
    cursor.execute(f"CREATE TABLE gold_{nome_tabela} AS {sql}")
    cursor.execute(f"CREATE VIEW vw_gold_{nome_tabela} AS SELECT * FROM gold_{nome_tabela}")
    conexao.commit()


def consultar_gold(conexao, nome_tabela):
    return pd.read_sql(f"SELECT * FROM vw_gold_{nome_tabela}", conexao)


def salvar_imagem(nome_imagem):
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / nome_imagem, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()


def gerar_grafico(
    dataframe,
    eixo_x,
    eixo_y,
    titulo,
    xlabel,
    ylabel,
    nome_imagem,
    horizontal=False,
    tamanho=(12, 6),
    mostrar_valores=True,
):
    plt.figure(figsize=tamanho)

    if horizontal:
        plt.barh(dataframe[eixo_x], dataframe[eixo_y])
        if mostrar_valores:
            for indice, valor in enumerate(dataframe[eixo_y]):
                plt.text(
                    valor,
                    indice,
                    f"{valor:,.2f}" if isinstance(valor, (int, float)) else valor,
                    va="center",
                )
        plt.gca().invert_yaxis()
    else:
        plt.bar(dataframe[eixo_x], dataframe[eixo_y])
        if mostrar_valores:
            for indice, valor in enumerate(dataframe[eixo_y]):
                plt.text(
                    indice,
                    valor,
                    f"{valor:,.2f}" if isinstance(valor, (int, float)) else valor,
                    ha="center",
                )
        plt.xticks(rotation=45, ha="right")

    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(alpha=0.3)
    salvar_imagem(nome_imagem)


def main():
    print("=== FASE 3: ANALISE + CAMADA GOLD ===")

    IMAGES_DIR.mkdir(exist_ok=True)

    conexao = banco.conectar()
    cursor = conexao.cursor()

    try:
        # 1 - Os 5 órgãos com maior custo total
        sql = """
        SELECT
            nome_orgao_superior,
            SUM(valor_total) AS custo_total
        FROM silver_viagem
        GROUP BY nome_orgao_superior
        ORDER BY custo_total DESC
        LIMIT 5
        """
        criar_gold(conexao, cursor, "top5_orgaos", sql)
        df = consultar_gold(conexao, "top5_orgaos")
        print(df)
        gerar_grafico(
            dataframe=df,
            eixo_x="nome_orgao_superior",
            eixo_y="custo_total",
            titulo="Top 5 órgãos com maior custo",
            xlabel="Custo Total (R$)",
            ylabel="Órgão",
            nome_imagem="01_top5_orgaos.png",
            horizontal=True,
        )

        # 2 - Os 3 destinos com maior custo médio por viagem
        sql = """
        SELECT
            CONCAT(t.destino_cidade, '/', t.destino_uf) AS destino,
            AVG(v.valor_total) AS custo_medio
        FROM silver_viagem v
        INNER JOIN silver_trecho t
            ON v.id_viagem = t.id_viagem
        GROUP BY
            t.destino_cidade,
            t.destino_uf
        ORDER BY custo_medio DESC
        LIMIT 3;
        """
        criar_gold(conexao, cursor, "top3_destinos", sql)
        df = consultar_gold(conexao, "top3_destinos")
        print(df)
        
        # Quebrar destinos em múltiplas linhas para melhor legibilidade
        destinos_formatados = []
        for destino in df["destinos"]:
            # Quebra a string a cada 50 caracteres
            destino_quebrado = '\n'.join([destino[i:i+50] for i in range(0, len(destino), 50)])
            destinos_formatados.append(destino_quebrado)
        
        plt.figure(figsize=(14, 8))
        plt.barh(range(len(df)), df["custo_medio"], color='steelblue', height=0.6)
        plt.yticks(range(len(df)), destinos_formatados, fontsize=10)
        plt.xlabel("Custo Médio (R$)", fontsize=12, fontweight='bold')
        plt.ylabel("Destino", fontsize=12, fontweight='bold')
        plt.title("Top 3 Destinos com Maior Custo Médio", fontsize=14, fontweight='bold', pad=20)
        
        # Adicionar valores das barras
        for i, valor in enumerate(df["custo_medio"]):
            plt.text(
                valor,
                i,
                f"  R$ {valor:,.2f}",
                va="center",
                fontsize=10,
                fontweight='bold'
            )
        
        plt.gca().invert_yaxis()
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.savefig(IMAGES_DIR / "02_destinos.png", dpi=300, bbox_inches="tight")
        plt.show()
        plt.close()

        # 3 - Viagem de maior duração e seu custo total
        sql = """
        SELECT
            v.id_viagem,
            v.nome_viajante,
            t.destino_cidade,
            t.destino_uf,
            v.duracao_dias,
            v.valor_total
        FROM silver_viagem v
        INNER JOIN silver_trecho t
            ON v.id_viagem = t.id_viagem
        ORDER BY v.duracao_dias DESC
        LIMIT 1;
        """
        criar_gold(conexao, cursor, "maior_duracao", sql)
        df = consultar_gold(conexao, "maior_duracao")
        print(df)

        plt.figure(figsize=(8, 5))
        plt.bar(["Maior duração"], [df.loc[0, "duracao_dias"]])
        plt.title("Viagem de maior duração")
        plt.ylabel("Dias")
        plt.text(
            0,
            df.loc[0, "duracao_dias"],
            f"{df.loc[0, 'duracao_dias']} dias",
            ha="center",
        )
        salvar_imagem("03_maior_duracao.png")

        # 4 - Tipo de pagamento com maior valor médio
        sql = """
        SELECT
            p.tipo_pagamento,
            v.nome_orgao_superior,
            AVG(p.valor) AS valor_medio
        FROM silver_pagamento p
        INNER JOIN silver_viagem v
            ON p.id_viagem = v.id_viagem
        GROUP BY
            p.tipo_pagamento,
            v.nome_orgao_superior
        ORDER BY valor_medio DESC;
        """
        criar_gold(conexao, cursor, "tipo_pagamento_media", sql)
        df = consultar_gold(conexao, "tipo_pagamento_media")
        print(df)
        gerar_grafico(
            dataframe=df,
            eixo_x="tipo_pagamento",
            eixo_y="valor_medio",
            titulo="Valor médio por tipo de pagamento",
            xlabel="Tipo de pagamento",
            ylabel="Valor médio (R$)",
            nome_imagem="04_tipo_pagamento.png",
        )

        # 5 - Meio de transporte mais usado nos trechos
        sql = """
        SELECT
            t.meio_transporte,
            v.nome_orgao_superior,
            COUNT(*) AS quantidade
        FROM silver_trecho t
        INNER JOIN silver_viagem v
            ON t.id_viagem = v.id_viagem
        GROUP BY
            t.meio_transporte,
            v.nome_orgao_superior
        ORDER BY quantidade DESC;
        """
        criar_gold(conexao, cursor, "meio_transporte", sql)
        df = consultar_gold(conexao, "meio_transporte")
        print(df)
        gerar_grafico(
            dataframe=df,
            eixo_x="meio_transporte",
            eixo_y="quantidade",
            titulo="Meio de transporte mais usado",
            xlabel="Meio de transporte",
            ylabel="Quantidade",
            nome_imagem="05_meio_transporte.png",
        )

        # 6 - UF de destino que aparece em mais trechos
        sql = """
        SELECT
            t.destino_uf,
            v.nome_orgao_superior,
            COUNT(*) AS quantidade
        FROM silver_trecho t
        INNER JOIN silver_viagem v
            ON t.id_viagem = v.id_viagem
        GROUP BY
            t.destino_uf,
            v.nome_orgao_superior
        ORDER BY quantidade DESC;
        """
        criar_gold(conexao, cursor, "destino_uf", sql)
        df = consultar_gold(conexao, "destino_uf")
        print(df)
        gerar_grafico(
            dataframe=df,
            eixo_x="destino_uf",
            eixo_y="quantidade",
            titulo="Top 10 UFs de destino",
            xlabel="Quantidade",
            ylabel="UF",
            nome_imagem="06_destino_uf.png",
            horizontal=True,
        )

        # 7 - Órgão que pagou mais no total
        sql = """
        SELECT
            v.nome_orgao_superior,
            SUM(p.valor) AS valor_total
        FROM silver_pagamento p
        INNER JOIN silver_viagem v
            ON p.id_viagem = v.id_viagem
        GROUP BY
            v.nome_orgao_superior
        ORDER BY valor_total DESC;
        """
        criar_gold(conexao, cursor, "orgao_pagador", sql)
        df = consultar_gold(conexao, "orgao_pagador")
        print(df)
        gerar_grafico(
            dataframe=df,
            eixo_x="nome_orgao_pagador",
            eixo_y="valor_total",
            titulo="Top 10 órgãos pagadores",
            xlabel="Valor total (R$)",
            ylabel="Órgão pagador",
            nome_imagem="07_orgao_pagador.png",
            horizontal=True,
            tamanho=(16, 12),
        )

    #     # 8 - Indicador: viagens com nome_viajante protegido por sigilo
    #     sql = f"""
    #     SELECT
    #         '{TEXTO_SIGILO}' AS indicador,
    #         SUM(CASE WHEN TRIM(nome_viajante) = '{TEXTO_SIGILO}' THEN 1 ELSE 0 END) AS quantidade_sigilo,
    #         COUNT(*) AS total_viagens,
    #         ROUND(
    #             SUM(CASE WHEN TRIM(nome_viajante) = '{TEXTO_SIGILO}' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    #             2
    #         ) AS percentual_sigilo
    #     FROM silver_viagem
    #     """
    #     criar_gold(conexao, cursor, "sigilo_nome_viajante", sql)
    #     df = consultar_gold(conexao, "sigilo_nome_viajante")
    #     print(df)

    #     qtd_sigilo = int(df.loc[0, "quantidade_sigilo"])
    #     total_viagens = int(df.loc[0, "total_viagens"])
    #     percentual = df.loc[0, "percentual_sigilo"]
    #     print("\n--- Indicador: nome_viajante protegido por sigilo ---")
    #     print(f"Registros com sigilo: {qtd_sigilo:,} de {total_viagens:,} ({percentual}%)")

    #     df_grafico = pd.DataFrame(
    #         {
    #             "categoria": ["Com sigilo", "Sem sigilo"],
    #             "quantidade": [qtd_sigilo, total_viagens - qtd_sigilo],
    #         }
    #     )
    #     gerar_grafico(
    #         dataframe=df_grafico,
    #         eixo_x="categoria",
    #         eixo_y="quantidade",
    #         titulo=f"Viagens com '{TEXTO_SIGILO}' em nome_viajante",
    #         xlabel="Categoria",
    #         ylabel="Quantidade de viagens",
    #         nome_imagem="08_sigilo_nome_viajante.png",
    #     )

        print("=== Análise concluída com sucesso! ===")
        print(f"Imagens salvas em: {IMAGES_DIR}")

    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    main()
