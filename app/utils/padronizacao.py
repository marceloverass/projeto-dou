import pandas as pd
import unicodedata
import re
import os

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def limpar_texto(texto):
    texto = str(texto).strip().lower()
    texto = remover_acentos(texto)
    texto = re.sub(r"\[.*?\]|\(.*?\)", "", texto)  
    texto = re.sub(r"[^a-zA-Z0-9\s]", "", texto)  
    texto = texto.replace("'", "").replace('"', "")  
    texto = texto.strip()
    return texto

# Função para padronizar os valores
def padronizar_tipo(texto):
    texto = limpar_texto(texto)
    if texto == "acao realizada" or texto == "acao decorrente da promocao" or texto == "acao apostilar" or texto == "acao penal":
        return "Movimentacao nao identificada"
    
    if texto == "tornar sem efeito a apoentadoria" or texto == "tornar sem efeito aposentadoria":
        return "tornar sem efeito aposentadoria"
    elif "aposentadoria" in texto:
        return "aposentadoria"
    
    if "apostilar" in texto:
        return "apostilar"
    
    if texto == "tornar sem efeito nomeacao" or texto =="tornar sem efeito a nomeacao" or texto == "Tornar sem efeito Nomeacao" or texto == "Tornar sem efeito Nomeação":
        return "tornar sem efeito a nomeacao"
    elif "nomeacao" in texto:
        return "nomeacao"
    
    if texto == "tornar sem efeito a designacao" or texto == "tornar sem efeito designacao" or texto == "tornar sem efeito designar":
        return "tornar sem efeito a designacao"
    elif texto == "revogar designacao" or texto == "revogar a designacao":
        return "revogar designacao"
    elif texto == "designacao suspensa" or texto == "suspender designacao" or texto == "suspensao de designacao":
        return "designacao suspensa"
    elif texto == "prorrogar designacao" or texto == "prorrogar a designacao" or texto =="prorrogar designar":
        return "designacao prorrogada"
    elif "designacao" in texto or "designar" in texto:
        return "designacao"

    if texto == "tornar sem efeito exoneracao" or texto == "tornar sem efeto exonerar":
        return "tornar sem efeito a exoneracao"
    elif "exoneracao" in texto or "exoneracao" in texto:
        return "exoneracao"

    if texto == "tornar sem efeito vacancia" or texto == "tornar sem efeito a vacancia":
        return "tornar sem efeito a vacancia"
    elif "vacancia" in texto or "vagancia" in texto:
        return "vacancia"
    
    if texto == "tornar sem efeito remocao" or texto == "tornar sem efeito a remocao" or texto == "tornar em efeito remover":
        return "tornar sem efeito a remocao"
    elif "remocao" in texto or "remover" in texto:
        return "remocao"

    if texto == "tornar sem efeito afastamento" or texto == "tornar sem efeito a afastamento":
        return "tornar sem efeito a afastamento"
    elif texto == "revogar afastamento":
        return "afastamento revogado"
    elif "afastamento" in texto:
        return "afastamento"

    if texto == "tornar sem efeito redisstribuicao":
        return "tornar sem efeito a redistribuicao"
    elif "redistribuicao" in texto:
        return "redistribuicao"

    if texto == "tornar sem efeito cessao":
        return "tornar sem efeito a cessao"
    if texto == "tornar sem efeito dispensa":
        return "tornar sem efeito a dispensa"
    elif "dispensa" in texto:
        return "dispensa"

    mapeamento = {
        "nomeacao": "nomear",
        "nomeacao realizada": "nomear",
        "nomeada": "nomear",
        "nomeado": "nomear",
        "nomea-la": "nomear",
        "nomea-lo": "nomear",
        "nomear": "nomear",
        "aposentar": "aposentadoria",
        "aposentou": "aposentadoria",
        "aposentado": "aposentadoria",
        "exonerar": "exoneracao",
        "exoneracao": "exoneracao",
        "exonera": "exoneracao",
        "Dispensalo": "Dispensa",
        "designar": "designacao",
        "designado":"designacao",
        "designacao":"designacao",
        "exonerado":"exoneracao",
        "exoneracao realizada":"exoneracao",
        "remover":"remocao",
        "removida":"remocao",
        "removido":"remocao",
        "afastar": "afastamento",
        "declarar vagos": "vacancia",
        "deixar vago": "vacancia",
        "tornar vago": "vacancia",
        "vago": "vacancia",
        "declarar vaga": "vacancia",
        "declara vaga": "vacancia",
        "posse/ingresso": "posse",
        "redistribuido": "redistribuicao",
        "reditribuiu": "redistribuicao",
        "redistribuir": "redistribuicao",
        "demissao": "demissao",
        'demitido': "demissao",
        "demitir": "demissao",
        "cessao": "cessao",
        "cessada": "cessao cessada",
        "cessao autorizada": "cessao autorizada",
        "cessao prorrogada": "cessao prorrogada",
        "prorrogar cessao": "cessao prorrogada",
        "prorrogar a cessao": "cessao prorrogada",
        "revogar cessao": "revogar cessao",
        "revogar a cessao": "revogar cessao",
        "tornar sem efeito cessao": "tornar sem efeito a cessao",
        "fazer cessar os efeitos da cessao": "fazer cessar os efeitos da cessao",
        "fazer cessar, os efeitos": "fazer cessar os efeitos da cessao",
        "cessar os efeitos": "cessar os efeitos",
        "cessar os efeitos da portaria": "cessar os efeitos",
        "cessar os efeitos do ato": "cessar os efeitos",
        "dispensada": "dispensa",
        "dispensado": "dispensa",
        "dispensa-lo": "dispensa",
        "dispensa-o": "dispensa",
        "dispensar": "dispensa",
        "dispensou": "dispensa",
        "dispensando": "dispensa",
        "beneficio especial": "aposentadoria",
        "apostilada": "apostilar",
        "aposentadoria concedida": "aposentadoria",
        "apostilado": "apostilar",
        "apostilamento": "apostilar",
        "conceder":"concessao",
        "concedeu":"concessao",
        "concedido":"concessao",
        "concedida":"concessao",
        "concessao":"concessao",
        "concedidos":"concessao",
        "cessa":"cessao",
        "conceder pensao post mortem":"conceder pensao por morte",
        "conceder pensao civil por morte":"conceder pensao por morte",
        "conceder pensao vitalicia por morte":"conceder pensao por morte",
        "convalidado":"convalidar",
        "substituicao":"substituir",
        "lotado":"lotar",
        "pensao estatutaria vitalicia concedida": "pensao estatutaria vitalicia",
        "exaurir os efeitos da portaria": "exaurir",
        "exaurir os efeitos":"exaurir",
        "deferir pensao civil por morte": "deferir pensao por morte",

    }
    
    if any(word in texto for word in ["acrescer", "apostadoria", "ajuizar","acolher","acrescentar","acompanhamento","antecipar","aplicar","anular","anular o ato de","provimento","apresentadoria","aprovar possiveis pratica de infracoes disciplinares","aprovar","apresentar","apresentacao","autorizar","auxiliar","cancelar","cancelamento","nan","exaurir os efeitos da portaria nº 116, de 12 de marco de 2018, que removeu a servidora",]):
        return None  # Exclui linhas contendo essas palavras
    return mapeamento.get(texto, texto)
