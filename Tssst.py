import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
from io import BytesIO
from difflib import SequenceMatcher

st.set_page_config(page_title="Verificador NF x RMA", layout="wide")

# 🚚 Transportadoras
transportadoras = {
    "BRASPRESS": {
        "razao_social": "BRASPRESS TRANSPORTES URGENTES LTDA",
        "cnpj": "48740351000327",
        "ie": "9030546625",
        "endereco": "RUA JOAO BETTEGA, 3802 – CIDADE INDUSTRIAL",
        "cidade": "CURITIBA",
        "uf": "PR"
    },
    "CRUZEIRO DO SUL": {
        "razao_social": "VIACAO CRUZEIRO DO SUL LTDA",
        "cnpj": "03232675006195",
        "ie": "",
        "endereco": "AVENIDA DEZ DE DEZEMBRO, 5680 – JARDIM PIZA",
        "cidade": "LONDRINA",
        "uf": "PR"
    },
    "FL BRASIL": {
        "razao_social": "FL BRASIL HOLDIND, LOGISTICA",
        "cnpj": "18233211002850",
        "ie": "9076066008",
        "endereco": "RODOVIA BR 116, 22301 – TATUQUARA",
        "cidade": "CURITIBA",
        "uf": "PR"
    },
    "LOCAL EXPRESS": {
        "razao_social": "LOCAL EXPRESS TRANSPORTES E LOGISTICA",
        "cnpj": "06199523000195",
        "ie": "9030307558",
        "endereco": "RUA FORMOSA, 131 – PLANTA PORTAL DA SERRA",
        "cidade": "PINHAIS",
        "uf": "PR"
    },
    "RODONAVES": {
        "razao_social": "RODONAVES TRANSPORTES E ENCOMENDAS LTDA",
        "cnpj": "44914992001703",
        "ie": "6013031914",
        "endereco": "RUA RIO GRANDE DO NORTE, 1200, , CENTRO",
        "cidade": "LONDRINA",
        "uf": "PR"
    }
}

# 🔧 Funções auxiliares
def extrair_texto_pdf(file_bytes):
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

def renderizar_primeira_pagina(file_bytes):
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        return doc[0].get_pixmap(dpi=120).tobytes("png")

