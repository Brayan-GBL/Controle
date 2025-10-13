import pandas as pd
import streamlit as st
from io import BytesIO

def processar_analise(cobranca_file, triagem_file):
    # Carregar todas as abas do arquivo
    cobranca_xl = pd.ExcelFile(cobranca_file)
    triagem_xl = pd.ExcelFile(triagem_file)

    # Listar todas as abas disponíveis
    cobranca_sheets = [s.strip() for s in cobranca_xl.sheet_names]
    triagem_sheets  = [s.strip() for s in triagem_xl.sheet_names]

    # Tentar encontrar a aba correta ignorando espaços e maiúsculas
    cobranca_sheet = next((s for s in cobranca_sheets if "devol" in s.lower() or "cobr" in s.lower()), None)
    triagem_sheet  = next((s for s in triagem_sheets  if "triagem" in s.lower()), None)
    if not cobranca_sheet or not triagem_sheet:
        raise ValueError(f"Abas não encontradas. Disponíveis: {cobranca_sheets} e {triagem_sheets}")

    # Carregar os dados das abas corretas
    cobranca_df = cobranca_xl.parse(cobranca_sheet)
    triagem_df  = triagem_xl.parse(triagem_sheet)

    # Limpar nomes das colunas e remover espaços extras
    cobranca_df.columns = cobranca_df.columns.str.strip()
    triagem_df.columns  = triagem_df.columns.str.strip().str.upper()

    # Verificações de colunas obrigatórias
    obrig_cobranca = ["NF", "LOCAL", "QTD UND"]
    obrig_triagem_min = ["NOTA FISCAL", "QTDE FÍSICA (BOM)", "QTDE FÍSICA (RUIM)"]
    for col in obrig_cobranca:
        if col not in cobranca_df.columns:
            raise KeyError(f"Coluna obrigatória '{col}' não encontrada na planilha de COBRANÇA.")
    for col in obrig_triagem_min:
        if col not in triagem_df.columns:
            raise KeyError(f"Coluna obrigatória '{col}' não encontrada na planilha de TRIAGEM.")

    # Detectar a coluna de pallet/“local” na TRIAGEM (PALLET é o caso real)
    triagem_local_candidates = ["PALLET", "PALETE", "PALET", "PALETTE", "LOCAL"]
    triagem_local_col = next((c for c in triagem_local_candidates if c in triagem_df.columns), None)

    # Filtrar apenas linhas com NF e LOCAL preenchidos na cobrança
    cobranca_df = cobranca_df.dropna(subset=["NF", "LOCAL"])

    # Tipagens e normalizações básicas
    cobranca_df["NF"]       = cobranca_df["NF"].astype(str).str.strip()
    cobranca_df["LOCAL"]    = cobranca_df["LOCAL"].astype(str).str.strip()
    cobranca_df["QTD UND"]  = pd.to_numeric(cobranca_df["QTD UND"], errors="coerce").fillna(0)

    triagem_df["NOTA FISCAL"]        = triagem_df["NOTA FISCAL"].astype(str).str.strip()
    triagem_df["QTDE FÍSICA (BOM)"]  = pd.to_numeric(triagem_df["QTDE FÍSICA (BOM)"], errors="coerce").fillna(0)
    triagem_df["QTDE FÍSICA (RUIM)"] = pd.to_numeric(triagem_df["QTDE FÍSICA (RUIM)"], errors="coerce").fillna(0)

    # Criar chave de concatenação na base Cobrança (mantido)
    cobranca_df["CONCAT_POSIGRAF"] = cobranca_df["NF"].astype(str) + cobranca_df["QTD UND"].astype(str)

    # --- AJUSTE PRINCIPAL ---
    if triagem_local_col is not None:
        # Ex.: triagem_local_col = "PALLET" (seu caso)
        triagem_df[triagem_local_col] = triagem_df[triagem_local_col].astype(str).str.strip()

        triagem_consolidado = (
            triagem_df
            .groupby(["NOTA FISCAL", triagem_local_col], as_index=False)
            .agg({
                "QTDE FÍSICA (BOM)": "sum",
                "QTDE FÍSICA (RUIM)": "sum"
            })
        )
        triagem_consolidado["CONCAT_DEV"] = (
            triagem_consolidado["QTDE FÍSICA (BOM)"] + triagem_consolidado["QTDE FÍSICA (RUIM)"]
        )

        # MERGE por NF + LOCAL(cobrança)  ~  NF + PALLET(triagem)
        resultado_df = cobranca_df.merge(
            triagem_consolidado,
            left_on=["NF", "LOCAL"],
            right_on=["NOTA FISCAL", triagem_local_col],
            how="left"
        )
    else:
        # Fallback: consolidar só por NF (avisa possível mistura de pallets)
        triagem_consolidado = (
            triagem_df
            .groupby("NOTA FISCAL", as_index=False)
            .agg({
                "QTDE FÍSICA (BOM)": "sum",
                "QTDE FÍSICA (RUIM)": "sum"
            })
        )
        triagem_consolidado["CONCAT_DEV"] = (
            triagem_consolidado["QTDE FÍSICA (BOM)"] + triagem_consolidado["QTDE FÍSICA (RUIM)"]
        )

        resultado_df = cobranca_df.merge(
            triagem_consolidado,
            left_on="NF",
            right_on="NOTA FISCAL",
            how="left"
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

    # Valores financeiros
    valor_unitario = 2.76
    resultado_df["Valor Unitário"]   = valor_unitario
    resultado_df["Total Nota"]       = resultado_df["QTD UND"] * valor_unitario
    resultado_df["Total Cobrança"]   = resultado_df["DIFERENÇA"] * valor_unitario

    # Layout de saída
    cols_saida = [
        "NF", "CLIENTE", "QTD UND", "LOCAL",
        "CONCAT_DEV", "DIFERENÇA", "Observação PSD",
        "Valor Unitário", "Total Nota", "Total Cobrança"
    ]
    cols_existentes = [c for c in cols_saida if c in resultado_df.columns]
    return resultado_df[cols_existentes]

# -------------------- STREAMLIT --------------------
st.title("FATURA POSIGRAF")

cobranca_file = st.file_uploader("Upload do arquivo COBRANÇA POSIGRAF", type=["xlsx"])
triagem_file  = st.file_uploader("Upload do arquivo CONFERÊNCIA TRIAGEM", type=["xlsx"])

if cobranca_file and triagem_file:
    try:
        df_resultado = processar_analise(cobranca_file, triagem_file)
        st.write("### Resultados da Análise:")
        st.dataframe(df_resultado, use_container_width=True)

        # Baixar relatório consolidado (BytesIO evita gravar em disco)
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

    except (ValueError, KeyError) as e:
        st.error(f"Erro: {str(e)}. Verifique se os arquivos contêm as abas e colunas corretas.")
