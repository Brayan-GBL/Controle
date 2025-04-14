import streamlit as st
import fitz  # PyMuPDF
import PyPDF2
import pandas as pd
import re
import xml.etree.ElementTree as ET
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

def extrair_campos_nf(texto_nf):
    return {
        "nome_cliente": buscar_regex(texto_nf, r"(?<=\n)[A-Z ]{5,}(?=\n)"),
        "cnpj_cliente": buscar_regex(texto_nf, r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"),
        "endereco_cliente": buscar_regex(texto_nf, r"AV.*?UVARANAS.*"),
        "quantidade_caixas": buscar_regex(texto_nf, r"QUANTIDADE\s*(\d+)"),
        "peso": buscar_regex(texto_nf, r"PESO (?:BRUTO|L[IÍ]QUIDO)\s*([\d.,]+)"),
        "frete": buscar_regex(texto_nf, r"FRETE POR CONTA\s*\n(.*?)\n"),
        "cfop": buscar_regex(texto_nf, r"\b(5202|6202|6949)\b"),
        "valor_total": buscar_regex(texto_nf, r"VALOR TOTAL DA NOTA\s*[\n:]\s*([\d.,]+)"),
        "transportadora_razao": buscar_regex(texto_nf, r"RAZ[AÃ]O SOCIAL\s*\n(.*?)\n"),
        "transportadora_cnpj": buscar_regex(texto_nf, r"\n(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})\n"),
        "transportadora_ie": buscar_regex(texto_nf, r"INSCRI[ÇC][ÃA]O ESTADUAL\s*\n(\d{8,})"),
        "transportadora_endereco": buscar_regex(texto_nf, r"ENDERE[ÇC]O\s*\n(.*?)\n"),
        "transportadora_cidade": buscar_regex(texto_nf, r"MUNIC[IÍ]PIO\s*\n(.*?)\n"),
        "transportadora_uf": buscar_regex(texto_nf, r"UF\s*\n(\w{2})")
    }

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

def extrair_dados_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

    dest = root.find('.//nfe:dest', ns)
    vol = root.find('.//nfe:vol', ns)
    transp = root.find('.//nfe:transporta', ns)

    frete_map = {
        '0': 'Emitente',
        '1': 'Destinatário',
        '2': 'Terceiros',
        '9': 'Sem Frete'
    }
    mod_frete_codigo = root.findtext('.//nfe:modFrete', default='', namespaces=ns)
    mod_frete = frete_map.get(mod_frete_codigo, mod_frete_codigo)

    endereco_logradouro = dest.findtext('nfe:enderDest/nfe:xLgr', default='', namespaces=ns)
    endereco_numero = dest.findtext('nfe:enderDest/nfe:nro', default='', namespaces=ns)
    endereco_cliente = f"{endereco_logradouro}, {endereco_numero}".strip(', ')

    return {
        "nome_cliente": dest.findtext('nfe:xNome', default='', namespaces=ns),
        "cnpj_cliente": dest.findtext('nfe:CNPJ', default='', namespaces=ns),
        "endereco_cliente": endereco_cliente,
        "quantidade_caixas": vol.findtext('nfe:qVol', default='', namespaces=ns),
        "peso": vol.findtext('nfe:pesoL', default='', namespaces=ns),
        "frete": mod_frete,
        "cfop": root.findtext('.//nfe:CFOP', default='', namespaces=ns),
        "valor_total": root.findtext('.//nfe:vNF', default='', namespaces=ns),
        "transportadora_razao": transp.findtext('nfe:xNome', default='', namespaces=ns),
        "transportadora_cnpj": transp.findtext('nfe:CNPJ', default='', namespaces=ns),
        "transportadora_ie": transp.findtext('nfe:IE', default='', namespaces=ns),
        "transportadora_endereco": transp.findtext('nfe:xEnder', default='', namespaces=ns),
        "transportadora_cidade": transp.findtext('nfe:xMun', default='', namespaces=ns),
        "transportadora_uf": transp.findtext('nfe:UF', default='', namespaces=ns),
    }

import requests
import base64
from PIL import Image
from lxml import html

# ======================== CAPTCHA SEFAZ =============================
def consultar_nfe_publica(chave):
    import re
    session = requests.Session()
    url = 'https://www.nfe.fazenda.gov.br/portal/consulta.aspx?tipoConsulta=completa'
    response = session.get(url)
    html_content = response.text
    base64_match = re.search(r'data:image/png;base64,([^"']+)', html_content)

    if base64_match:
        img_base64 = img_data[0].split(',')[-1]
        image_bytes = base64.b64decode(img_base64)
        image = Image.open(BytesIO(image_bytes))
        st.image(image, caption="Digite o código da imagem (CAPTCHA)")
        captcha = st.text_input("🔐 Código CAPTCHA", key="captcha")
        if captcha:
            st.info("📡 Enviando dados para SEFAZ...")
            st.warning("🚧 Integração com consulta pública ainda em desenvolvimento.")
    else:
        st.error("❌ Não foi possível carregar o captcha da SEFAZ.")