def buscar_regex_global(texto, padrao):
    match = re.search(padrao, texto, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None

def similaridade(a, b):
    a = re.sub(r'[^a-zA-Z0-9]', '', a or '').lower()
    b = re.sub(r'[^a-zA-Z0-9]', '', b or '').lower()
    return SequenceMatcher(None, a, b).ratio()

def frete_equivalente(valor_nf):
    if not valor_nf:
        return False
    return any(x in valor_nf.upper() for x in ['FOB', 'DEST', 'REMET', 'REMETENTE', 'DESTINATÁRIO'])

def buscar_nome_endereco_cliente(texto):
    partes = texto.split("NATUREZA DA OPERAÇÃO")[0]
    linhas = partes.strip().splitlines()
    nome = linhas[0] if len(linhas) > 0 else None
    endereco = linhas[1] if len(linhas) > 1 else None
    return nome, endereco

# 🧠 Analisador principal
def analisar_dados(texto_nf, texto_rma):
    resultado = []

    # Nome e Endereço Cliente
    nome_nf, endereco_nf = buscar_nome_endereco_cliente(texto_nf)
    nome_rma = buscar_regex_global(texto_rma, r'Nome/Raz[aã]o\s*Social:\s*(.*?)\n')
    endereco_rma = buscar_regex_global(texto_rma, r'Endere[cç]o:\s*(.*?)\s+CEP')
    resultado.append(("Nome Cliente", nome_nf, nome_rma, similaridade(nome_nf, nome_rma) > 0.85))
    resultado.append(("Endereço Cliente", endereco_nf, endereco_rma, similaridade(endereco_nf, endereco_rma) > 0.85))

    # CNPJ
    cnpj_nf = buscar_regex_global(texto_nf, r'\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}')
    cnpj_rma = buscar_regex_global(texto_rma, r'CPF/CNPJ\s*[:\s]*([\d./-]+)')
    resultado.append(("CNPJ Cliente", cnpj_nf, cnpj_rma, re.sub(r'\D','',cnpj_nf or '') == re.sub(r'\D','',cnpj_rma or '')))

    # Quantidade de Caixas
    qtd_nf = buscar_regex_global(texto_nf, r'QUANTIDADE\s*\n?(\d+)')
    qtd_rma = buscar_regex_global(texto_rma, r'Volume:\s*(\d+)')
    resultado.append(("Quantidade de Caixas", qtd_nf, qtd_rma, qtd_nf == qtd_rma))

    # Peso
    peso_nf = buscar_regex_global(texto_nf, r'PESO L[IÍ]QUIDO\s*\n?([\d.,]+)')
    peso_rma = buscar_regex_global(texto_rma, r'Peso:\s*([\d.,]+)')
    resultado.append(("Peso", peso_nf, peso_rma, peso_nf == peso_rma))

    # Frete
    frete_nf = buscar_regex_global(texto_nf, r'FRETE POR CONTA\s*:?[\s\n]*(.*?)\n')
    frete_rma = buscar_regex_global(texto_rma, r'Frete:\s*(\w+)')
    frete_ok = frete_rma and 'FOB' in frete_rma.upper() and frete_equivalente(frete_nf)
    resultado.append(("Tipo de Frete", frete_nf, frete_rma, frete_ok))

    # CFOP
    cfop_nf = buscar_regex_global(texto_nf, r'\b(5202|6202|6949)\b')
    cfop_rma = buscar_regex_global(texto_rma, r'CFOP:\s*(\d+)')
    resultado.append(("CFOP", cfop_nf, cfop_rma, cfop_nf == cfop_rma))

    # Valor total
    valor_nf = buscar_regex_global(texto_nf, r'VALOR TOTAL DA NOTA\s*\n([\d.,]+)')
    valor_rma = buscar_regex_global(texto_rma, r'Tot\. Liquido\(R\$.*?\):\s*([\d.,]+)')
    try:
        ok_valor = abs(float(valor_nf.replace(',','.')) - float(valor_rma.replace(',','.'))) <= 0.99
    except:
        ok_valor = False
    resultado.append(("Valor Total", valor_nf, valor_rma, ok_valor))

    # Transportadora
    nome_transp_nf = buscar_regex_global(texto_nf, r'RAZ[AÃ]O SOCIAL\s*\n(.*?)\n')
    nome_transp_rma = buscar_regex_global(texto_rma, r'Transportadora:\s*(.*?)(\s|$)')
    dados_ok = False
    if nome_transp_rma in transportadoras:
        d = transportadoras[nome_transp_rma]
        dados_ok = all([
            d["razao_social"].lower() in texto_nf.lower(),
            d["cnpj"].replace(".", "").replace("-", "").replace("/", "") in texto_nf.replace(".", "").replace("-", "").replace("/", ""),
            d["ie"] in texto_nf,
            d["endereco"].lower() in texto_nf.lower(),
            d["cidade"].lower() in texto_nf.lower(),
            d["uf"].lower() in texto_nf.lower()
        ])
    resultado.append(("Transportadora", nome_transp_nf, nome_transp_rma, dados_ok))

    return pd.DataFrame(resultado, columns=["Campo", "Valor NF", "Valor RMA", "Está OK?"])

# 🎯 Interface
st.title("✅ Verificador de Nota Fiscal x RMA")

col1, col2 = st.columns(2)
with col1:
    nf_file = st.file_uploader("📄 Enviar Nota Fiscal (PDF)", type=["pdf"])
with col2:
    rma_file = st.file_uploader("📄 Enviar RMA (PDF)", type=["pdf"])

if not nf_file or not rma_file:
    st.info("👆 Envie os dois PDFs para iniciar.")
    st.stop()

nf_bytes = nf_file.read()
rma_bytes = rma_file.read()
texto_nf = extrair_texto_pdf(BytesIO(nf_bytes))
texto_rma = extrair_texto_pdf(BytesIO(rma_bytes))

st.markdown("### 🔍 Comparação dos Dados")
df = analisar_dados(texto_nf, texto_rma)
df["Status"] = df["Está OK?"].apply(lambda x: "✅" if x else "❌")
st.dataframe(df[["Campo", "Valor NF", "Valor RMA", "Status"]], use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar Relatório CSV", data=csv, file_name="comparacao_nf_rma.csv")

with st.expander("🖼️ Visualizar primeira página dos PDFs"):
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("📑 Nota Fiscal")
        st.image(renderizar_primeira_pagina(BytesIO(nf_bytes)), use_container_width=True)
    with col4:
        st.subheader("📑 RMA")
        st.image(renderizar_primeira_pagina(BytesIO(rma_bytes)), use_container_width=True)
