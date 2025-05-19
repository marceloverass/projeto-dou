import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app.utils.mapeamento import mapa_orgao_codigos
from app.utils.mapeamento import mapa_orgao_siglas

# Desativa warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_in_links(dia, mes, ano):
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Configuração de retentativas para o WebDriver
    max_attempts = 20
    attempt = 0
    driver = None
    
    while attempt < max_attempts:
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            
            lista_orgao = []
            url_base = f'https://www.in.gov.br/leiturajornal?data={dia}-{mes}-{ano}&secao=do2'

            driver.get(url_base)
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script('return document.readyState') == 'complete')
            
            # Espera adicional para elementos dinâmicos
            time.sleep(2)
            
            orgao_select = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, 'slcOrgs')))
            orgaos_options = orgao_select.find_elements(By.TAG_NAME, 'option')
            
            for orgao_option in orgaos_options:
                if orgao_option.text in ['Poder Judiciário', 'Ministério Público da União', 'Conselho Nacional do Ministério Público']:
                    lista_orgao.append(orgao_option.text)
                    print(f"Órgão adicionado: {orgao_option.text}")
            print(f"Órgãos selecionados: {lista_orgao}")
            filtered_links = []
            for orgao in lista_orgao:
                url = f'https://www.in.gov.br/leiturajornal?data={dia}-{mes}-{ano}&secao=do2&org={orgao}'
                print(f"Acessando a URL: {url}")
                
                while True:  # Reinicia o loop para o órgão em caso de erro ou demora
                    try:
                        driver.get(url)
                        WebDriverWait(driver, 30).until(
                            lambda d: d.execute_script('return document.readyState') == 'complete')
                        time.sleep(3)  # Espera para carregamento
                        
                        def extract_links():
                            try:
                                WebDriverWait(driver, 30).until(
                                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="web/dou"]')))
                                links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="web/dou"]')
                                for link in links:
                                    href = link.get_attribute('href')
                                    if href and 'in.gov.br' in href:
                                        filtered_links.append(href)
                            except Exception as e:
                                print(f"Erro ao extrair links: {e}")

                        def go_to_next_page():
                            try:
                                next_button = WebDriverWait(driver, 20).until(
                                    EC.element_to_be_clickable((By.XPATH, '//span[text()="Próximo »"]')))
                                driver.execute_script("arguments[0].click();", next_button)
                                time.sleep(2)  # Espera após clique
                                return True
                            except:
                                return False

                        while True:
                            extract_links()
                            if not go_to_next_page():
                                break
                        
                        # Sai do loop do órgão se tudo correr bem
                        break

                    except Exception as e:
                        print(f"Erro ao processar órgão {orgao}: {e}")
                        print("Reiniciando o processo para este órgão...")
                        time.sleep(5)  # Espera antes de reiniciar
                        continue

            df = pd.DataFrame(filtered_links, columns=["Links"]).drop_duplicates()
            print(f"Total de links extraídos: {len(df)}")
            return processar_links_df(df)
            
        except Exception as e:
            attempt += 1
            print(f"Tentativa {attempt} falhou. Erro: {str(e)}")
            if attempt < max_attempts:
                time.sleep(5 * attempt)  # Backoff exponencial
            else:
                raise
        finally:
            if driver:
                driver.quit()

def extrair_dados(link):
    max_tentativas = 15
    contador_de_erros = 0
    ultimo_erro = None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive'
    }
    
    session = requests.Session()
    session.verify = False  # Desativa verificação SSL (cuidado em produção)
    
    while contador_de_erros < max_tentativas:
        try:
            tempo_espera = min(2 ** contador_de_erros, 30)  # Backoff exponencial com limite de 30s
            
            if contador_de_erros > 0:
                print(f"Tentativa {contador_de_erros + 1} para {link} (aguardando {tempo_espera}s)")
                time.sleep(tempo_espera)
                
            print(f"Processando: {link}")
            
            # Configuração de timeout e retry
            adapter = requests.adapters.HTTPAdapter(
                max_retries=3,
                pool_connections=10,
                pool_maxsize=10
            )
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            response = session.get(
                link,
                headers=headers,
                timeout=(10, 30),  # 10s para conectar, 30s para receber
                allow_redirects=True
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extração robusta com fallbacks
                identifica = soup.find(class_="identifica") or soup.find('h2')
                dou_paragraph = soup.find_all(class_="dou-paragraph") or soup.find_all('p')
                orgao_dou_data = soup.find(class_="orgao-dou-data") or soup.find('span', {'class': 'publicado-dou-data'})
                publicado_dou_data = soup.find(class_="publicado-dou-data") or soup.find('span', {'class': 'publicado-dou-data'})

                dados = {
                    "DATA_PUB": publicado_dou_data.get_text(strip=True) if publicado_dou_data else None,
                    "IDENTIFICACAO": identifica.get_text(strip=True) if identifica else None,
                    "LINK": link, 
                    "ORGAO": orgao_dou_data.get_text(strip=True) if orgao_dou_data else None,               
                    "TEXTO": " ".join([p.get_text(strip=True) for p in dou_paragraph]) if dou_paragraph else None,
                }
                return dados
            
            print(f"Erro HTTP {response.status_code}: {link}")
            contador_de_erros += 1
            ultimo_erro = f"HTTP {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            print(f"Erro de requisição: {link} - {str(e)}")
            contador_de_erros += 1
            ultimo_erro = f"Request Error: {str(e)}"
            time.sleep(5)
            
        except Exception as e:
            print(f"Erro inesperado: {link} - {str(e)}")
            contador_de_erros += 1
            ultimo_erro = f"Unexpected Error: {str(e)}"
            time.sleep(5)
    
    return {
        "Erro": f"Falha após {max_tentativas} tentativas",
        "Link": link,
        "Detalhe_Erro": ultimo_erro,
        "Tentativas": contador_de_erros
    }
def processar_links_df(df):
    if 'Links' not in df.columns:
        raise ValueError("A coluna 'Links' não está presente no DataFrame.")
    
    resultados = []
    for link in df['Links'].unique():  # Processa apenas links únicos
        if pd.notna(link):
            resultado = extrair_dados(link)
            resultados.append(resultado)

    df_resultado = pd.DataFrame(resultados)
    
    if df_resultado.empty or "ORGAO" not in df_resultado.columns:
        print("Nenhum órgão relacionado realizou publicação neste dia.")
        return pd.DataFrame()
    
    # Processamento adicional
    df_resultado["CODIGO"] = df_resultado["ORGAO"].apply(obter_codigo_orgao)
    df_resultado["SIGLA"] = df_resultado["ORGAO"].apply(obter_sigla_orgao)
    
    # Reordenar colunas
    colunas = ["DATA_PUB", "IDENTIFICACAO", "LINK", "ORGAO", "CODIGO", "SIGLA", "TEXTO"]
    df_resultado = df_resultado[colunas]
    
    # Converter data
    try:
        df_resultado["DATA_PUB"] = pd.to_datetime(
            df_resultado['DATA_PUB'], 
            dayfirst=True, 
            errors='coerce'
        ).dt.strftime('%Y/%m/%d')
    except Exception as e:
        print(f"Erro ao converter datas: {e}")
        df_resultado["DATA_PUB"] = None
    
    # Filtrar por padrão de texto
    pattern = (
        r'nomear|vacância|redistribuido|licença|Deixar Vago|Afastamento|aposentadoria|'
        r'Tornar sem efeito|reverter|nomeia|nomeei|nomeado|Nomeando|Nomeação|'
        r'Exonerar|Exonera|Exonerou|Exonerado|Exonerando|Exoneração|designar|'
        r'Designar|designou|designado|designando|designação|dispensar|dispensa|'
        r'dispensou|Dispensado|dispensando|vago|declara vacância|aposentar|'
        r'aposenta|aposentou|aposentado|aposentando|concessão de aposentadoria|'
        r'redistribuir|redistribui|redistribuiu|redistribuído|redistribuindo|'
        r'redistribuição|remover|remove|removeu|removido|removendo|remoção|'
        r'ceder|cede|cedeu|cedido|cedendo|cessão|requisitar|requisita|'
        r'requisitou|Requisitado|requisitando|requisição|substituir|substitui|'
        r'substituiu|substituído|substituindo|substituição|reconduzir|reconduz|'
        r'reconduziu|reconduzido|Reconduzindo|recondução|Reintegrar|reintegra|'
        r'reintegrou|reintegrado|reintegrando|reintegração|readaptar|readapta|'
        r'readaptou|readaptado|readaptando|readaptação|demitir|demite|demitiu|'
        r'demitido|demitindo|demissão|destituir|destitui|destituiu|destituído|'
        r'destituindo|destituição|licenciar|licencia|licenciou|licenciado|'
        r'licenciando|afastar|afasta|afastou|afastado|afastando|afastamento|'
        r'posse|assumir exercício|assumindo exercício|falecimento|declarar vago|'
        r'(art\.?(?:igo)?\s*(?:7|8|9|10|13|15|18|20|22|24|25|27|28|29|30|31|32|'
        r'33|34|35|36|37|44|81|82|83|84|85|86|90|91|92|93|94|95|96|127|132|147|'
        r'186|202)(?:º)?)'
    )
    
    try:
        df_resultado = df_resultado[
            df_resultado['TEXTO'].str.contains(
                pattern, 
                flags=re.IGNORECASE, 
                regex=True, 
                na=False
            )
        ]
    except Exception as e:
        print(f"Erro ao filtrar por padrão de texto: {e}")
    
    return df_resultado

def obter_codigo_orgao(orgao):
    if not isinstance(orgao, str):
        return None
    
    orgao_lower = orgao.lower()
    for chave, codigo in mapa_orgao_codigos.items():
        if chave.lower() in orgao_lower:
            return codigo
    if "ministério público da união" in orgao_lower:
        return 94
    return None

def obter_sigla_orgao(orgao):
    if not isinstance(orgao, str):
        return None
    
    orgao_lower = orgao.lower()
    for chave, sigla in mapa_orgao_siglas.items():
        if chave.lower() in orgao_lower:
            return sigla
    if "ministério público da união" in orgao_lower:
        return "MPU"
    return None