import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
from io import BytesIO

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
        "endereco": "R FORMOSA, 131 – PLANTA PORTAL DA SERRA",
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

# 🔎 Utilitários
def extrair_texto_pdf(file_bytes):
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

def renderizar_primeira_pagina(file_bytes):
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        return doc[0].get_pixmap(dpi=120).tobytes("png")

def extrair_campo(regex, texto, limpar=None):
    match = re.search(regex, texto)
    if not match:
        return None
    valor = match.group(1).strip()
    return re.sub(limpar, '', valor) if limpar else valor

def comparar_enderecos_simples(end1, end2):
    limpar = lambda s: re.sub(r'[^a-zA-Z0-9]', '', s or '').lower()
    return limpar(end1) == limpar(end2)

# 🧠 Lógica de verificação
def analisar_dados(texto_nf, texto_rma):
    resultado = []

    cnpj_nf = extrair_campo(r'CNPJ/CPF\s*[:\s]*([\d./-]+)', texto_nf, r'\D')
    cnpj_rma = extrair_campo(r'CPF/CNPJ\s*[:\s]*([\d./-]+)', texto_rma, r'\D')
    resultado.append(("CNPJ Cliente", cnpj_nf, cnpj_rma, cnpj_nf == cnpj_rma))

    endereco_nf = extrair_campo(r'LIVRARIA.*?\n(.*?)\n', texto_nf)
    endereco_rma = extrair_campo(r'Endereço:\s*(.*?)\s+CEP', texto_rma)
    resultado.append(("Endereço Cliente", endereco_nf, endereco_rma, comparar_enderecos_simples(endereco_nf, endereco_rma)))

    volume_nf = extrair_campo(r'QUANTIDADE\s*\n(\d+)', texto_nf)
    volume_rma = extrair_campo(r'Volume:\s*(\d+)', texto_rma)
    resultado.append(("Quantidade de Caixas", volume_nf, volume_rma, volume_nf == volume_rma))

    peso_nf = extrair_campo(r'PESO LÍQUIDO\s*\n([\d.,]+)', texto_nf)
    peso_rma = extrair_campo(r'Peso:\s*([\d.,]+)', texto_rma)
    resultado.append(("Peso", peso_nf, peso_rma, peso_nf == peso_rma))

    frete_nf = extrair_campo(r'FRETE POR CONTA\s*\n(.*?)\n', texto_nf)
    frete_rma = extrair_campo(r'Frete:\s*(\w+)', texto_rma)
    frete_valido = frete_nf and 'FOB' in frete_nf.upper() and frete_rma and 'FOB' in frete_rma.upper()
    resultado.append(("Tipo de Frete", frete_nf, frete_rma, frete_valido))

    cfop_nf = extrair_campo(r'\n(5202|6202|6949)\n', texto_nf)
    cfop_rma = extrair_campo(r'CFOP:\s*(\d+)', texto_rma)
    cfop_valido = cfop_nf in ['5202', '6202', '6949']
    resultado.append(("CFOP", cfop_nf, cfop_rma, cfop_valido))

    valor_nf = extrair_campo(r'VALOR TOTAL DA NOTA\s*\n([\d.,]+)', texto_nf)
    valor_rma = extrair_campo(r'Tot\. Liquido\(R\$.*?\):\s*([\d.,]+)', texto_rma)
    try:
        valor_nf_f = float(valor_nf.replace(',', '.'))
        valor_rma_f = float(valor_rma.replace(',', '.'))
        tolerancia_valor = abs(valor_nf_f - valor_rma_f) <= 0.99
    except:
        tolerancia_valor = False
    resultado.append(("Valor Total", valor_nf, valor_rma, tolerancia_valor))

    nome_transp_nf = extrair_campo(r'TRANSPORTADOR / VOLUMES TRANSPORTADOS\s*\n(.*?)\n', texto_nf)
    nome_transp_rma = extrair_campo(r'Transportadora:\s*(.*?)(\s|$)', texto_rma)
    nome_valido = nome_transp_rma in transportadoras and nome_transp_nf and transportadoras[nome_transp_rma]["razao_social"].lower() in texto_nf.lower()
    resultado.append(("Transportadora", nome_transp_nf, nome_transp_rma, nome_valido))

    return pd.DataFrame(resultado, columns=["Campo", "Valor NF", "Valor RMA", "Está OK?"])

# 🖥️ Interface
st.title("✅ Verificador de Nota Fiscal x RMA")

col1, col2 = st.columns(2)
with col1:
    nf_file = st.file_uploader("📄 Enviar Nota Fiscal (PDF)", type=["pdf"], key="nf")
with col2:
    rma_file = st.file_uploader("📄 Enviar RMA (PDF)", type=["pdf"], key="rma")

if not nf_file or not rma_file:
    st.info("👆 Envie os dois PDFs para iniciar a verificação.")
    st.stop()

# Processamento seguro
nf_bytes = nf_file.read()
rma_bytes = rma_file.read()

try:
    texto_nf = extrair_texto_pdf(BytesIO(nf_bytes))
    texto_rma = extrair_texto_pdf(BytesIO(rma_bytes))
except Exception as e:
    st.error(f"❌ Erro ao ler os arquivos PDF: {e}")
    st.stop()

# Comparação
st.markdown("### 🔍 Comparação dos Dados")
df_resultado = analisar_dados(texto_nf, texto_rma)
st.dataframe(df_resultado, use_container_width=True)

# Exportar CSV
csv = df_resultado.to_csv(index=False).encode('utf-8')
st.download_button("📥 Baixar Relatório CSV", data=csv, file_name="comparacao_nf_rma.csv", mime="text/csv")

# Exibir páginas dos PDFs (só a primeira)
with st.expander("🖼️ Visualizar primeira página dos PDFs"):
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("📑 Nota Fiscal")
        st.image(renderizar_primeira_pagina(BytesIO(nf_bytes)), use_column_width=True)
    with col4:
        st.subheader("📑 RMA")
        st.image(renderizar_primeira_pagina(BytesIO(rma_bytes)), use_column_width=True)
