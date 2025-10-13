import pandas as pd
import streamlit as st
import unicodedata

def _norm(s: str) -> str:
    """normaliza nomes de colunas: maiúsculas, sem acento e sem espaços extras"""
    if not isinstance(s, str):
        return s
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.strip().upper()

def _find_col(df: pd.DataFrame, candidates):
    """encontra a primeira coluna do DF que bate (normalizada) com a lista de candidatos"""
    norm_map = { _norm(c): c for c in df.columns }
    for cand in candidates:
        if _norm(cand) in norm_map:
            return norm_map[_norm(cand)]
    return None

def processar_analise(cobranca_file, triagem_file):
    # Carregar todas as abas do arquivo
    cobranca_xl = pd.ExcelFile(cobranca_file)
    triagem_xl = pd.ExcelFile(triagem_file)

    # Listar abas
    cobranca_sheets = [s.strip() for s in cobranca_xl.sheet_names]
    triagem_sheets  = [s.strip() for s in triagem_xl.sheet_names]

    # Encontrar abas por nome aproximado
    cobranca_sheet = next((s for s in cobranca_sheets if "devol" in s.lower() or "cobr" in s.lower()), None)
    triagem_sheet  = next((s for s in triagem_sheets  if "triagem" in s.lower()), None)
    if not cobranca_sheet or not triagem_sheet:
        raise ValueError(f"Abas não encontradas. Disponíveis: {cobranca_sheets} e {triagem_sheets}")

    # Ler abas
    cobranca_df = cobranca_xl.parse(cobranca_sheet)
    triagem_df  = triagem_xl.parse(triagem_sheet)

    # Normalizar nomes de colunas
    cobranca_df.columns = [c.strip() for c in cobranca_df.columns]
    triagem_df.columns  = [c.strip() for c in triagem_df.columns]

    # Identificar colunas necessárias (tolerante a nomes)
    col_nf_cob   = _find_col(cobranca_df, ["NF", "NOTA FISCAL", "NFE", "NF_PSD"])
    col_local_cb = _find_col(cobranca_df, ["LOCAL", "PALLET", "PALETE", "PALETTE"])
    col_qtd_und  = _find_col(cobranca_df, ["QTD UND", "QTD_UND", "QTD", "QUANTIDADE"])

    col_nf_tri   = _find_col(triagem_df, ["NOTA FISCAL", "NF", "NFE"])
    col_bom      = _find_col(triagem_df, ["QTDE FÍSICA (BOM)", "QTDE FISICA (BOM)", "QTD FISICA BOM", "QTD BOM", "BOM"])
    col_ruim     = _find_col(triagem_df, ["QTDE FÍSICA (RUIM)", "QTDE FISICA (RUIM)", "QTD FISICA RUIM", "QTD RUIM", "RUIM"])
    col_local_tr = _find_col(triagem_df, ["LOCAL", "PALLET", "PALETE", "PALETTE"])

    obrig_cob = [("NF", col_nf_cob), ("LOCAL", col_local_cb), ("QTD UND", col_qtd_und)]
    obrig_tri = [("NOTA FISCAL", col_nf_tri), ("QTDE FÍSICA (BOM)", col_bom), ("QTDE FÍSICA (RUIM)", col_ruim)]
    faltando = [nome for nome, col in obrig_cob + obrig_tri if col is None]
    if faltando:
        raise KeyError(f"Colunas obrigatórias ausentes: {', '.join(faltando)}")

    # Filtro de linhas válidas
    cobranca_df = cobranca_df.dropna(subset=[col_nf_cob, col_local_cb])

    # Tipos
    cobranca_df[col_nf_cob]   = cobranca_df[col_nf_cob].astype(str).str.strip()
    cobranca_df[col_local_cb] = cobranca_df[col_local_cb].astype(str).str.strip()
    cobranca_df[col_qtd_und]  = pd.to_numeric(cobranca_df[col_qtd_und], errors="coerce").fillna(0)

    triagem_df[col_nf_tri] = triagem_df[col_nf_tri].astype(str).str.strip()
    triagem_df[col_bom]    = pd.to_numeric(triagem_df[col_bom], errors="coerce").fillna(0)
    triagem_df[col_ruim]   = pd.to_numeric(triagem_df[col_ruim], errors="coerce").fillna(0)

    # Se a triagem NÃO tiver coluna de LOCAL/PALLET, caímos no agrupamento só por NF (com aviso)
    if col_local_tr is None:
        # Agrupa por NF (sem LOCAL) – comportamento antigo
        triagem_consolidado = (
            triagem_df.groupby(col_nf_tri, as_index=False)
            .agg({col_bom: "sum", col_ruim: "sum"})
        )
        triagem_consolidado["CONCAT_DEV"] = triagem_consolidado[col_bom] + triagem_consolidado[col_ruim]

        # Merge apenas por NF (pode misturar pallets iguais de clientes diferentes!)
        resultado_df = cobranca_df.merge(
            triagem_consolidado,
            left_on=col_nf_cob,
            right_on=col_nf_tri,
            how="left"
        )
        resultado_df["_AVISO_LOCAL"] = "Triagem sem coluna de LOCAL/PALLET — somou por NF."
    else:
        # Normaliza LOCAL da triagem também
        triagem_df[col_local_tr] = triagem_df[col_local_tr].astype(str).str.strip()

        # Agrupa por NOTA FISCAL **e** LOCAL (pallet) — CORREÇÃO PEDIDA
        triagem_consolidado = (
            triagem_df.groupby([col_nf_tri, col_local_tr], as_index=False)
            .agg({col_bom: "sum", col_ruim: "sum"})
        )
        triagem_consolidado["CONCAT_DEV"] = triagem_consolidado[col_bom] + triagem_consolidado[col_ruim]

        # Merge por NF + LOCAL (PONTO-CHAVE)
        resultado_df = cobranca_df.merge(
            triagem_consolidado,
            left_on=[col_nf_cob, col_local_cb],
            right_on=[col_nf_tri, col_local_tr],
            how="left"
        )

    # Diferença e classificação
    resultado_df["DIFERENÇA"] = (resultado_df["CONCAT_DEV"].fillna(0) - resultado_df[col_qtd_und].fillna(0))

    def classificar_diferenca(row):
        bom = row.get(col_bom, 0) or 0
        ruim = row.get(col_ruim, 0) or 0
        concat_dev = row.get("CONCAT_DEV", 0) or 0
        qtd_und = row.get(col_qtd_und, 0) or 0

        if concat_dev > qtd_und and concat_dev == bom + ruim:
            return "Informação incorreta - Devemos pagar mais"
        elif (concat_dev - qtd_und) > 0 and (bom + ruim) < qtd_und:
            return "Cobrança indevida - Quantidade menor recebida"
        elif (concat_dev - qtd_und) > 0:
            return "Sobra cliente"
        elif (concat_dev - qtd_und) < 0:
            return "Digitou errado" if concat_dev > 0 else "Não recebemos nada"
        else:
            return "Correto"

    resultado_df["Observação PSD"] = resultado_df.apply(classificar_diferenca, axis=1)

    # Valores financeiros
    valor_unitario = 2,8863
    resultado_df["Valor Unitário"]   = valor_unitario
    resultado_df["Total Nota"]       = resultado_df[col_qtd_und].fillna(0) * valor_unitario
    resultado_df["Total Cobrança"]   = resultado_df["DIFERENÇA"].fillna(0) * valor_unitario

    # Seleção/renomeação amigável
    col_cliente = _find_col(cobranca_df, ["CLIENTE", "NOME CLIENTE", "CLIENTE_NOME"])
    cols_saida = [
        col_nf_cob, (col_cliente or "CLIENTE"), col_qtd_und, col_local_cb,
        "CONCAT_DEV", "DIFERENÇA", "Observação PSD", "Valor Unitário", "Total Nota", "Total Cobrança"
    ]
    # Garante que todas existem
    cols_saida = [c for c in cols_saida if c in resultado_df.columns]

    # Renomeia para os rótulos pedidos
    rename_map = {
        col_nf_cob: "NF",
        col_qtd_und: "QTD UND",
        col_local_cb: "LOCAL",
    }
    if col_cliente:
        rename_map[col_cliente] = "CLIENTE"

    saida = resultado_df[cols_saida].rename(columns=rename_map)

    return saida


# -------------------- STREAMLIT --------------------
st.title("FATURA POSIGRAF")

cobranca_file = st.file_uploader("Upload do arquivo COBRANÇA POSIGRAF", type=["xlsx"])
triagem_file  = st.file_uploader("Upload do arquivo CONFERÊNCIA TRIAGEM", type=["xlsx"])

if cobranca_file and triagem_file:
    try:
        df_resultado = processar_analise(cobranca_file, triagem_file)
        st.write("### Resultados da Análise:")
        st.dataframe(df_resultado)

        # Baixar relatório consolidado
        nome_saida = "analise_cobranca_triagem.xlsx"
        df_resultado.to_excel(nome_saida, index=False)
        with open(nome_saida, "rb") as file:
            st.download_button(
                label="Baixar Relatório Consolidado",
                data=file,
                file_name=nome_saida,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except (ValueError, KeyError) as e:
        st.error(f"Erro: {str(e)}. Verifique se os arquivos contêm as abas e colunas corretas.")
