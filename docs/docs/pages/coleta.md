# 📄 Extração de Dados do Diário Oficial da União (DOU)

## Objetivo

Este módulo realiza a **raspagem automatizada de links e dados do Diário Oficial da União (DOU)**, seção 2, a partir de uma data fornecida. O foco principal é identificar **movimentações funcionais**, como nomeações, exonerações, aposentadorias e similares, publicadas por órgãos selecionados.

---

## ⚙️ Funcionalidades

* Raspagem de links do DOU via Selenium.
* Filtragem por órgãos de interesse: `Poder Judiciário`, `Ministério Público da União`, `Conselho Nacional do Ministério Público`.
* Requisição segura e resiliente via `requests` com backoff exponencial.
* Extração e estruturação dos dados relevantes das publicações.
* Filtragem textual com expressões regulares de termos funcionais.
* Enriquecimento com códigos e siglas institucionais via mapeamentos externos.

---

## 🧩 Módulos Utilizados

* `pandas` – estruturação e tratamento de dados.
* `selenium` – raspagem de links dinâmicos no site da Imprensa Nacional.
* `requests` & `BeautifulSoup` – obtenção e parsing dos conteúdos das publicações.
* `re` – expressões regulares para filtragem textual.
* `time`, `urllib3` – controle de tempo e conexão SSL.

---

## 🔄 Fluxo Principal

### 1. `scrape_in_links(dia, mes, ano)`

**Responsável por:**

* Acessar a edição do DOU correspondente à data fornecida.
* Rastrear e coletar os links das publicações de interesse.
* Retornar um `DataFrame` com os dados processados.

**Passos:**

1. Inicia um navegador headless via Selenium.
2. Acessa a URL base do DOU para o dia informado.
3. Seleciona os órgãos de interesse no campo de filtro.
4. Para cada órgão:

   * Navega entre as páginas.
   * Coleta os links das publicações (via seletor `a[href*="web/dou"]`).
5. Cria um `DataFrame` de links.
6. Passa os links únicos para `processar_links_df()`.

---

### 2. `processar_links_df(df)`

**Responsável por:**

* Processar todos os links coletados e estruturar os dados extraídos.

**Passos:**

1. Para cada link, chama a função `extrair_dados(link)`.
2. Cria um `DataFrame` consolidado.
3. Aplica os mapeamentos de `CODIGO` e `SIGLA` do órgão.
4. Formata a data para `YYYY/MM/DD`.
5. Filtra as publicações que contenham termos relevantes via regex extensa.

---

### 3. `extrair_dados(link)`

**Responsável por:**

* Realizar a requisição ao conteúdo da publicação e extrair os dados relevantes.

**Dados extraídos:**

* `DATA_PUB`: Data de publicação.
* `IDENTIFICACAO`: Título ou identificação do ato.
* `ORGAO`: Órgão responsável.
* `TEXTO`: Corpo textual da publicação.
* `LINK`: URL da publicação.

**Lógicas adicionais:**

* Retentativas automáticas com controle de tempo e tratamento de exceções.
* Fallbacks para diferentes seletores HTML (ex: `.dou-paragraph`, `.identifica`, etc.).

---

### 4. `obter_codigo_orgao(orgao)` e `obter_sigla_orgao(orgao)`

**Responsáveis por:**

* Realizar o mapeamento do nome do órgão para seu respectivo código e sigla, usando os dicionários:

  * `mapa_orgao_codigos`
  * `mapa_orgao_siglas`

---

## 🛡️ Robustez do Código

* **Retentativas** com backoff exponencial em `requests` e Selenium.
* **Tratamento de exceções** detalhado para evitar falhas inesperadas.
* **Extração tolerante a falhas** com seletores alternativos e verificações de conteúdo.
* **Desativação de SSL warnings**, útil em ambientes restritivos.

---

## 🔍 Filtros de Texto Aplicados

Utiliza um padrão regex robusto para identificar expressões como:

* `nomear`, `exonerar`, `aposentar`, `licenciar`, `remover`, `redistribuir`, `requisitar`, `substituir`, `falecimento`, etc.
* Expressões formais com base em **artigos de lei**, como: `art. 7º`, `artigo 127`, etc.

---

## 🗃️ Exemplo de Saída (`DataFrame` Final)

| DATA\_PUB  | IDENTIFICACAO        | LINK         | ORGAO      | CODIGO | SIGLA | TEXTO |
| ---------- | -------------------- | ------------ | ---------- | ------ | ----- | ----- |
| 2025/05/13 | Portaria nº 123/2025 | https\://... | Tribunal X | 0001   | TRX   | ...   |

---

## 📎 Observações

* **Dependências**:

  * `app.utils.mapeamento` deve conter os mapeamentos `mapa_orgao_codigos` e `mapa_orgao_siglas`.
* **Ambiente recomendado**:

  * Google Chrome instalado (via `webdriver-manager`).
  * Ideal rodar em ambientes com suporte a `headless Chrome`.

