import streamlit as st
import fitz  # PyMuPDF
import PyPDF2
import pandas as pd
import re
import xml.etree.ElementTree as ET
from io import BytesIO
from difflib import SequenceMatcher
import streamlit.components.v1 as components  # <— necessário para o HTML/JS do balão

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

def parse_num(s):
    if not s:
        return 0.0
    txt = s.strip()
    if '.' in txt and ',' in txt:
        txt = txt.replace('.', '').replace(',', '.')
    elif ',' in txt:
        txt = txt.replace(',', '.')
    try:
        return float(txt)
    except:
        return 0.0

def extrair_valor_total_rma(texto):
    match = re.search(r"Tot\.\s*Liquido\(R\$.*?\):\s*([\d.,]+)", texto, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    match_alt = re.search(r"TOTAL GERAL\s*([\d.,]+)", texto, flags=re.IGNORECASE)
    if match_alt:
        return match_alt.group(1)
    match_final = re.search(r"TOTAL\s*[:\s]+([\d.,]+)", texto, flags=re.IGNORECASE)
    return match_final.group(1) if match_final else None

def buscar_regex(texto, pat):
    m = re.search(pat, texto, flags=re.IGNORECASE)
    if not m:
        return None
    return m.group(1).strip() if m.lastindex else m.group(0).strip()

def extrair_campos_nf(texto_nf):
    return {
        'nome_cliente': buscar_regex(texto_nf, r'(?<=\n)[A-Z ]{5,}(?=\n)'),
        'cnpj_cliente': buscar_regex(texto_nf, r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'),
        'endereco_cliente': buscar_regex(texto_nf, r'AV.*?UVARANAS.*'),
        'quantidade_caixas': buscar_regex(texto_nf, r'QUANTIDADE\s*(\d+)'),
        'peso': buscar_regex(texto_nf, r'PESO (?:BRUTO|L[IÍ]QUIDO)\s*([\d.,]+)'),
        'frete': buscar_regex(texto_nf, r'FRETE POR CONTA\s*\n(.*?)\n'),
        'cfop': buscar_regex(texto_nf, r'\b(5202|6202|6949)\b'),
        'valor_total': buscar_regex(texto_nf, r'VALOR TOTAL DA NOTA\s*[\n:]\s*([\d.,]+)'),
        'transportadora_razao': buscar_regex(texto_nf, r'RAZ[AÃ]O SOCIAL\s*\n(.*?)\n'),
        'transportadora_cnpj': buscar_regex(texto_nf, r'\n(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})\n'),
        'transportadora_ie': buscar_regex(texto_nf, r'INSCRI[ÇC][ÃA]O ESTADUAL\s*\n(\d{8,})'),
        'transportadora_endereco': buscar_regex(texto_nf, r'ENDERE[ÇC]O\s*\n(.*?)\n')
    }

def extrair_texto_pdf(file_bytes):
    with fitz.open(stream=file_bytes, filetype='pdf') as doc:
        return '\n'.join(p.get_text() for p in doc)

# ————— ALTERAÇÃO: renderizar até 3 páginas —————
def renderizar_paginas_para_preview(file_bytes, n_paginas: int = 3, dpi: int = 120):
    imagens = []
    with fitz.open(stream=file_bytes, filetype='pdf') as doc:
        total = min(n_paginas, len(doc))
        for pg in range(total):
            pix = doc[pg].get_pixmap(dpi=dpi)
            imagens.append(pix.tobytes('png'))
    return imagens

def similaridade(a, b):
    return SequenceMatcher(None,
        re.sub(r'\s+', ' ', (a or '')).lower(),
        re.sub(r'\s+', ' ', (b or '')).lower()
    ).ratio()

def extrair_dados_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    emit = root.find('.//nfe:emit', ns)
    transp = root.find('.//nfe:transporta', ns)
    vol = root.find('.//nfe:vol', ns)
    pb = vol.findtext('nfe:pesoB', '0', namespaces=ns) if vol is not None else '0'
    pl = vol.findtext('nfe:pesoL', '0', namespaces=ns) if vol is not None else '0'
    peso = pb if parse_num(pb) > 0 else pl
    fmap = {'0':'Emitente','1':'Destinatário','2':'Terceiros','9':'Sem Frete'}
    mf = root.findtext('.//nfe:modFrete','', namespaces=ns)
    frete = fmap.get(mf, mf)
    log = emit.findtext('nfe:enderEmit/nfe:xLgr','',namespaces=ns)
    nro = emit.findtext('nfe:enderEmit/nfe:nro','',namespaces=ns)
    end_emit = f"{log}, {nro}".strip(', ')
    return {
        'nome_cliente': emit.findtext('nfe:xNome','',namespaces=ns),
        'cnpj_cliente': emit.findtext('nfe:CNPJ','',namespaces=ns),
        'endereco_cliente': end_emit,
        'quantidade_caixas': vol.findtext('nfe:qVol','',namespaces=ns) if vol is not None else '',
        'peso': peso,
        'frete': frete,
        'cfop': root.findtext('.//nfe:CFOP','',namespaces=ns),
        'valor_total': root.findtext('.//nfe:vNF','',namespaces=ns),
        'transportadora_razao': transp.findtext('nfe:xNome','',namespaces=ns) if transp is not None else '',
        'transportadora_cnpj': transp.findtext('nfe:CNPJ','',namespaces=ns) if transp is not None else '',
        'transportadora_ie': transp.findtext('nfe:IE','',namespaces=ns) if transp is not None else '',
        'transportadora_endereco': transp.findtext('nfe:xEnder','',namespaces=ns) if transp is not None else ''
    }

# =========================== INTERFACE ================================
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
        origem = 'XML'
        if nf_file: nf_bytes = nf_file.read()
    elif nf_file:
        nf_bytes = nf_file.read()
        texto_nf = extrair_texto_com_pypdf2(nf_bytes)
        dados_nf = extrair_campos_nf(texto_nf)
        origem = 'PDF'
    else:
        st.info("👆 Envie a NF ou XML para iniciar a verificação.")
        st.stop()

    def analisar_dados(nf, rma_texto):
        def ext(p): return buscar_regex(rma_texto, p)
        rma = {
            'nome_cliente': ext(r'Nome/Raz[aã]o\s*Social:\s*(.*?)\n'),
            'endereco_cliente': ext(r'Endere[cç]o:\s*(.*?)\s+CEP'),
            'cnpj_cliente': ext(r'CPF/CNPJ\s*[:\s]*([\d./-]+)'),
            'quantidade_caixas': ext(r'Volume:\s*(\d+)'),
            'peso': ext(r'Peso:\s*([\d.,]+)'),
            'frete': ext(r'Frete:\s*(\w+)'),
            'cfop': ext(r'CFOP:\s*(\d+)'),
            'valor_total': extrair_valor_total_rma(rma_texto),
            'transportadora_razao': ext(r'Transportadora:\s*(.*?)(\s|$)')
        }

        rows = []
        for campo, v_nf in nf.items():
            if campo not in rma: continue
            v_r = rma[campo]
            if campo in ('valor_total','peso'):
                tol = 0.99 if campo=='valor_total' else 0.01
                ok = abs(parse_num(v_nf) - parse_num(v_r)) <= tol
            else:
                ok = similaridade(v_nf, v_r) > 0.85
            rows.append((campo.replace('_',' ').title(), v_nf, v_r, ok))

        xml_name = nf.get('transportadora_razao','')
        match = None
        for key, base in transportadoras.items():
            if base['razao_social'].lower() in xml_name.lower() or xml_name.lower() in base['razao_social'].lower() or similaridade(xml_name, base['razao_social'])>0.8:
                match = key
                break
        if match:
            base = transportadoras[match]
            rows.extend([
                ('Transportadora Razao', xml_name, base['razao_social'], base['razao_social'].lower() in xml_name.lower()),
                ('Transportadora CNPJ', nf.get('transportadora_cnpj',''), base['cnpj'], base['cnpj']==nf.get('transportadora_cnpj','')),
                ('Transportadora IE', nf.get('transportadora_ie',''), base['ie'], base['ie']==nf.get('transportadora_ie','')),
                ('Transportadora Endereco', nf.get('transportadora_endereco',''), base['endereco'], base['endereco'].lower() in nf.get('transportadora_endereco','').lower())
            ])
        else:
            rows.append(('Transportadora Razao', xml_name, '', False))

        return pd.DataFrame(rows, columns=['Campo','Valor NF','Valor RMA','Status'])

    df = analisar_dados(dados_nf, texto_rma)
    df['Status'] = df['Status'].apply(lambda x:'✅' if x else '❌')

    st.markdown(f"### 📋 Comparação dos Dados (Origem da NF: {origem})")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Relatório CSV", data=csv, file_name='comparacao_nf_rma.csv')

    with st.expander("🖼️ Visualizar PDFs"):
        imgs_nf  = renderizar_paginas_para_preview(BytesIO(nf_bytes), n_paginas=3)
        imgs_rma = renderizar_paginas_para_preview(BytesIO(rma_bytes), n_paginas=3)

        col_nf, col_rma = st.columns(2)

        with col_nf:
            st.subheader("📑 Nota Fiscal")
            for img in imgs_nf:
                st.image(img, use_column_width=True)

        with col_rma:
            st.subheader("📑 RMA")
            for img in imgs_rma:
                st.image(img, use_column_width=True)

else:
    st.info("👆 Envie ao menos a RMA para iniciar a verificação.")

# ====================== BALÃO FLUTUANTE + MODAL ======================
RAW_IMAGE_URL = "https://raw.githubusercontent.com/Brayan-GBL/Controle/main/NFXRMA.jpg"

components.html(f"""
<style>
  /* ponto “?” fixo no canto */
  #guide-balloon {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #FFA500;
    color: #fff;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    font-size: 2em;
    line-height: 50px;
    text-align: center;
    cursor: pointer;
    transition: transform 0.2s ease;
    z-index: 10000;
  }}
  #guide-balloon:hover {{
    transform: scale(1.1);
  }}

  /* backdrop do modal */
  #guide-modal {{
    display: none;
    position: fixed;
    top:0; left:0;
    width:100%; height:100%;
    background: rgba(0,0,0,0.8);
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 9999;
  }}
  #guide-modal.show {{
    display: flex;
    opacity: 1;
  }}

  /* imagem dentro do modal */
  #guide-modal img {{
    max-width: 90%;
    max-height: 90%;
    border-radius: 8px;
    transform: scale(0.8);
    transition: transform 0.3s ease;
  }}
  #guide-modal.show img {{
    transform: scale(1);
  }}
</style>

<!-- o “balão” virou um círculo laranja com “?” -->
<div id="guide-balloon" title="Clique para abrir o guia">?</div>

<!-- modal inicialmente escondido -->
<div id="guide-modal">
  <img src="{RAW_IMAGE_URL}" />
</div>

<script>
  const balloon = document.getElementById('guide-balloon');
  const modal   = document.getElementById('guide-modal');

  balloon.addEventListener('click', () => {{
    modal.classList.add('show');
  }});

  // ao clicar em qualquer lugar do backdrop, fecha
  modal.addEventListener('click', () => {{
    modal.classList.remove('show');
  }});
</script>
""", height=200, width=200)

