import re
import pandas as pd
import streamlit as st

def processar_analise(cobranca_file, triagem_file):
    # Carregar todas as abas do arquivo
    cobranca_xl = pd.ExcelFile(cobranca_file)
    triagem_xl = pd.ExcelFile(triagem_file)

    # Listar todas as abas disponíveis
    cobranca_sheets = [s.strip() for s in cobranca_xl.sheet_names]
    triagem_sheets = [s.strip() for s in triagem_xl.sheet_names]

    # Tentar encontrar a aba correta ignorando espaços e maiúsculas
    cobranca_sheet = next((s for s in cobranca_sheets if "devol" in s.lower()), None)
    triagem_sheet = next((s for s in triagem_sheets if "triagem" in s.lower()), None)
    if not cobranca_sheet or not triagem_sheet:
        raise ValueError(f"Abas não encontradas. Disponíveis: {cobranca_sheets} e {triagem_sheets}")

    # Carregar os dados das abas corretas
    cobranca_df = cobranca_xl.parse(cobranca_sheet)
    triagem_df = triagem_xl.parse(triagem_sheet)

    # Limpar nomes das colunas e remover espaços extras
    cobranca_df.columns = cobranca_df.columns.str.strip()
    triagem_df.columns = triagem_df.columns.str.strip().str.upper()

    # Filtrar apenas linhas com NF e LOCAL preenchidos
    cobranca_df = cobranca_df.dropna(subset=["NF", "LOCAL"])

    # --------------------
    # NOVO: criar CHAVE composta nas duas bases
    #     - triagem: usar FORMULA (PALLET+NOTA FISCAL)
    #     - cobrança: LOCAL+NF
    #     - normalizando para manter só dígitos (evita 'PALLET 5023', '20.0' etc.)
    # --------------------
    def only_digits(x):
        return re.sub(r"\D", "", str(x).strip())  # só dígitos

    if "FORMULA" in triagem_df.columns:
        triagem_df["CHAVE"] = triagem_df["FORMULA"].apply(only_digits)
        cobranca_df["CHAVE"] = cobranca_df["LOCAL"].apply(only_digits) + cobranca_df["NF"].apply(only_digits)
        usa_chave_composta = True
    else:
        # fallback: mantém seu comportamento original (junta só por NF)
        usa_chave_composta = False

    # Criar chave de concatenação na base Cobrança (sua lógica)
    cobranca_df["CONCAT_POSIGRAF"] = cobranca_df["NF"].astype(str) + cobranca_df["QTD UND"].astype(str)

    # Consolidar quantidades físicas (BOA + RUIM) da triagem
    if usa_chave_composta:
        triagem_consolidado = (
            triagem_df.groupby("CHAVE")
            .agg({"QTDE FÍSICA (BOM)": "sum", "QTDE FÍSICA (RUIM)": "sum"})
            .reset_index()
        )
    else:
        triagem_consolidado = (
            triagem_df.groupby("NOTA FISCAL")
            .agg({"QTDE FÍSICA (BOM)": "sum", "QTDE FÍSICA (RUIM)": "sum"})
            .reset_index()
        )

    triagem_consolidado["CONCAT_DEV"] = (
        triagem_consolidado["QTDE FÍSICA (BOM)"] + triagem_consolidado["QTDE FÍSICA (RUIM)"]
    )

    # Mesclar os dados
    if usa_chave_composta:
        resultado_df = cobranca_df.merge(
            triagem_consolidado, left_on="CHAVE", right_on="CHAVE", how="left"
        )
    else:
        resultado_df = cobranca_df.merge(
            triagem_consolidado, left_on="NF", right_on="NOTA FISCAL", how="left"
        )

    # Calcular diferença entre quantidades
    resultado_df["CONCAT_DEV"] = pd.to_numeric(resultado_df["CONCAT_DEV"], errors="coerce").fillna(0)
    resultado_df["DIFERENÇA"] = resultado_df["CONCAT_DEV"] - resultado_df["QTD UND"]

    # Criar análise de status (sua lógica intacta)
    def classificar_diferenca(row):
        if row["CONCAT_DEV"] > row["QTD UND"] and row["CONCAT_DEV"] == row["QTDE FÍSICA (BOM)"] + row["QTDE FÍSICA (RUIM)"]:
            return "Informação incorreta - Devemos pagar mais"
        elif row["DIFERENÇA"] > 0 and row["QTDE FÍSICA (BOM)"] + row["QTDE FÍSICA (RUIM)"] < row["QTD UND"]:
            return "Cobrança indevida - Quantidade menor recebida"
        elif row["DIFERENÇA"] > 0:
            return "Sobra cliente"
        elif row["DIFERENÇA"] < 0:
            return "Digitou errado" if row["CONCAT_DEV"] > 0 else "Não recebemos nada"
        else:
            return "Correto"

    resultado_df["Observação PSD"] = resultado_df.apply(classificar_diferenca, axis=1)

    # Calcular valores financeiros
    valor_unitario = 2.76
    resultado_df["Valor Unitário"] = valor_unitario
    resultado_df["Total Nota"] = resultado_df["QTD UND"] * valor_unitario
    resultado_df["Total Cobrança"] = resultado_df["DIFERENÇA"] * valor_unitario

    return resultado_df[[
        "NF", "CLIENTE", "QTD UND", "LOCAL",
        "CONCAT_DEV", "DIFERENÇA", "Observação PSD",
        "Valor Unitário", "Total Nota", "Total Cobrança"
    ]]

# Interface no Streamlit
st.title("FATURA POSIGRAF")
cobranca_file = st.file_uploader("Upload do arquivo COBRANÇA POSIGRAF", type=["xlsx"])
triagem_file = st.file_uploader("Upload do arquivo CONFERÊNCIA TRIAGEM", type=["xlsx"])

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
