# 📄 Documentação: Processamento Pós-Leitura por IA

Após a leitura e interpretação inicial dos textos extraídos do Diário Oficial da União por modelos de Inteligência Artificial (IA), o DataFrame resultante (`df`) passa por uma série de etapas de **extração**, **normalização** e **padronização de dados** com o objetivo de consolidar as informações funcionais (nomeações, exonerações, aposentadorias etc.). A seguir, descrevemos detalhadamente essas etapas:

---

## 🔍 1. Extração de Dados JSON da Resposta da IA

### Funções principais:
- `safe_literal_eval(text)`: Avalia strings com estrutura JSON de forma segura.
- `preprocess_string(s)`: Remove caracteres problemáticos como `\n` e `\\`.
- `extract_data(resposta)`: Interpreta a string JSON gerada pela IA e extrai as informações estruturadas.

### Informações extraídas:
Cada entrada JSON deve conter os campos:
- `ação`
- `Nome`
- `Cargo`

Esses dados são transformados em tuplas do tipo `(TIPO, NOME, CARGO)`.

---

## 📊 2. Explosão e Organização do DataFrame

### Processo:
- Coluna `Resposta_Gerada` → aplicada com `extract_data`.
- Resultado explode a coluna `extracted_data` para múltiplas linhas.
- Geração de um novo DataFrame com as colunas:
  - `TIPO` (ação funcional)
  - `NOME` (nome do servidor)
  - `CARGO` (cargo indicado)
- Linhas sem `TIPO` ou `NOME` são descartadas para maior confiabilidade.

---

## 🧹 3. Limpeza e Padronização de Texto

### Funções aplicadas:
- `remover_acentos(texto)`: Remove acentuação de caracteres.
- `limpar_texto(texto)`: Limpa o texto, remove símbolos, acentos e deixa em caixa baixa.

---

## 🧭 4. Mapeamento e Padronização de Tipos de Ações

### Função:
- `padronizar_tipo(texto)`

### Objetivo:
- Consolidar diversas variações de uma mesma ação funcional em categorias padronizadas, como:
  - `"nomear"` para todas as formas de nomeação.
  - `"aposentadoria"` para aposentadorias e benefícios similares.
  - `"dispensa"`, `"exoneracao"`, `"remocao"`, `"designacao"`, etc.

### Casos especiais:
- Ações irrelevantes ou inconsistentes são descartadas.
- Expressões como `"ação realizada"`, `"ajuizar"`, `"aprovar"`, etc., são excluídas do resultado final por não representarem movimentações funcionais.

---

## 🧮 5. Categorização de Tipos em Grupos Funcionais

### Função:
- `categorizar_tipo(tipo)`

### Mapeamento de categorias:
- **Categoria 1 – Entrada**:
  - Ex: `nomear`, `designacao`, `posse`
- **Categoria 2 – Saída**:
  - Ex: `exoneracao`, `dispensa`, `remocao`, `afastamento`, `vacancia`
- **Categoria 3 – Pensão**:
  - Ex: `pensao`, `deferir pensao por morte`, `pensao vitalicia`
- **Categoria 18 – Outros/Não Classificados**

---

## ✅ Resultado Final

O DataFrame final está estruturado com:
- `TIPO`: Ação padronizada (ex: `nomear`, `aposentadoria`)
- `NOME`: Nome da pessoa envolvida
- `CARGO`: Cargo funcional mencionado
- `CATEGORIA`: Número identificador da categoria funcional (ex: 1 = Entrada, 2 = Saída)

Esse DataFrame pode ser utilizado para geração de relatórios, visualizações, análises ou envio automatizado de notificações e atualizações institucionais.

---

## 📁 Exemplo de Linha Final

| TIPO         | NOME               | CARGO                          | CATEGORIA |
|--------------|--------------------|--------------------------------|-----------|
| nomear       | João da Silva      | Técnico Administrativo         | 1         |
| aposentadoria| Maria Oliveira     | Professora EBTT                | 2         |
| remocao      | Carlos Pereira     | Analista Judiciário            | 2         |
