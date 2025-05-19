# 📄 Manual de Execução – Meu Querido Diário

Este manual explica como executar o sistema **Meu Querido Diário**, responsável por automatizar a coleta, leitura e envio de informações do Diário Oficial da União (DOU).

---

## 🛠️ Requisitos

- Para **executar o arquivo `.exe`**, **não é necessário instalar Python**.
- Para **executar o código diretamente (via `main.py`)**, instale o [Python 3.10+](https://www.python.org/downloads/) e as dependências.

---

## 🐍 Instalação do Python e Dependências (Modo Desenvolvedor)

### 1. Instale o Python 3.10+

Baixe e instale o [Python 3.10+](https://www.python.org/downloads/). Durante a instalação, **marque a opção**:

> ✅ Add Python to PATH

---

### 2. Instale as dependências

No terminal, navegue até a pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

Se o arquivo `requirements.txt` não existir, crie um com o seguinte conteúdo:

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

## ▶️ Execução

### ✅ Usuário Comum

Dê dois cliques no arquivo `Meu Querido Diário v2.0.exe` ou execute no terminal:

```bash
.\Meu Querido Diário v2.0.exe
```

Certifique-se de que os arquivos `cc_list.txt` e `cc_list_erro.txt` estejam no mesmo diretório.

---

### 🧪 Desenvolvedor

Se for executar o código diretamente, use um dos comandos abaixo no terminal:

```bash
python -m app.main
```

ou

```bash
python app/main.py
```

---

## 🧾 Observações

- **Arquivos importantes**:
    - `cc_list.txt`: lista de e-mails para cópia das comunicações.
    - `cc_list_erro.txt`: lista de e-mails para alertas em caso de erro.
    - `.env`: arquivo para configurar variáveis sensíveis, como senhas e conexões.
- Certifique-se de que todos os arquivos necessários estejam no mesmo diretório do executável ou script.

