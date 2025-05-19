# 📄 Manual de Execução – Meu Querido Diário

Este manual explica como executar o sistema **Meu Querido Diário**, responsável por automatizar a coleta, leitura e envio de informações do Diário Oficial da União (DOU).

---

## 🛠️ 1. Requisitos

Para **executar o arquivo `.exe`**, **não é necessário instalar Python**, desde que as bibliotecas estejam embutidas no executável.

Contudo, **se for executar o código diretamente (via `main.py`)**, siga os passos abaixo.

---

## 🐍 2. Instalação do Python e dependências (modo desenvolvedor)

### 2.1. Instale o [Python 3.10+](https://www.python.org/downloads/) (caso ainda não tenha)

Durante a instalação, **marque a opção**:

> ✅ Add Python to PATH

---

### 2.2. Instale as bibliotecas

No terminal (CMD ou PowerShell), vá até a pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

Se não tiver o `requirements.txt`, copie e cole este conteúdo em um novo arquivo:

```txt
pandas
pyodbc
python-dotenv
matplotlib
requests
beautifulsoup4
selenium
webdriver-manager
g4f==0.5.0.4
```

---

## ▶️ 3. Executando o programa

### ✅ Modo 1 – Usuário comum

Apenas **dê dois cliques em `Meu Querido Diário v2.0.exe`** ou execute via terminal:

```bash
.\Meu Querido Diário v2.0.exe
```

Certifique-se de que os arquivos `cc_list_erro.txt` e `cc_list.txt` estejam no mesmo diretório.

---

### 🧪 Modo 2 – Desenvolvedor (via script Python)

Se estiver rodando o código diretamente:

```bash
python -m app.main
```

ou

```bash
python app/main.py
```

---

### 🔄 4. Fluxo de Funcionamento do Sistema

1. A aplicação acessa o [Site do DOU](https://www.in.gov.br/leiturajornal) para obter os links de todas as postagens do dia anterior. Em seguida, lê o HTML de cada link e organiza as informações em um dataframe.
2. Utiliza o [Gf4](https://github.com/xtekky/gpt4free) para interpretar o conteúdo das postagens, retornando um JSON que é adicionado como uma nova coluna no dataframe.
3. Realiza a extração detalhada das informações contidas no JSON retornado.
4. Padroniza os dados no dataframe para garantir consistência e uniformidade.
5. Insere no banco de dados todas as informações coletadas.
6. Caso ocorra algum erro durante o processo, o sistema automaticamente envia um e-mail de notificação para o gerente responsável, detalhando o problema ocorrido.

---

## 🧾 5. Arquivos importantes

* `cc_list.txt`: lista de e-mails que receberão cópia das comunicações.
* `cc_list_erro.txt`: e-mails que receberão alertas em caso de erro.
* `.env`: variáveis sensíveis como senhas, conexões, etc. Exemplo:


