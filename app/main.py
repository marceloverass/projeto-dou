import os
import pandas as pd
import pyodbc
import logging
import sys
from datetime import datetime, timedelta
from app.processamento.salva_links import scrape_in_links
from app.processamento.processo_api_IA import ler_dataframe_diario
from app.processamento.raspagem import raspagem_dataframe
from app.utils.padronizacao import padronizar_dataframe
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import matplotlib.pyplot as plt
from io import BytesIO
from email.mime.image import MIMEImage
from dotenv import load_dotenv

# Configurações de logging
logging.basicConfig(
    filename='processamento_dou.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()
TESTE = os.getenv("TESTE")


# Configurações do banco de dados
DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("PASSWORD")
DRIVER = "SQL Server"
DB_CONNECTION_STRING = f"DRIVER={DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={PASSWORD}"

# Configurações de e-mail
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL_SENDER = "marcos.marinho@funprespjud.com.br"
EMAIL_DESTINATARIO = "giovani.rocha@funprespjud.com.br"
ASSUNTO = "Relatório de Processamento Diário - DOU"

def get_base_dir():
    """Retorna o diretório base do script ou do executável."""
    if getattr(sys, 'frozen', False):  
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()

def testar_conexao_banco():
    dados_teste = {
        "DATA_PUB": datetime.now(),
        "IDENTIFICACAO": "Teste",
        "LINK": "http://teste.com",
        "ORGAO": "Teste Orgão",
        "CODIGO": 123,
        "SIGLA": "TO",
        "TIPO": "Teste Tipo",
        "NOME": "Teste Nome",
        "CARGO": "Teste Cargo",
        "TIPO_CATEGORIA": 1
    }
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING, timeout=5)
        conn.close()
        logging.info("Conexão com o banco de dados bem-sucedida.")
        
        return True
    except Exception as e:
        logging.error(f"Falha ao conectar com o banco de dados: {e}")
        print("Erro: Não foi possível conectar ao banco de dados. Verifique suas credenciais.")
        return False
    
def carregar_cc_list():
    try:
        path = os.path.join(BASE_DIR, 'cc_list.txt')
        with open(path, 'r', encoding='utf-8') as f:
            return [email.strip() for email in f.readlines() if email.strip()]
    except FileNotFoundError:
        logging.warning("Arquivo cc_list.txt não encontrado. Nenhum e-mail em cópia será usado.")
        return []

def carregar_cc_list_erro():
    try:
        path = os.path.join(BASE_DIR, 'cc_list_erro.txt')
        with open(path, 'r', encoding='utf-8') as f:
            return [email.strip() for email in f.readlines() if email.strip()]
    except FileNotFoundError:
        logging.warning("Arquivo cc_list_erro.txt não encontrado. Nenhum e-mail em cópia será usado.")
        return []

def gerar_grafico_barras(df, coluna, titulo):
    contagem = df[coluna].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    
    bars = contagem.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')

    # Título e labels com fonte maior
    ax.set_title(titulo, fontsize=14, weight='bold')
    ax.set_xlabel(coluna, fontsize=12)
    ax.set_ylabel('Quantidade', fontsize=12)

    # Ajustar o limite superior do eixo Y
    ax.set_ylim(0, contagem.max() + 10)

    # Rótulos acima das barras
    for i, value in enumerate(contagem.values):
        ax.text(i, value + 0.5, str(value), ha='center', va='bottom', fontsize=10)

    # Rotacionar rótulos do eixo X
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=120)
    buffer.seek(0)
    plt.close(fig)
    return buffer


