import re
import unicodedata
import pandas as pd
import streamlit as st
from io import BytesIO

# --------- Normalizadores de chave ---------
def strip_accents_upper(s: str) -> str:
    if not isinstance(s, str):
        s = "" if pd.isna(s) else str(s)
    s = s.strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", s).upper()  # colapsa espaços

def nf_key(s: str) -> str:
    s = "" if s is None else str(s)
    digits = re.sub(r"\D", "", s)  # só dígitos
    if digits:
        # remove zeros à esquerda sem perder '0' puro
        digits = digits.lstrip("0") or "0"
        return digits
    # fallback: texto normalizado (caso a NF tenha letras por algum motivo)
    return strip_accents_upper(s)

def pallet_key(s: str) -> str:
    # alfa-numérico em maiúsculas, sem espaços/pontuação (ex.: "PALLET 5023" -> "PALLET5023")
    s_norm = strip_accents_upper(s)
    return re.sub(r"[^A-Z0-9]", "", s_norm)


def processar_analise(cobranca_file, triagem_file):
    # Carregar workbooks
    cobranca_xl = pd.ExcelFile(cobranca_file)
    triagem_xl  = pd.ExcelFile(triagem_file)

    # Descobrir abas
    cobranca_sheets = [s.strip() for s in cobranca_xl.sheet_names]
    triagem_sheets  = [s.strip() for s in triagem_xl.sheet_names]
    cobranca_sheet = next((s for s in cobranca_sheets if "devol" in s.lower() or "cobr" in s.lower()), None)
    triagem_sheet  = next((s for s in triagem_sheets  if "triagem" in s.lower()), None)
    if not cobranca_sheet or not triagem_sheet:
        raise ValueError(f"Abas não encontradas. Disponíveis: {cobranca_sheets} e {triagem_sheets}")

    # Ler abas
    cobranca_df = cobranca_xl.parse(cobranca_sheet)
    triagem_df  = triagem_xl.parse(triagem_sheet)

    # Padronizar cabeçalhos
    cobranca_df.columns = cobranca_df.columns.str.strip()
    triagem_df.columns  = triagem_df.columns.str.strip().str.upper()

    # Checagens mínimas
    for col in ["NF", "LOCAL", "QTD UND"]:
        if col not in cobranca_df.columns:
            raise KeyError(f"Coluna obrigatória '{col}' não encontrada na COBRANÇA.")
    for col in ["NOTA FISCAL", "QTDE FÍSICA (BOM)", "QTDE FÍSICA (RUIM)"]:
        if col not in triagem_df.columns:
            raise KeyError(f"Coluna obrigatória '{col}' não encontrada na TRIAGEM.")

    # Descobrir a coluna de pallet na TRIAGEM (seu caso é PALLET)
    triagem_local_candidates = ["PALLET", "PALETE", "PALET", "PALETTE", "LOCAL"]
    triagem_local_col = next((c for c in triagem_local_candidates if c in triagem_df.columns), None)
    if triagem_local_col is None:
        # Sem PALLET/LOCAL na triagem -> avisa e segue por NF (não recomendado, mas funcional)
        triagem_local_col = None

    # Limpeza e tipos
    cobranca_df = cobranca_df.dropna(subset=["NF", "LOCAL"])
    cobranca_df["NF"]      = cobranca_df["NF"].astype(str).str.strip()
    cobranca_df["LOCAL"]   = cobranca_df["LOCAL"].astype(str).str.strip()
    cobranca_df["QTD UND"] = pd.to_numeric(cobranca_df["QTD UND"], errors="coerce").fillna(0)

    triagem_df["NOTA FISCAL"]        = triagem_df["NOTA FISCAL"].astype(str).str.strip()
    triagem_df["QTDE FÍSICA (BOM)"]  = pd.to_numeric(triagem_df["QTDE FÍSICA (BOM)"], errors="coerce").fillna(0)
    triagem_df["QTDE FÍSICA (RUIM)"] = pd.to_numeric(triagem_df["QTDE FÍSICA (RUIM)"], errors="coerce").fillna(0)
    if triagem_local_col:
        triagem_df[triagem_local_col] = triagem_df[triagem_local_col].astype(str).str.strip()

    # Chaves normalizadas (MESMA ORDEM nas duas bases: (NF_KEY, PALLET_KEY))
    cobranca_df["NF_KEY"]     = cobranca_df["NF"].map(nf_key)
    cobranca_df["PALLET_KEY"] = cobranca_df["LOCAL"].map(pallet_key)

    triagem_df["NF_KEY"] = triagem_df["NOTA FISCAL"].map(nf_key)
    if triagem_local_col:
        triagem_df["PALLET_KEY"] = triagem_df[triagem_local_col].map(pallet_key)

    # Consolidar triagem por (NF_KEY, PALLET_KEY) se houver pallet; senão por NF_KEY
    if triagem_local_col:
        triagem_consolidado = (
            triagem_df.dropna(subset=["NF_KEY", "PALLET_KEY"])
            .groupby(["NF_KEY", "PALLET_KEY"], as_index=False)
            .agg({
                "QTDE FÍSICA (BOM)": "sum",
                "QTDE FÍSICA (RUIM)": "sum",
            })
        )
    else:
        triagem_consolidado = (
            triagem_df.dropna(subset=["NF_KEY"])
            .groupby(["NF_KEY"], as_index=False)
            .agg({
                "QTDE FÍSICA (BOM)": "sum",
                "QTDE FÍSICA (RUIM)": "sum",
            })
        )

    triagem_consolidado["CONCAT_DEV"] = (
        triagem_consolidado["QTDE FÍSICA (BOM)"] + triagem_consolidado["QTDE FÍSICA (RUIM)"]
    )

    # Merge por mesma chave (ordem idêntica!)
    if triagem_local_col:
        resultado_df = cobranca_df.merge(
            triagem_consolidado,
            on=["NF_KEY", "PALLET_KEY"],
            how="left",
            validate="m:1"  # cada linha de cobrança deve bater com no máx. 1 linha consolidada
        )
    else:
        resultado_df = cobranca_df.merge(
            triagem_consolidado,
            on=["NF_KEY"],
            how="left",
            validate="m:1"
        )
        resultado_df["_AVISO_LOCAL"] = "Triagem sem coluna de PALLET/LOCAL — somou por NF (pode misturar pallets)."

    # Cálculos finais
    resultado_df["CONCAT_DEV"] = pd.to_numeric(resultado_df["CONCAT_DEV"], errors="coerce").fillna(0)
    resultado_df["DIFERENÇA"]  = resultado_df["CONCAT_DEV"] - resultado_df["QTD UND"]

    def classificar_diferenca(row):
        bom = row.get("QTDE FÍSICA (BOM)", 0) or 0
        ruim = row.get("QTDE FÍSICA (RUIM)", 0) or 0
        concat_dev = row.get("CONCAT_DEV", 0) or 0
        qtd_und = row.get("QTD UND", 0) or 0
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

    # Financeiro
    valor_unitario = 2.76
    resultado_df["Valor Unitário"] = valor_unitario
    resultado_df["Total Nota"]     = resultado_df["QTD UND"] * valor_unitario
    resultado_df["Total Cobrança"] = resultado_df["DIFERENÇA"] * valor_unitario

    # Saída limpa
    cols_saida = [
        "NF", "CLIENTE", "QTD UND", "LOCAL",
        "CONCAT_DEV", "DIFERENÇA", "Observação PSD",
        "Valor Unitário", "Total Nota", "Total Cobrança"
    ]
    cols_existentes = [c for c in cols_saida if c in resultado_df.columns]

    # Extras p/ diagnóstico (úteis no Streamlit se quiser inspecionar)
    diag_cols = ["NF", "LOCAL", "NF_KEY", "PALLET_KEY"]
    for c in diag_cols:
        if c not in resultado_df.columns:
            diag_cols.remove(c)

    return resultado_df[cols_existentes + diag_cols]