# =========================== INTERFACE ================================
st.title("✅ Verificador de Nota Fiscal x RMA")

col1, col2, col3 = st.columns(3)
with col1:
    nf_file = st.file_uploader("📄 Enviar Nota Fiscal (PDF)", type=["pdf"])
with col2:
    rma_file = st.file_uploader("📄 Enviar RMA (PDF)", type=["pdf"])
with col3:
    xml_file = st.file_uploader("🧾 Enviar XML da NF-e", type=["xml"])

chave_manual = st.text_input("🔑 Caso não tenha o XML, cole a chave de acesso (44 dígitos)")

if st.button("🔍 Buscar NF pela Chave") and chave_manual:
    consultar_nfe_publica(chave_manual)
    st.stop()

if rma_file:
    rma_bytes = rma_file.read()
    texto_rma = extrair_texto_pdf(rma_bytes)

    if xml_file:
        dados_nf = extrair_dados_xml(xml_file)
        origem = "XML"
    elif nf_file:
        nf_bytes = nf_file.read()
        texto_nf = extrair_texto_com_pypdf2(nf_bytes)
        dados_nf = extrair_campos_nf(texto_nf)
        origem = "PDF"
    else:
        st.info("👆 Envie a NF, XML ou use a chave de acesso.")
        st.stop()

    def analisar_dados(nf, rma_texto):
        def extrair(p): return buscar_regex(rma_texto, p)
        rma = {
            "nome_cliente": extrair(r'Nome/Raz[aã]o\s*Social:\s*(.*?)\n'),
            "endereco_cliente": extrair(r'Endere[cç]o:\s*(.*?)\s+CEP'),
            "cnpj_cliente": extrair(r'CPF/CNPJ\s*[:\s]*([\d./-]+)'),
            "quantidade_caixas": extrair(r'Volume:\s*(\d+)'),
            "peso": extrair(r'Peso:\s*([\d.,]+)'),
            "frete": extrair(r'Frete:\s*(\w+)'),
            "cfop": extrair(r'CFOP:\s*(\d+)'),
            "valor_total": extrair_valor_total_rma(rma_texto),
            "transportadora_razao": extrair(r'Transportadora:\s*(.*?)(\s|$)')
        }

        resultado = []
        for campo, val_nf in nf.items():
            if campo not in rma:
                continue
            val_rma = rma[campo]
            if campo == "valor_total":
                try:
                    ok = abs(float(val_nf.replace(',', '.')) - float(val_rma.replace(',', '.'))) <= 0.99
                except:
                    ok = False
            else:
                ok = similaridade(val_nf or '', val_rma or '') > 0.85
            resultado.append((campo.replace('_', ' ').title(), val_nf, val_rma, ok))

        nome_rma = rma.get("transportadora_razao")
        transp_ok = False
        if nome_rma and nome_rma in transportadoras:
            d = transportadoras[nome_rma]
            transp_ok = all([
                d["razao_social"].lower() in (nf.get("transportadora_razao") or '').lower(),
                d["cnpj"] in (nf.get("transportadora_cnpj") or ''),
                d["ie"] in (nf.get("transportadora_ie") or ''),
                d["endereco"].lower() in (nf.get("transportadora_endereco") or '').lower(),
                d["cidade"].lower() in (nf.get("transportadora_cidade") or '').lower(),
                d["uf"].lower() in (nf.get("transportadora_uf") or '').lower()
            ])
        resultado.append(("Transportadora", nf.get("transportadora_razao"), nome_rma, transp_ok))
        return pd.DataFrame(resultado, columns=["Campo", "Valor NF", "Valor RMA", "Status"])

    df_result = analisar_dados(dados_nf, texto_rma)
    df_result["Status"] = df_result["Status"].apply(lambda x: "✅" if x else "❌")

    st.markdown(f"### 📋 Comparação dos Dados (Origem da NF: {origem})")
    st.dataframe(df_result, use_container_width=True)

    csv = df_result.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar Relatório CSV", data=csv, file_name="comparacao_nf_rma.csv")

    with st.expander("🖼️ Visualizar PDFs"):
        colA, colB = st.columns(2)
        with colA:
            st.subheader("📑 Nota Fiscal")
            if nf_file:
                st.image(renderizar_primeira_pagina(BytesIO(nf_bytes)), use_column_width=True)
            else:
                st.info("NF não enviada.")
        with colB:
            st.subheader("📑 RMA")
            st.image(renderizar_primeira_pagina(BytesIO(rma_bytes)), use_column_width=True)
else:
    st.info("👆 Envie ao menos a RMA para iniciar a verificação.")
