import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import banco
from mysql.connector import Error

# TABELAS RAW

raw_viagem = """
    (
        id_viagem              VARCHAR(20),
        num_proposta           VARCHAR(20),
        situacao               VARCHAR(50),
        viagem_urgente         VARCHAR(5),
        justificativa_viagem   VARCHAR(1000),
        cod_orgao_superior     VARCHAR(20),
        nome_orgao_superior    VARCHAR(255),
        cod_orgao_solicitante  VARCHAR(20),
        nome_orgao_solicitante VARCHAR(255),
        cpf_viajante           VARCHAR(15),
        nome_viajante          VARCHAR(255),
        cargo                  VARCHAR(255),
        funcao                 VARCHAR(255),
        descricao_funcao       VARCHAR(255),
        data_inicio            VARCHAR(10),
        data_fim               VARCHAR(10),
        destinos               VARCHAR(4000),
        motivo                 VARCHAR(4000),
        valor_diarias          VARCHAR(15),
        valor_passagens        VARCHAR(15),
        valor_devolucao        VARCHAR(15),
        valor_outros_gastos    VARCHAR(15)
    ) ENGINE=InnoDB;
"""

raw_passagem = """
    (
        id_viagem            VARCHAR(20),
        num_proposta         VARCHAR(20),
        meio_transporte      VARCHAR(50),
        pais_origem_ida      VARCHAR(60),
        uf_origem_ida        VARCHAR(40),
        cidade_origem_ida    VARCHAR(80),
        pais_destino_ida     VARCHAR(60),
        uf_destino_ida       VARCHAR(40),
        cidade_destino_ida   VARCHAR(80),
        pais_origem_volta    VARCHAR(60),
        uf_origem_volta      VARCHAR(40),
        cidade_origem_volta  VARCHAR(80),
        pais_destino_volta   VARCHAR(60),
        uf_destino_volta     VARCHAR(40),
        cidade_destino_volta VARCHAR(80),
        valor_passagem       VARCHAR(15),
        taxa_servico         VARCHAR(15),
        data_emissao         VARCHAR(10),
        hora_emissao         VARCHAR(10)
    ) ENGINE=InnoDB;
"""

raw_pagamento = """
    (
        id_viagem           VARCHAR(20),
        num_proposta        VARCHAR(20),
        cod_orgao_superior  VARCHAR(20),
        nome_orgao_superior VARCHAR(255),
        cod_orgao_pagador   VARCHAR(20),
        nome_orgao_pagador  VARCHAR(255),
        cod_un_pagadora     VARCHAR(20),
        nome_un_pagadora    VARCHAR(255),
        tipo_pagamento      VARCHAR(50),
        valor               VARCHAR(15)
    ) ENGINE=InnoDB;
"""

raw_trecho = """
    (
        id_viagem        VARCHAR(20),
        num_proposta     VARCHAR(20),
        sequencia_trecho VARCHAR(2),
        origem_data      VARCHAR(10),
        origem_pais      VARCHAR(60),
        origem_uf        VARCHAR(40),
        origem_cidade    VARCHAR(80),
        destino_data     VARCHAR(10),
        destino_pais     VARCHAR(60),
        destino_uf       VARCHAR(40),
        destino_cidade   VARCHAR(80),
        meio_transporte  VARCHAR(50),
        numero_diarias   VARCHAR(15),
        missao           VARCHAR(3)
    ) ENGINE=InnoDB;
"""