# -------------------- STREAMLIT --------------------
st.title("FATURA POSIGRAF")

cobranca_file = st.file_uploader("Upload do arquivo COBRANÇA POSIGRAF", type=["xlsx"])
triagem_file  = st.file_uploader("Upload do arquivo CONFERÊNCIA TRIAGEM", type=["xlsx"])

if cobranca_file and triagem_file:
    try:
        df_resultado = processar_analise(cobranca_file, triagem_file)

        st.write("### Resultados da Análise:")
        st.dataframe(df_resultado, use_container_width=True)

        # Diagnóstico opcional: ver pares sem match (CONCAT_DEV = 0 mas QTD UND > 0)
        with st.expander("Diagnóstico de chaves (opcional)"):
            sem_match = df_resultado[(df_resultado["QTD UND"] > 0) & (df_resultado["CONCAT_DEV"] == 0)]
            st.write(f"Pares NF/LOCAL sem correspondência na triagem: {len(sem_match)}")
            st.dataframe(sem_match[["NF","LOCAL","NF_KEY","PALLET_KEY"]] if not sem_match.empty else sem_match)

        # Download
        nome_saida = "analise_cobranca_triagem.xlsx"
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_resultado.to_excel(writer, index=False, sheet_name="Resultado")
        st.download_button(
            label="Baixar Relatório Consolidado",
            data=buffer.getvalue(),
            file_name=nome_saida,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except (ValueError, KeyError, pd.errors.MergeError) as e:
        st.error(f"Erro: {str(e)}. Verifique nomes de colunas e conteúdo (NF/LOCAL/PALLET).")
