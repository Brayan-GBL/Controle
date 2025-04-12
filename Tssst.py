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

def extrair_dados_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError:
        st.error("❌ Arquivo XML inválido. Verifique o conteúdo.")
        st.stop()

    ns = {}
    for elem in root.iter():
        if '}' in elem.tag:
            ns['nfe'] = elem.tag.split('}')[0].strip('{')
            break

    dest = root.find('.//nfe:dest', ns)
    vol = root.find('.//nfe:vol', ns)
    transp = root.find('.//nfe:transporta', ns)

    return {
        "nome_cliente": dest.findtext('nfe:xNome', default='', namespaces=ns) if dest is not None else '',
        "cnpj_cliente": dest.findtext('nfe:CNPJ', default='', namespaces=ns) if dest is not None else '',
        "endereco_cliente": f"{dest.findtext('nfe:enderDest/nfe:xLgr', default='', namespaces=ns)}, {dest.findtext('nfe:enderDest/nfe:nro', default='', namespaces=ns)}" if dest is not None else '',
        "quantidade_caixas": vol.findtext('nfe:qVol', default='', namespaces=ns) if vol is not None else '',
        "peso": vol.findtext('nfe:pesoL', default='', namespaces=ns) if vol is not None else '',
        "frete": root.findtext('.//nfe:modFrete', default='', namespaces=ns),
        "cfop": root.findtext('.//nfe:CFOP', default='', namespaces=ns),
        "valor_total": root.findtext('.//nfe:vNF', default='', namespaces=ns),
        "transportadora_razao": transp.findtext('nfe:xNome', default='', namespaces=ns) if transp is not None else '',
        "transportadora_cnpj": transp.findtext('nfe:CNPJ', default='', namespaces=ns) if transp is not None else '',
        "transportadora_ie": transp.findtext('nfe:IE', default='', namespaces=ns) if transp is not None else '',
        "transportadora_endereco": transp.findtext('nfe:xEnder', default='', namespaces=ns) if transp is not None else '',
        "transportadora_cidade": transp.findtext('nfe:xMun', default='', namespaces=ns) if transp is not None else '',
        "transportadora_uf": transp.findtext('nfe:UF', default='', namespaces=ns) if transp is not None else '',
    }
