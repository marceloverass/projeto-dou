import pandas as pd
import time
from g4f.client import Client
client = Client()

# Função para gerar respostas com controle de rate limit
def generate_response(text):
    contador_erros = 0
    while True:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": f"""
                        Usando o seguinte texto:
                        {text}
                        Retorne os resultados da seguinte forma:
                        [
                            {{"ação": "ação realizada","Nome":"Nome do servidor(se houver)", "Cargo": "Cargo do servidor (se houver)"}},{{"ação": "ação realizada","Nome":"Nome do servidor(se houver)", "Cargo": "Cargo do servidor (se houver)"}} 
                        ] 
                        Repita o padrão se houver mais de uma ação.

                        considere como ação somente os seguintes termos: Nomeado, Vacância, redistribuido, aposentadoria, Deixar Vago, Licença, Lotar, Afastamento,Reverter, Designar, Tornar sem efeito Nomeação, Tornar sem efeito vacância, Remover, Afastar, Demitir, Ceder, Remover, Dispensa, Exonerar, Substituir, Reconduzir, Falecimento e Posse . Não considere como ação nenhum termo fora da lista especificada; se nenhum termo casar com os critérios da lista, deixe o campo em branco.

                        Esses documentos serão utilizados em um projeto importante, portanto retorne somente os resultados solicitados corretos e nada mais.
                    """
                }]
            )

            result_text = response.choices[0].message.content

            # Verificações de resposta inválida
            mensagens_invalidas = [
                "rate limit", "too many messages in a row", "one message exceeds",
                "desculpe", "model not found", "request ended with status code 404",
                "claro!", "you have reached your request limit for the hour"
            ]

            if any(msg in result_text.lower() for msg in mensagens_invalidas):
                print(f"Erro na resposta (tentativa {contador_erros + 1}): {result_text[:80]}...")

                contador_erros += 1
                if "you have reached your request limit" in result_text.lower():
                    print("Limite de requisições por hora atingido. Aguardando 1 hora.")
                    time.sleep(5)
                elif contador_erros >= 30:
                    print("30 tentativas com erro. Retornando resposta vazia.")
                    return '[]'
                elif contador_erros >= 10:
                    time.sleep(10)
                else:
                    time.sleep(3)
                continue

            # Resposta válida
            return result_text

        except Exception as e:
            print(f"Erro na chamada da API (tentativa {contador_erros + 1}): {e}")
            contador_erros += 1
            if contador_erros >= 20:
                print("20 falhas consecutivas. Retornando resposta vazia.")
                return '[]'
            time.sleep(5)



# Função para processar DataFrame e atualizar status
def ler_dataframe_diario(df):
    texts_array = df['TEXTO'].tolist()
    responses = []
    inicio = time.time()

    i = 0
    while i < len(texts_array):
        text = texts_array[i]
        response = generate_response(text)

        # Verifica se a resposta é um erro conhecido e tenta novamente a mesma linha
        if "you have reached your request limit for the hour" in response.lower() or \
           "rate limit" in response.lower() or \
           response.strip() == "":
            print(f"Tentativa falhou na linha {i + 1}, repetindo após aguardar.")
            time.sleep(8)  
            continue  # Volta para a mesma linha
        else:
            responses.append(response)
            print(f"Processando linha {i + 1}/{len(texts_array)}: {response}")
            i += 1  # Só avança se a resposta for válida

    df['Resposta_Gerada'] = responses
    fim = time.time()
    execucao = (fim - inicio) / 60
    print(f'Processamento completo em {execucao:.2f} minutos.')
    return df


#print(generate_response(""))