def categorizar_tipo(tipo):
    if not isinstance(tipo, str):
        return 18  # valor padrão para casos não tratados
    tipo = tipo.strip().upper()  # padroniza o texto
    categorias = {
        # Categoria 1 - ENTRADA
        'DESIGNACAO': 1, 'NOMEAR': 1, 'NOMEACAO': 1, 'POSSE': 1, 'CONVOCAR': 1, 'CONVOCACAO': 1,
        # Categoria 2 - SAIDA
        'VACANCIA': 2, 'DISPENSA': 2, 'DEMISSAO': 2, 'DESISTENCIA': 2, 'AFASTAMENTO': 2, 'EXONERACAO': 2,
        'DECLARACAO DE VAGA': 2, 'DESOCUPAR': 2, 'DESONERACAO': 2, 'DESONERAR': 2, 'PERDA DE CARGO': 2,
        'OBITO': 2, 'FALECIMENTO': 2, 'REDISTRIBUICAO': 2, 'REDISTRIBUIU': 2, 'REMOCAO': 2,
        # Categoria 3 - PENSÃO
        'PENSAO': 3, 'PENSAO CIVIL': 3, 'PENSAO CIVIL VITALICIA': 3, 'PENSAO CONCEDIDA': 3,
        'PENSAO ESTATUTARIA': 3, 'PENSAO ESTATUTARIA TEMPORARIA': 3, 'PENSAO ESTATUTARIA VITALICIA': 3,
        'PENSAO POR MORTE': 3, 'DEFERIR PENSAO POR MORTE': 3, 'DEFERIR PENSAO VITALICIA': 3,
        'DECLARAR A PERDA DA QUALIDADE DE BENEFICIARIO DE PENSAO TEMPORARIA': 3,
        'REDUCAO DE COTA DE PENSAO': 3, 'CONCEDER LICENCA': 3, 'CONCEDER PENSAO': 3,
        'CONCEDER PENSAO CIVIL': 3, 'CONCEDER PENSAO CIVIL TEMPORARIA': 3, 'CONCEDER PENSAO CIVIL VITALICIA': 3,
        'CONCEDER PENSAO ESTATUTARIA': 3, 'CONCEDER PENSAO ESTATUTARIA VITALICIA': 3,
        'CONCEDER PENSAO MILITAR': 3, 'CONCEDER PENSAO POR MORTE': 3, 'CONCEDER PENSAO PROVISORIA': 3,
        'CONCEDER PENSAO TEMPORARIA': 3, 'CONCEDER PENSAO VITALICIA': 3, 'CONCEDIDA PENSAO CIVIL': 3,
        'CONCESSAO DE PENSAO': 3, 'CONCESSAO DE PENSAO ESTATUTARIA': 3, 'CONCESSAO DE PENSAO VITALICIA': 3,
        'CONCEDENDO PENSAO CIVIL': 3,
        # Categoria 4 - APOSENTADORIA
        'APOSENTADORIA': 4,
        # Categoria 5 - Administrativos
        'APOSTILAR': 5, 'CONSOLIDAR': 5, 'CONSOLIDAR A INDICACAO': 5, 'CONSTITUIR': 5, 'CONVALIDAR': 5,
        'CONVERTER': 5, 'DEFERIR': 5, 'DEFERIMENTO DE MIGRACAO DE REGIME PREVIDENCIARIO': 5,
        'DELEGAR': 5, 'DELEGAR COMPETENCIA': 5, 'DESCONSIDERAR': 5, 'DETERMINAR PAGAMENTO': 5,
        'ESTABELECER': 5, 'FAZER CESSAR': 5, 'FAZER CESSAR OS EFEITOS': 5, 'HOMOLOGAR': 5,
        'IMPLEMENTAR': 5, 'INSTITUIR': 5, 'MANIFESTACAO DE DESISTENCIA': 5, 'OFICIAR': 5, 'RATIFICAR': 5,
        'REGISTRAR': 5, 'REPRISTINAR': 5, 'RESTABELECER': 5, 'RESTABELECER OS EFEITOS': 5,
        'RESTABELECIMENTO': 5, 'RESTAURAR': 5, 'RETIFICAR': 5, 'RETIFICACAO': 5, 'REVERTER': 5,
        'REVISAR': 5, 'REVOGAR': 5, 'SOBRESTAR': 5, 'TORNAR INSUBSISTENTE': 5, 'TORNAR NULO': 5,
        'TORNAR PUBLICA': 5, 'TORNAR SEM EFEITO': 5, 'TORNAR SEM FEITO': 5, 'APROVEITAR': 5,
        'CONCESSAO': 5, 'DISPONIBILIZAR': 5, 'ENCERRAR': 5, 'EXCLUIR': 5, 'INDICAR': 5, 'LEIASE': 5,
        'LIMITAR': 5, 'MANTER': 5, 'RENOVA': 5, 'RESERVAR': 5, 'RECONHECER': 5, 'REVOCAR': 5,
        'VINCULAR': 5, 'DECLARAR': 5, 'DECLARAR EXTINTA': 5, 'DECLARAR VITALICIOS': 5,
        'OFERECER DENUNCIA': 5, 'RECONVOCAR': 5, 'REDUZIR': 5,
        # Categoria 6 - PROMOCAO
        'PROMOCAO': 6, 'PROMOCAO FUNCIONAL': 6, 'PROMOVER': 6, 'CONCEDER BENEFICIO ESPECIAL': 6,
        'INCLUIR VANTAGEM': 6, 'DETERMINAR A CONVERSAO EM PECUNIA': 6, 'INCLUIDO': 6, 'INCLUIR': 6,
        'ISENCAO': 6, 'ELOGIAR': 6,
        # Categoria 7 - LICENCAS
        'LICENCA': 7, 'LICENCATRANSITO': 7, 'CONCEDER 30 DIAS DE TRANSITO': 7,
        'CONCEDER PERIODO DE TRANSITO': 7, 'CONCEDER PRAZO DE TRANSITO': 7, 'CONCEDER TRANSITO': 7,
        'SUSPENDER': 7, 'SUSPENSA': 7, 'SUSPENSAO': 7, 'SUSPENSAO DE TRANSITO': 7,
        'INTERRUPCAO': 7, 'INTERROMPER': 7, 'CONCEDER 30  DIAS DE TRANSITO': 7,
        # Categoria 8 - CESSAO
        'CEDER': 8, 'CESSAO': 8, 'CESSAO AUTORIZADA': 8, 'CESSAO CESSADA': 8,
        'CESSAO PRORROGADA': 8, 'AUTORIZACAO DE PRORROGACAO DA CESSAO': 8,
        'REQUISITAR': 8, 'REVOGAR CESSAO': 8, 'TORNA SEM EFEITO A CESSAO': 8,
        'TORNA SEM EFEITO CEDER': 8,
        # Categoria 12 - ENCARGOS
        'ASSUMIR': 12, 'DESIGNACAO SUSPENSA': 12, 'PRESIDIR': 12, 'COORDENAR': 12,
        'RESPONDER': 12, 'SUBDELEGAR': 12, 'SUBSTITUIR': 12, 'SUBSTITUTA EVENTUAL': 12,
        'REVOGAR DESIGNACAO': 12, 'REVOGAR SUBSTITUICAO': 12,
        'TORNA SEM EFEITO A DESIGNACAO': 12, 'TORNA SEM EFEITO SUBSTITUICAO': 12,
        # Categoria 13 - MOVIMENTACAO
        'MOVIMENTACAO': 13, 'MOVIMENTACAO NAO IDENTIFICADA': 13, 'POSICIONADO': 13, 'POSICIONAR': 13,
        'POSSEINGRESSO': 13, 'PRORROGAR': 13, 'PROVER': 13, 'READAPTAR': 13, 'RECONDUZIR': 13,
        'REINCLUIR': 13, 'REINTEGRAR': 13, 'TRANSPOR': 13, 'TRANSPOSICAO': 13,
        'RETORNAR': 13, 'RETORNO': 13, 'REESTABELECER': 13, 'RESTITUICAO': 13,
        # Categoria 14 - LOTACAO
        'ALTERAR': 14, 'ALTERAR LOTACAO': 14, 'ATRIBUIR': 14, 'COLOCAR': 14,
        'COLOCAR A DISPOSICAO': 14, 'COLOCAR EM EXERCICIO PROVISORIO': 14, 'DESLOCAR': 14,
        'LOTAR': 14, 'RELOTAR': 14, 'REMANEJAR': 14, 'TRANSFERIR': 14,
        'TRANSFORMAR': 14, 'TRANSFORMAR E ALTERAR A LOTACAO': 14,
        # Categoria 15 - TORNAR SEM EFEITO
        'TORNAR SEM EFEITO A NOMEACAO': 15, 'TORNAR SEM EFEITO A VACANCIA': 15,
        'TORNAR SEM EFEITO APOSENTADORIA': 15, 'TORNAR SEM EFEITO A AFASTAMENTO': 15,
        'TORNAR SEM EFEITO A REMOCAO': 15, 'TORNAR SEM EFEITO EXONERAR': 15,
        'TORNAR SEM EFEITO PROVENTOS': 15,
        # Categoria 16 - CESSACAO
        'CESSAR': 16, 'CESSAR OS EFEITOS': 16, 'EXAURIR': 16,
        'EXAURIR OS EFEITOS DA PORTARIA N 116 DE 12 DE MARCO DE 2018 QUE REMOVEU A SERVIDORA': 16,
        'DEVOLVER': 16, 'EXTINCAO': 16, 'EXTINGUIR': 16, 'EXTINTA': 16, 'DESTITUICAO': 16,
        'DESTITUIR': 16, 'PERDA DO CARGO': 16, 'RENUNCIA': 16,
        # Categoria 17 - EXERCICIO
        'DESEMPENHAR SUAS ATRIBUICOES': 17, 'EXERCER': 17, 'EXERCER INTERINAMENTE': 17,
        'PERMANECER': 17, 'PERMANENCIA': 17, 'RECEBENDO': 17, 'RECEBER': 17,
        'RECEBER POR RECIPROCIDADE': 17, 'RECEPCIONADO': 17,
        'INCLUSAO NO QUADRO PERMANENTE DE PESSOAL': 17,
    }
    return categorias.get(tipo, 18)
    