# TABELAS SILVER
silver_viagem = """
    (
        id_viagem              VARCHAR(20) PRIMARY KEY NOT NULL,
        num_proposta           VARCHAR(20),
        situacao               VARCHAR(50),
        viagem_urgente         VARCHAR(5),
        justificativa_viagem   VARCHAR(1000),
        cod_orgao_superior     VARCHAR(20),
        nome_orgao_superior    VARCHAR(255) NOT NULL,
        cod_orgao_solicitante  VARCHAR(20),
        nome_orgao_solicitante VARCHAR(255),
        cpf_viajante           VARCHAR(15),
        nome_viajante          VARCHAR(255),
        cargo                  VARCHAR(255),
        funcao                 VARCHAR(255),
        descricao_funcao       VARCHAR(255),
        data_inicio            DATE,
        data_fim               DATE,
        destinos               VARCHAR(4000),
        motivo                 VARCHAR(4000),
        valor_diarias          DECIMAL(10,2) CHECK(valor_diarias >= 0),
        valor_passagens        DECIMAL(10,2),
        valor_devolucao        DECIMAL(10,2),
        valor_outros_gastos    DECIMAL(10,2),
        valor_total            DECIMAL(10,2),
        duracao_dias           INT
    ) ENGINE=InnoDB;
"""

silver_passagem = """
    (
        id_passagem        INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
        id_viagem          VARCHAR(20) NOT NULL,
        meio_transporte    VARCHAR(50),
        pais_origem_ida    VARCHAR(60),
        uf_origem_ida      VARCHAR(40),
        cidade_origem_ida  VARCHAR(80),
        pais_destino_ida   VARCHAR(60),
        uf_destino_ida     VARCHAR(40),
        cidade_destino_ida VARCHAR(80),
        valor_passagem     DECIMAL(10,2) CHECK(valor_passagem >= 0),
        taxa_servico       DECIMAL(10,2) CHECK(taxa_servico >= 0),
        data_emissao       DATE,
        FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem)
    ) ENGINE=InnoDB;
"""

silver_pagamento = """
    (
        id_pagamento       INT,
        id_viagem          VARCHAR(20),
        num_proposta       VARCHAR(20),
        nome_orgao_pagador VARCHAR(255),
        nome_ug_pagadora   VARCHAR(255),
        tipo_pagamento     VARCHAR(50) NOT NULL,
        valor              DECIMAL(10,2) CHECK(valor >= 0),
        FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem)
    ) ENGINE=InnoDB;
"""

silver_trecho = """
    (
        id_trecho        INT,
        id_viagem        VARCHAR(20),
        sequencia_trecho INT,
        origem_data      DATE,
        origem_uf        VARCHAR(40),
        origem_cidade    VARCHAR(80),
        destino_data     DATE,
        destino_uf       VARCHAR(40),
        destino_cidade   VARCHAR(80),
        meio_transporte  VARCHAR(50),
        numero_diarias   DECIMAL(10,2),
        FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem)
    ) ENGINE=InnoDB;
"""

table_definitions = {
    'raw_viagem': raw_viagem,
    'raw_passagem': raw_passagem,
    'raw_pagamento': raw_pagamento,
    'raw_trecho': raw_trecho,
    'silver_viagem': silver_viagem,
    'silver_passagem': silver_passagem,
    'silver_pagamento': silver_pagamento,
    'silver_trecho': silver_trecho
}

def drop_table(table_name):
    conn = None
    try:
        conn = banco.conectar()
        cursor = conn.cursor()
        query = f'DROP TABLE IF EXISTS {table_name}'
        cursor.execute(query)
        print(f'Tabela \'{table_name}\' removida com sucesso!')
    except Error as e:
        print(f'Erro ao remover tabela: {e}')
    finally:
        if conn is not None and conn.is_connected():
            conn.close()

def create_table(table_name, fields):
    conn = None
    create_table = f'CREATE TABLE {table_name} {fields}'
    try:
        drop_table(table_name)
        conn = banco.conectar()
        cursor = conn.cursor()
        cursor.execute(create_table)
        print(f'Tabela \'{table_name}\' criada com sucesso!')
    except Error as e:
        print(f'Erro ao criar tabela: {e}')
    finally:
        if conn is not None and conn.is_connected():
            conn.close()

def main():
    for table_name, fields in table_definitions.items():
        create_table(table_name, fields)
        print(str.center(f'========== CRIAÇÃO DA TABELA {table_name.upper()} ==========', 80, '='))

if __name__ == '__main__':
    main()