def enviar_email_sucesso(df):
    cc_list = carregar_cc_list()
    hora = datetime.now().strftime("%H:%M")
    data = datetime.now().strftime("%d/%m/%Y")
    dia, mes, ano = calcular_dia_limpeza()
    ontem = datetime(ano, mes, dia).strftime("%d/%m/%Y")
    resumo_tipos = df['TIPO'].value_counts().to_frame().reset_index()
    resumo_orgaos = df['SIGLA'].value_counts().to_frame().reset_index()

    corpo_email = f"""\
    Prezados,<br><br>

    O processo automático de leitura e inserção de dados do Meu Querido Diário foi concluído com sucesso em {data} às {hora}.<br><br>

    <b>Total de registros inseridos de {ontem}:</b> {len(df)}<br><br>

    <b>Resumo por tipo:</b><br>
    <img src="cid:grafico_tipos"><br><br>

    <b>Resumo por órgão:</b><br>
    <img src="cid:grafico_orgaos"><br><br>

    Atenciosamente,<br>
    EQUIPE GEARC
    """

    try:
        msg = MIMEMultipart('related')
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_DESTINATARIO
        msg["Cc"] = ", ".join(cc_list)
        msg["Subject"] = ASSUNTO

        msg_alt = MIMEMultipart('alternative')
        msg.attach(msg_alt)
        msg_alt.attach(MIMEText(corpo_email, "html"))

        # Gráfico 1 - TIPO
        buffer_tipos = gerar_grafico_barras(df, 'TIPO', 'Distribuição por Tipo')
        image_tipos = MIMEImage(buffer_tipos.read(), name="grafico_tipos.png")
        image_tipos.add_header('Content-ID', '<grafico_tipos>')
        msg.attach(image_tipos)

        # Gráfico 2 - SIGLA
        buffer_orgaos = gerar_grafico_barras(df, 'SIGLA', 'Distribuição por Órgão')
        image_orgaos = MIMEImage(buffer_orgaos.read(), name="grafico_orgaos.png")
        image_orgaos.add_header('Content-ID', '<grafico_orgaos>')
        msg.attach(image_orgaos)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.sendmail(EMAIL_SENDER, [EMAIL_DESTINATARIO] + cc_list, msg.as_string())

        logging.info(f"E-mail de sucesso com gráfico enviado para {EMAIL_DESTINATARIO}")
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail com gráficos: {e}")

