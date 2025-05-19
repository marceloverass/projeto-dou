# 🤖 Processamento de Publicações do DOU com IA (G4F)

## Objetivo

Este módulo utiliza um modelo de linguagem da API **G4F (GPT-4o)** para realizar a **interpretação semântica das publicações extraídas do DOU**, transformando o texto bruto em estruturas JSON contendo **ações funcionais identificadas** (como nomeações, vacâncias, aposentadorias etc.).

---

## ⚙️ Funcionalidades

* Análise de texto via **IA gratuita (G4F API)**.
* Extração de estruturas JSON padronizadas contendo:

  * Ação funcional (ex: "Nomeado", "Exonerar").
  * Nome do servidor (se identificado).
  * Cargo (se identificado).
* Tolerância a erros e limites de requisições.
* Loop de retentativas com controle de tempo.

---

## 🧩 Módulos Utilizados

* `pandas` – estruturação de dados tabulares.
* `time` – controle de tempo de execução e espera entre tentativas.
* `g4f.client` – API para chamada de modelos GPT open-source gratuitos.

---

## 🔄 Fluxo Principal

### 1. `generate_response(text)`

**Responsável por:**

* Enviar o texto da publicação ao modelo GPT.
* Receber uma resposta JSON estruturada com as ações identificadas.

**Parâmetros da prompt:**

* Texto da publicação do DOU.
* Lista pré-definida de **termos aceitos como ações válidas**.
* Exigência de retorno exclusivamente no formato especificado, como:

```json
[
  {"ação": "Nomeado", "Nome": "João Silva", "Cargo": "Analista"},
  {"ação": "Exonerar", "Nome": "Maria Souza", "Cargo": "Técnica"}
]
```

**Robustez:**

* Tenta até **30 vezes** em caso de erro de resposta.
* Detecta mensagens de erro conhecidas (ex: "rate limit", "model not found").
* Controla o tempo de espera entre tentativas: entre 3 e 10 segundos, com backoff adaptativo.
* Em caso de falhas consecutivas, retorna `'[]'`.

---

### 2. `ler_dataframe_diario(df)`

**Responsável por:**

* Iterar sobre o DataFrame resultante da raspagem do DOU.
* Aplicar `generate_response()` a cada item da coluna `TEXTO`.
* Criar nova coluna `Resposta_Gerada` com os JSONs extraídos por IA.

**Fluxo:**

1. Converte a coluna `TEXTO` em uma lista.
2. Itera por índice com controle explícito:

   * Se a resposta for inválida, repete a mesma linha após esperar.
   * Só avança para o próximo item se a resposta for válida.
3. Calcula o tempo total de execução.
4. Retorna o DataFrame atualizado.

**Saída esperada:**

| TEXTO             | Resposta\_Gerada                                                    |
| ----------------- | ------------------------------------------------------------------- |
| "Fica nomeado..." | `[{"ação": "Nomeado", "Nome": "Carlos Silva", "Cargo": "Diretor"}]` |

---

## 🛡️ Considerações de Robustez

* Resiliência a quedas da API G4F, erros 404, rate limit e respostas irrelevantes.
* Backoff escalonado em tentativas falhas.
* Controle de erro por número de tentativas com log intermediário.
* Garante que a IA responda apenas com o formato JSON solicitado.

---

## 🗃️ Integração com Etapas Anteriores

Este módulo é aplicado **após** o processo de raspagem do DOU (`scrape_in_links` → `processar_links_df`) e utiliza o `DataFrame` resultante, enriquecendo-o com interpretações estruturadas por IA.

---

## 💡 Observações Finais

* A biblioteca `g4f` é experimental e gratuita; portanto, este módulo já contempla **tratamento preventivo contra instabilidade**.
* Caso seja necessário um serviço mais estável ou com SLA, recomenda-se integração futura com a **API oficial da OpenAI ou modelos locais**.
