import cohere
import streamlit as st
import docx
import pandas as pd

# Configurar sua chave da API do Cohere usando secrets
# Configurar sua chave da API do Cohere usando o secrets
cohere_client = cohere.Client(st.secrets["COHERE_API_KEY"])


# Função para extrair o texto de um arquivo Word (DOCX)
def extrair_texto_de_word(caminho_word):
    doc = docx.Document(caminho_word)
    texto_completo = ""
    for paragrafo in doc.paragraphs:
        texto_completo += paragrafo.text + "\n"
    return texto_completo

# Função para extrair e combinar os dados de vários arquivos Excel
def extrair_texto_de_multiplos_excels(lista_caminhos_excels, limite_linhas=1000):
    texto_total = ""
    for caminho_excel in lista_caminhos_excels:
        df = pd.read_excel(caminho_excel)
        df = df.head(limite_linhas)  # Limitar o número de linhas extraídas
        texto_total += df.to_string(index=False) + "\n\n"
    return texto_total

# Função para usar o Cohere para responder perguntas sobre os dados dos arquivos
def perguntar_ia_sobre_arquivos(texto_words, texto_excel, pergunta):
    prompt = f"""
    Você é um assistente especializado em fornecer respostas claras e humanas. Seu papel é ajudar o usuário com base nas informações extraídas de arquivos. Seja acolhedor e empático ao responder. Ao responder, certifique-se de incluir os detalhes mais relevantes e fornecer uma explicação clara e completa. Seja o mais humano possível em sua abordagem, mostrando compreensão e oferecendo suporte ao usuário.

    Aqui estão os dados extraídos de dois tipos de arquivos:

    **Arquivos Word (CNPJ e transportadoras):**
    {texto_words[:5000]}  # Limitar texto enviado para a IA
    
    **Arquivos Excel (SAC, números de notas fiscais, datas de entrega):**
    {texto_excel[:5000]}  # Limitar texto enviado para a IA

    **Pergunta do usuário:** {pergunta}
    
    Por favor, responda de forma acolhedora, humana e clara, e inclua todos os detalhes relevantes para ajudar o usuário a entender completamente a resposta. Certifique-se de validar a dúvida do usuário e oferecer insights baseados nos dados fornecidos.
    """

    response = cohere_client.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    
    return response.generations[0].text

# Caminhos fixos para os arquivos Word e Excel
caminhos_words = ["Transportadoras.docx", "Manual_Devolucao.docx"]
caminhos_excels = ["Base.xlsx", "Teste.xlsx"]

# Extrair texto de todos os arquivos Word e do Excel
texto_words = ""
for caminho_word in caminhos_words:
    texto_words += extrair_texto_de_word(caminho_word)

texto_excel = extrair_texto_de_multiplos_excels(caminhos_excels, limite_linhas=50)

# Interface do Streamlit
st.title("Consulta de Dados Logistica Reversa - PSD")

# Caixa de texto para o usuário fazer perguntas
pergunta = st.text_input("Digite a sua pergunta sobre os dados:")

# Botão para iniciar a consulta
if st.button("Consultar"):
    if pergunta:
        resposta = perguntar_ia_sobre_arquivos(texto_words, texto_excel, pergunta)
        st.write("Resposta da IA:", resposta)
    else:
        st.write("Por favor, digite uma pergunta.")