def enviar_email_erro(mensagem_erro):
    cc_list_erro = carregar_cc_list_erro()
    hora = datetime.now().strftime("%H:%M")
    data = datetime.now().strftime("%d/%m/%Y")

    corpo_email = f"""\
    Prezados,<br><br>

    O processo automático de leitura e inserção de dados do Diário Oficial da União falhou em {data} às {hora}.<br><br>

    <b>Erro:</b><br>
    <pre>{mensagem_erro}</pre><br>

    Por favor, verifique o log da aplicação ou entre em contato com a equipe responsável.<br><br>

    Atenciosamente,<br>
    EQUIPE GEARC
    """

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_DESTINATARIO
        msg["Cc"] = ", ".join(cc_list_erro)
        msg["Subject"] = "🚨 Falha no Processamento Diário - DOU"
        msg.attach(MIMEText(corpo_email, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.sendmail(EMAIL_SENDER, [EMAIL_DESTINATARIO], msg.as_string())

        logging.info(f"E-mail de erro enviado para {EMAIL_DESTINATARIO}")
    except Exception as e:
        logging.error(f"Falha ao enviar e-mail de erro: {e}")

def limpeza_diaria(dia, mes, ano):
    try:
        df = scrape_in_links(dia, mes, ano)
        df_api_diario = ler_dataframe_diario(df)
        df_raspagem = raspagem_dataframe(df_api_diario)
        df_final = padronizar_dataframe(df_raspagem)

        if df_final.empty:
            mensagem = f"Nenhum dado foi processado para o DOU de {dia:02d}/{mes:02d}/{ano}. Nenhuma inserção foi realizada."
            logging.warning(mensagem)
            #enviar_email_erro(mensagem)
            return

        inserir_dados(df_final, 'MQD')
        enviar_email_sucesso(df_final)

    except Exception as e:
        logging.exception("Erro ao processar os dados:")
        #enviar_email_erro(str(e))

def inserir_dados(df, tabela_destino):
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        colunas_esperadas = {"DATA_PUB", "IDENTIFICACAO", "LINK", "ORGAO", "CODIGO", 
                            "SIGLA", "TIPO", "NOME", "CARGO", "TIPO_CATEGORIA"}
        colunas_df = set(df.columns)

        if not colunas_esperadas.issubset(colunas_df):
            erro_msg = f"Erro: Colunas ausentes no DataFrame: {colunas_esperadas - colunas_df}"
            logging.error(erro_msg)
            raise Exception(erro_msg)

        # DATA_PUB: converter para datetime, invalidos viram NaT
        df["DATA_PUB"] = pd.to_datetime(df["DATA_PUB"], errors="coerce")

        # CODIGO: converter para inteiro, invalidos viram None
        df["CODIGO"] = pd.to_numeric(df["CODIGO"], errors="coerce").dropna().astype(int)
        df["CODIGO"] = df["CODIGO"].where(pd.notna(df["CODIGO"]), None)

        # Para as colunas string, garantir que None permaneça None
        cols_str = ['IDENTIFICACAO', 'LINK', 'ORGAO', 'SIGLA', 'TIPO', 'NOME', 'CARGO', 'TIPO_CATEGORIA']

        for col in cols_str:
            if col in df.columns:
                # Substitui NaN por None
                df[col] = df[col].where(pd.notna(df[col]), None)
                # Se não for None, converte para string e aplica strip
                df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Para CODIGO e DATA_PUB, substituir NaN/NaT por None (padrão para banco)
        df["CODIGO"] = df["CODIGO"].where(pd.notna(df["CODIGO"]), None)
        df["DATA_PUB"] = df["DATA_PUB"].where(pd.notna(df["DATA_PUB"]), None)
        # Print da primeira linha e seus tipos para teste
        if not df.empty:
            primeira_linha = df.iloc[0]
            print("Primeira linha:", primeira_linha.to_dict())
            print("Tipos:", {col: type(primeira_linha[col]) for col in df.columns})
        # Inserir linha a linha
        for idx, row in df.iterrows():
            try:
                # Garante que CODIGO seja int ou None
                codigo_val = int(row['CODIGO']) if row['CODIGO'] is not None and not pd.isna(row['CODIGO']) else None
                cursor.execute(f"""
                    INSERT INTO {tabela_destino} 
                    (DATA_PUB, IDENTIFICACAO, LINK, ORGAO, CODIGO, SIGLA, TIPO, NOME, CARGO, TIPO_CATEGORIA)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                row['DATA_PUB'], row['IDENTIFICACAO'], row['LINK'], row['ORGAO'],
                codigo_val, row['SIGLA'], row['TIPO'], row['NOME'], row['CARGO'], row['TIPO_CATEGORIA'])

            except Exception as e:
                logging.warning(f"Erro ao inserir linha índice {idx} nome '{row.get('NOME', '')}': {e}")

        conn.commit()
        logging.info(f"Dados inseridos com sucesso na tabela {tabela_destino}!")

    except Exception as e:
        logging.exception("Erro de conexão com o banco de dados ou processamento:")
        raise

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def calcular_dia_limpeza():
    hoje = datetime.now()
    dia_semana = hoje.weekday()  # segunda = 0 ... domingo = 6

    if dia_semana in (5, 6):
        return None 
    elif dia_semana == 0: 
        data_alvo = hoje - timedelta(days=3)
    else:
        data_alvo = hoje - timedelta(days=1)

    return data_alvo.day, data_alvo.month, data_alvo.year

if __name__ == "__main__":
    data = calcular_dia_limpeza()
    
    if not testar_conexao_banco():
        sys.exit("Encerrando processo por falha na conexão com o banco de dados.")
        logging.error("Encerrando processo por falha na conexão com o banco de dados.")
    if data:
        dia, mes, ano = data
        limpeza_diaria(dia, mes, ano)
    else:
        print("Hoje é sábado ou domingo. Nenhuma limpeza será executada.")