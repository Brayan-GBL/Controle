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
    return SequenceMatcher(None, limpar_texto(a).lower(), limpar_texto(b).lower()).ratio()

def buscar_regex(texto, padrao):
    match = re.search(padrao, texto, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip() if match.lastindex else match.group(0).strip()

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

    # dados do emitente
    emit = root.find('.//nfe:emit', ns)
    transp = root.find('.//nfe:transporta', ns)
    vol = root.find('.//nfe:vol', ns)

    # peso: prioriza bruto
    peso_b = vol.findtext('nfe:pesoB', '0', namespaces=ns) if vol is not None else '0'
    peso_l = vol.findtext('nfe:pesoL', '0', namespaces=ns) if vol is not None else '0'
    peso = peso_b if float(peso_b.replace(',', '.')) > 0 else peso_l

    # frete
    frete_map = {'0': 'Emitente', '1': 'Destinatário', '2': 'Terceiros', '9': 'Sem Frete'}
    mod_frete_codigo = root.findtext('.//nfe:modFrete', '', namespaces=ns)
    frete = frete_map.get(mod_frete_codigo, mod_frete_codigo)

    # endereço emitente
    log = emit.findtext('nfe:enderEmit/nfe:xLgr', '', namespaces=ns)
    nro = emit.findtext('nfe:enderEmit/nfe:nro', '', namespaces=ns)
    endereco_emit = f"{log}, {nro}".strip(', ')

    return {
        'nome_cliente': emit.findtext('nfe:xNome', '', namespaces=ns),
        'cnpj_cliente': emit.findtext('nfe:CNPJ', '', namespaces=ns),
        'endereco_cliente': endereco_emit,
        'quantidade_caixas': vol.findtext('nfe:qVol', '', namespaces=ns) if vol is not None else '',
        'peso': peso,
        'frete': frete,
        'cfop': root.findtext('.//nfe:CFOP', '', namespaces=ns),
        'valor_total': root.findtext('.//nfe:vNF', '', namespaces=ns),
        'transportadora_razao': transp.findtext('nfe:xNome', '', namespaces=ns) if transp is not None else '',
        'transportadora_cnpj': transp.findtext('nfe:CNPJ', '', namespaces=ns) if transp is not None else '',
        'transportadora_ie': transp.findtext('nfe:IE', '', namespaces=ns) if transp is not None else '',
        'transportadora_endereco': transp.findtext('nfe:xEnder', '', namespaces=ns) if transp is not None else '',
        'transportadora_cidade': transp.findtext('nfe:xMun', '', namespaces=ns) if transp is not None else '',
        'transportadora_uf': transp.findtext('nfe:UF', '', namespaces=ns) if transp is not None else ''
    }

# interface
st.title("✅ Verificador de Nota Fiscal x RMA")
col1, col2, col3 = st.columns(3)
with col1:
    nf_file = st.file_uploader("📄 Enviar Nota Fiscal (PDF)", type=["pdf"])
with col2:
    rma_file = st.file_uploader("📄 Enviar RMA (PDF)", type=["pdf"])
with col3:
    xml_file = st.file_uploader("🧾 Enviar XML da NF-e", type=["xml"])

if rma_file:
    rma_bytes = rma_file.read()
    texto_rma = extrair_texto_pdf(rma_bytes)

    if xml_file:
        dados_nf = extrair_dados_xml(xml_file)
        origem = "XML"
        if nf_file: nf_bytes = nf_file.read()
    elif nf_file:
        nf_bytes = nf_file.read()
        texto_nf = extrair_texto_com_pypdf2(nf_bytes)
        dados_nf = extrair_campos_nf(texto_nf)
        origem = "PDF"
    else:
        st.info("👆 Envie a NF ou XML para iniciar a verificação.")
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
            if campo not in rma: continue
            val_rma = rma[campo]
            if campo in ("valor_total", "peso"):
                try:
                    num_nf = float(val_nf.replace('.', '').replace(',', '.'))
                    num_rma = float(val_rma.replace('.', '').replace(',', '.'))
                    tol = 0.99 if campo == "valor_total" else 0.01
                    ok = abs(num_nf - num_rma) <= tol
                except:
                    ok = False
            else:
                ok = similaridade(val_nf or '', val_rma or '') > 0.85
            resultado.append((campo.replace('_', ' ').title(), val_nf, val_rma, ok))

        nome = rma.get("transportadora_razao") or ''
        key = nome if nome in transportadoras else None
        if key:
            d = transportadoras[key]
            transp_rows = [
                ("Transportadora Razao", nf.get("transportadora_razao", ''), d['razao_social'], d['razao_social'].lower() in nf.get("transportadora_razao", '').lower()),
                ("Transportadora CNPJ", nf.get("transportadora_cnpj", ''), d['cnpj'], d['cnpj'] == nf.get("transportadora_cnpj", '')), 
                ("Transportadora IE", nf.get("transportadora_ie", ''), d['ie'], d['ie'] == nf.get("transportadora_ie", '')),
                ("Transportadora Endereco", nf.get("transportadora_endereco", ''), d['endereco'], d['endereco'].lower() in nf.get("transportadora_endereco", '').lower()),
                ("Transportadora Cidade", nf.get("transportadora_cidade", ''), d['cidade'], d['cidade'].lower() == nf.get("transportadora_cidade", '').lower()),
                ("Transportadora UF", nf.get("transportadora_uf", ''), d['uf'], d['uf'] == nf.get("transportadora_uf", ''))
            ]
            resultado.extend(transp_rows)
        else:
            resultado.append(("Transportadora Razao", nome, '', False))

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
