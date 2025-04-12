import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
from io import BytesIO
from difflib import SequenceMatcher

st.set_page_config(page_title="Verificador NF x RMA", layout="wide")

# ======================== TRANSPORTADORAS =============================
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

# ====================== FUNÇÕES AUXILIARES =======================
def extrair_texto_pdf(file_bytes):
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

def renderizar_primeira_pagina(file_bytes):
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        return doc[0].get_pixmap(dpi=120).tobytes("png")

def limpar_texto(texto):
    return re.sub(r'\s+', ' ', texto or '').strip()

def similaridade(a, b):
    a = limpar_texto(a).lower()
    b = limpar_texto(b).lower()
    return SequenceMatcher(None, a, b).ratio()

def buscar_regex(texto, padrao):
    match = re.search(padrao, texto, flags=re.IGNORECASE)
    if not match:
        return None
    if match.lastindex:
        return match.group(1).strip()
    return match.group(0).strip()

def extrair_valor_total_rma(texto):
    match = re.search(r"TOTAL GERAL\s*(\d{1,3}(?:\.\d{3})*,\d{2})", texto, re.IGNORECASE)
    if match:
        return match.group(1)
    match_alt = re.search(r"TOTAL\s*[:\s]+(\d{1,3}(?:\.\d{3})*,\d{2})", texto, re.IGNORECASE)
    return match_alt.group(1) if match_alt else None

def extrair_campos_nf(texto_nf):
    campos = {
        "nome_cliente": buscar_regex(texto_nf, r"(?<=\n)[A-Z ]{5,}(?=\n)"),
        "endereco_cliente": buscar_regex(texto_nf, r"(?<=\n)[A-Z].*\d{3,}.*(?=\n)"),
        "cnpj_cliente": buscar_regex(texto_nf, r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"),
        "quantidade_caixas": buscar_regex(texto_nf, r"QUANTIDADE\s*\n(\d+)"),
        "peso": buscar_regex(texto_nf, r"PESO L[IÍ]QUIDO\s*\n([\d.,]+)"),
        "frete": buscar_regex(texto_nf, r"FRETE POR CONTA\s*\n(.*?)\n"),
        "cfop": buscar_regex(texto_nf, r"\b(5202|6202|6949)\b"),
        "valor_total": buscar_regex(texto_nf, r"VALOR TOTAL DA NOTA\s*\n([\d.,]+)"),
        "transportadora_razao": buscar_regex(texto_nf, r"TRANSPORTADOR / VOLUMES TRANSPORTADOS\s*\n(.*?)\n") or "",
        "transportadora_cnpj": buscar_regex(texto_nf, r"\n(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})\n"),
        "transportadora_ie": buscar_regex(texto_nf, r"INSCRIÇÃO ESTADUAL\s*\n(\d{8,})"),
        "transportadora_endereco": buscar_regex(texto_nf, r"ENDEREÇO\s*\n(.*?)\n"),
        "transportadora_cidade": buscar_regex(texto_nf, r"MUNIC[IÍ]PIO\s*\n(.*?)\n"),
        "transportadora_uf": buscar_regex(texto_nf, r"UF\s*\n(\w{2})")
    }
    return campos

# =========================== INTERFACE ================================
st.title("✅ Verificador de Nota Fiscal x RMA")
col1, col2 = st.columns(2)
with col1:
    nf_file = st.file_uploader("📄 Enviar Nota Fiscal (PDF)", type=["pdf"])
with col2:
    rma_file = st.file_uploader("📄 Enviar RMA (PDF)", type=["pdf"])

if nf_file and rma_file:
    nf_bytes = nf_file.read()
    rma_bytes = rma_file.read()
    texto_nf = extrair_texto_pdf(nf_bytes)
    texto_rma = extrair_texto_pdf(rma_bytes)

    dados_nf = extrair_campos_nf(texto_nf)
    resultado_df = analisar_dados(dados_nf, texto_rma)
    resultado_df["Status"] = resultado_df["Status"].apply(lambda x: "✅" if x else "❌")

    st.markdown("### 🔍 Comparação dos Dados")
    st.dataframe(resultado_df, use_container_width=True)

    csv = resultado_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar Relatório CSV", data=csv, file_name="comparacao_nf_rma.csv")

    with st.expander("🖼️ Visualizar primeira página dos PDFs"):
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("📑 Nota Fiscal")
            st.image(renderizar_primeira_pagina(BytesIO(nf_bytes)), use_container_width=True)
        with col4:
            st.subheader("📑 RMA")
            st.image(renderizar_primeira_pagina(BytesIO(rma_bytes)), use_container_width=True)
else:
    st.info("👆 Envie os dois PDFs para iniciar a verificação.")
