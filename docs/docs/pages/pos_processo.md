# 📄 Documentação: Etapa Pós-Limpeza no Script de Processamento DOU

Após a execução da função `limpeza_diaria(dia, mes, ano)`, o script segue a seguinte lógica:

1. **Extração e Padronização de Dados**
   Os dados brutos do Diário Oficial da União (DOU) são extraídos com:

   * `scrape_in_links`: coleta os links do DOU.
   * `ler_dataframe_diario`: envia os links para API de IA e interpreta os dados.
   * `raspagem_dataframe`: extrai campos relevantes com expressões regulares.
   * `padronizar_dataframe`: normaliza os dados para o padrão esperado.

2. **Validação do DataFrame Final**

   * Se o `DataFrame` estiver **vazio**, o processo considera que **nenhum dado foi encontrado** para o dia anterior.
   * Um e-mail de erro é enviado via `enviar_email_erro()` e o processo é encerrado.

3. **Inserção no Banco de Dados**
   Se houver dados:

   * A função `inserir_dados()` insere os registros no banco de dados SQL Server.
   * Caso haja erro na conexão ou na inserção de alguma linha, um log de erro é gerado e um e-mail de erro é disparado.

4. **Envio de E-mail de Sucesso**
   Se a inserção for concluída com sucesso:

   * Um e-mail de confirmação é enviado por `enviar_email_sucesso()`.
   * Este e-mail contém:

     * Quantidade total de registros inseridos.
     * Data da execução e data da publicação.
     * Gráficos com distribuição por `TIPO` e `SIGLA` (órgãos).
     * Lista de destinatários em cópia (`cc_list.txt`).

---

### 📊 Fluxograma: Pós-processamento Diário - DOU

```mermaid
flowchart TD
    A[Início - Script Executado] --> B[Calcular Dia de Execução]
    B --> C{Dia útil?}
    C -- Não --> Z[Fim: Não executa em sábados ou domingos]
    C -- Sim --> D[Executa limpeza_diaria(dia, mes, ano)]
    D --> E[scrape_in_links]
    E --> F[ler_dataframe_diario]
    F --> G[raspagem_dataframe]
    G --> H[padronizar_dataframe]
    H --> I{DataFrame vazio?}
    I -- Sim --> J[Enviar e-mail de erro: Nenhum dado processado]
    J --> Z
    I -- Não --> K[inserir_dados()]
    K --> L{Erro na conexão/inserção?}
    L -- Sim --> M[Enviar e-mail de erro com detalhes]
    M --> Z
    L -- Não --> N[Enviar e-mail de sucesso com gráficos]
    N --> Z
```