def padronizar_dataframe(df):
    if 'Resposta_Gerada' in df.columns:
        df = df.drop(columns=['Resposta_Gerada'])
    if 'TEXTO' in df.columns:
        df = df.drop(columns=['TEXTO'])
    columns_order = ['DATA_PUB', 'IDENTIFICACAO', 'LINK', 'ORGAO', 'CODIGO', 'SIGLA', 'TIPO', 'NOME', 'CARGO']
    existing_columns = [col for col in columns_order if col in df.columns]
    df = df[existing_columns]
    if 'TIPO' in df.columns:
        df["TIPO"] = df["TIPO"].apply(padronizar_tipo)
    if 'TIPO' in df.columns and 'NOME' in df.columns:
        df = df.dropna(subset=["TIPO", "NOME"])
        df = df[(df["TIPO"].str.strip() != "") & (df["NOME"].str.strip() != "")]
    if 'CODIGO' in df.columns:
        df["CODIGO"] = df["CODIGO"].replace("Código Desconhecido", None)
        df["CODIGO"] = pd.to_numeric(df["CODIGO"], errors='coerce')
    for col in ['NOME', 'IDENTIFICACAO', 'CARGO']:
        if col in df.columns:
            df[col] = df[col].str.replace(r"[\n\r]", " ", regex=True)
            df[col] = df[col].apply(limpar_texto)
    for col in ['NOME', 'TIPO', 'CARGO', 'ORGAO']:
        if col in df.columns:
            df[col] = df[col].str.upper()

    if 'TIPO' in df.columns:
        df["TIPO_CATEGORIA"] = df["TIPO"].apply(categorizar_tipo)

    return df
