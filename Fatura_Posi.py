import pandas as pd
import streamlit as st

def processar_analise(cobranca_file, triagem_file):
    # Carregar os arquivos com os nomes exatos das abas
    try:
        cobranca_df = pd.read_excel(cobranca_file, sheet_name="Devoluções")
        triagem_df = pd.read_excel(triagem_file, sheet_name="TRIAGEM")
    except ValueError as e:
        raise ValueError("Erro ao carregar os arquivos. Verifique se as abas 'Devoluções' e 'TRIAGEM' existem.")
    
    # Limpar nomes das colunas para remover espaços extras
    cobranca_df.columns = cobranca_df.columns.str.strip()
    triagem_df.columns = triagem_df.columns.str.strip()
    
    # Criar a chave de concatenação na base Cobrança
    cobranca_df["CONCAT_POSIGRAF"] = cobranca_df["NF"].astype(str) + cobranca_df["QTD UND"].astype(str)
    
    # Consolidar quantidades físicas (BOA + RUIM) da triagem
    triagem_consolidado = triagem_df.groupby("Nota Fiscal").agg({"QTDE FÍSICA (BOM)": "sum", "QTDE FÍSICA (RUIM)": "sum"}).reset_index()
    triagem_consolidado["CONCAT_DEV"] = triagem_consolidado["QTDE FÍSICA (BOM)"] + triagem_consolidado["QTDE FÍSICA (RUIM)"]
    
    # Mesclar os dados
    resultado_df = cobranca_df.merge(triagem_consolidado, left_on="NF", right_on="Nota Fiscal", how="left")
    
    # Calcular diferença entre quantidades
    resultado_df["DIFERENÇA"] = resultado_df["CONCAT_DEV"] - resultado_df["QTD UND"]
    
    # Validar se os valores batem
    resultado_df["VALIDAÇÃO"] = resultado_df["CONCAT_DEV"] == resultado_df["QTD UND"]
    
    return resultado_df

# Interface no Streamlit
st.title("Análise de Cobrança e Triagem")

cobranca_file = st.file_uploader("Upload do arquivo COBRANÇA LOGÍSTICA", type=["xlsx"])
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
    except ValueError as e:
        st.error(f"Erro: {str(e)}. Verifique se os arquivos contêm as abas corretas.")
