import pyodbc
import pandas as pd
import logging
from typing import Union
import os
import dotenv
# Carregar variáveis de ambiente do arquivo .env
dotenv.load_dotenv()
# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("PASSWORD")
DRIVER = "SQL Server"
DB_CONNECTION_STRING = f"DRIVER={DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={PASSWORD}"

def enviar_email_erro(mensagem: str):
    # Função fictícia — substitua pelo seu sistema real de notificação
    logging.error(f"Enviando e-mail de erro: {mensagem}")

def inserir_dados(df: pd.DataFrame, tabela_destino: str):
    """
    Insere os dados do DataFrame na tabela especificada de um banco SQL Server.
    
    Parâmetros:
    - df: DataFrame contendo os dados a serem inseridos.
    - tabela_destino: Nome da tabela no banco de dados onde os dados serão inseridos.

    Requisitos:
    - O DataFrame deve conter as colunas:
      ['DATA_PUB', 'IDENTIFICACAO', 'LINK', 'ORGAO', 'CODIGO', 'SIGLA', 'TIPO', 'NOME', 'CARGO', 'TIPO_CATEGORIA']
    """
    try:
        # Verificar nome da tabela para evitar SQL Injection
        if not tabela_destino.isidentifier():
            raise ValueError(f"Nome de tabela inválido: {tabela_destino}")

        colunas_esperadas = {
            "DATA_PUB", "IDENTIFICACAO", "LINK", "ORGAO", "CODIGO", 
            "SIGLA", "TIPO", "NOME", "CARGO", "TIPO_CATEGORIA"
        }
        colunas_df = set(df.columns)

        # Validar colunas do DataFrame
        if not colunas_esperadas.issubset(colunas_df):
            colunas_faltando = colunas_esperadas - colunas_df
            erro_msg = f"Erro: Colunas ausentes no DataFrame: {colunas_faltando}"
            logging.error(erro_msg)
            raise ValueError(erro_msg)

        # Conversões e limpeza
        df["DATA_PUB"] = pd.to_datetime(df["DATA_PUB"], errors="coerce")
        df["CODIGO"] = pd.to_numeric(df["CODIGO"], errors="coerce")
        df = df.where(pd.notna(df), None)  # Substitui NaNs por None para compatibilidade com o pyodbc

        # Conexão
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        for _, row in df.iterrows():
            try:
                cursor.execute(f"""
                    INSERT INTO {tabela_destino} 
                    (DATA_PUB, IDENTIFICACAO, LINK, ORGAO, CODIGO, SIGLA, TIPO, NOME, CARGO, TIPO_CATEGORIA)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                row['DATA_PUB'], row['IDENTIFICACAO'], row['LINK'], row['ORGAO'],
                row['CODIGO'], row['SIGLA'], row['TIPO'], row['NOME'], row['CARGO'], row['TIPO_CATEGORIA'])

            except Exception as e:
                logging.warning(f"Erro ao inserir linha (NOME: {row.get('NOME', 'Desconhecido')}): {e}")

        conn.commit()
        logging.info(f"✅ Dados inseridos com sucesso na tabela '{tabela_destino}'!")

    except Exception as e:
        logging.exception("❌ Erro ao inserir dados no banco de dados:")
        enviar_email_erro(str(e))
        raise

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
dados_teste = pd.DataFrame([{
    "DATA_PUB": "2024-05-01",
    "IDENTIFICACAO": "123ABC",
    "LINK": "https://exemplo.com",
    "ORGAO": "MINISTÉRIO EXEMPLO",
    "CODIGO": 456,
    "SIGLA": "ME",
    "TIPO": "Nomeação",
    "NOME": "João da Silva",
    "CARGO": "Analista",
    "TIPO_CATEGORIA": "Efetivo"
}])
print(DB_CONNECTION_STRING)
inserir_dados(dados_teste, "MQD")
