import streamlit as st
import fitz  # PyMuPDF
import PyPDF2
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
def extrair_texto_com_pypdf2(file_bytes):
    reader = PyPDF2.PdfReader(BytesIO(file_bytes))
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() + "\n"
    return texto

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
    match = re.search(r"Tot\.\s*Liquido\(R\$.*?\):\s*([\d.,]+)", texto, re.IGNORECASE)
    if match:
        return match.group(1)
    match_alt = re.search(r"TOTAL GERAL\s*([\d.,]+)", texto, re.IGNORECASE)
    if match_alt:
        return match_alt.group(1)
    match_final = re.search(r"TOTAL\s*[:\s]+([\d.,]+)", texto, re.IGNORECASE)
    return match_final.group(1) if match_final else None

def extrair_campos_nf(texto_nf):
    return {
        "nome_cliente": buscar_regex(texto_nf, r"ESCOLA.*"),
        "endereco_cliente": buscar_regex(texto_nf, r"AV\s+GAL\s+CARLOS\s+CAVALCANTI.*"),
        "cnpj_cliente": buscar_regex(texto_nf, r"(?<=REMETENTE.*?)\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"),
        "quantidade_caixas": buscar_regex(texto_nf, r"QUANTIDADE\s*:?.*?(\d+)"),
        "peso": buscar_regex(texto_nf, r"PESO (?:BRUTO|L[IÍ]QUIDO)\s*:?.*?([\d.,]+)"),
        "frete": buscar_regex(texto_nf, r"FRETE POR CONTA\s*:?.*?(\w+)"),
        "cfop": buscar_regex(texto_nf, r"\b(5202|6202|6949)\b"),
        "valor_total": buscar_regex(texto_nf, r"VALOR TOTAL DA NOTA\s+([\d.,]+)"),
        "transportadora_razao": buscar_regex(texto_nf, r"RAZ[\u00c3A]O SOCIAL\s+(.*?)\s+ENDERE[\u00c7C]O"),
        "transportadora_cnpj": buscar_regex(texto_nf, r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"),
        "transportadora_ie": buscar_regex(texto_nf, r"INSCRI[\u00c7C][\u00c3A]O ESTADUAL\s+(\d{8,})"),
        "transportadora_endereco": buscar_regex(texto_nf, r"ENDERE[\u00c7C]O\s+(.*?)\s+MUNIC[IÍ]PIO"),
        "transportadora_cidade": buscar_regex(texto_nf, r"MUNIC[IÍ]PIO\s+(.*?)\s+UF"),
        "transportadora_uf": buscar_regex(texto_nf, r"UF\s+(PR|SC|RS|SP|MG|RJ|ES|BA|CE|PE|AM)")
    }

# (função analisar_dados permanece igual)
# (bloco de interface permanece igual com exibição de texto extraído e imagens)

# Alterações no layout e recuperação da seção de imagem lado a lado
with st.expander("🖼️ Visualizar primeira página dos PDFs"):
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("📑 Nota Fiscal")
        st.image(renderizar_primeira_pagina(BytesIO(nf_bytes)), use_column_width=True)
    with col4:
        st.subheader("📑 RMA")
        st.image(renderizar_primeira_pagina(BytesIO(rma_bytes)), use_column_width=True)
