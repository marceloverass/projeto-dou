import xml.etree.ElementTree as ET
import os
import pandas as pd
from salva_links import scrape_in_links
from processo_api_IA import ler_dataframe_diario
from raspagem import raspagem_dataframe
import threading
import calendar

def limpeza_diaria(dia, mes, ano, diretorio_saida, evento):
    nome = f'{dia:02d}-{mes:02d}-{ano} Meu Querido Diário.xlsx'
    arquivo_saida = os.path.join(diretorio_saida, f'{mes:02d}-{ano}', nome)
    
    if os.path.exists(arquivo_saida):
        print(f"Arquivo {arquivo_saida} já existe. Pulando...")
        return
    df = scrape_in_links(dia, mes, ano)
    df_api_diario = ler_dataframe_diario(df)
    df_raspagem = raspagem_dataframe(df_api_diario, print)
    
    # Criar o diretório de saída no formato mes/ano
    diretorio_mes_ano = os.path.join(diretorio_saida, f'{mes:02d}-{ano}')
    os.makedirs(diretorio_mes_ano, exist_ok=True)
    
    
    arquivo_saida = os.path.join(diretorio_mes_ano, nome)
    try:
        df_raspagem.to_excel(arquivo_saida, index=False)
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
    
    return df_raspagem 


# Solicitar o mês e o ano do usuário
#mes = int(input("Digite o mês (1-12): "))
#ano = int(input("Digite o ano: "))

# Obter o número de dias no mês
#dias_no_mes = calendar.monthrange(ano, mes)[1]
ano =2025
output_excel = r'W:\DISEG\GEARC\_RESTRITO\Projeto DOU\resources\Extracao_Final\GERAL\{ano}'.format(ano=ano)

limpeza_diaria(17,4,2025, output_excel, None)
# Processar todos os dias do mês sequencialmente
#for dia in range(1, dias_no_mes + 1):
 #   print(f"Processando dia {dia:02d}/{mes:02d}/{ano}...")
  #  evento = threading.Event()
   # processar_arquivo = threading.Thread(target=limpeza_diaria, args=(dia, mes, ano, output_excel, evento))
    #processar_arquivo.start()
    #processar_arquivo.join()
    #print(f"Dia {dia:02d}/{mes:02d}/{ano} concluído.\n")
