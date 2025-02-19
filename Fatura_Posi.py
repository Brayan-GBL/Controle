import pandas as pd
import streamlit as st

def processar_analise(cobranca_file, triagem_file):
    # Carregar todas as abas do arquivo
    cobranca_xl = pd.ExcelFile(cobranca_file)
    triagem_xl = pd.ExcelFile(triagem_file)
    
    # Listar todas as abas disponíveis
    cobranca_sheets = [s.strip() for s in cobranca_xl.sheet_names]
    triagem_sheets = [s.strip() for s in triagem_xl.sheet_names]
    
    # Exibir abas disponíveis para depuração
    print(f"Abas no arquivo de Cobrança: {cobranca_sheets}")
    print(f"Abas no arquivo de Triagem: {triagem_sheets}")
    
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
    
    # Exibir colunas disponíveis para depuração
    print(f"Colunas na aba TRIAGEM: {list(triagem_df.columns)}")
    
    # Verificar se a coluna 'NOTA FISCAL' existe na aba TRIAGEM
    if "NOTA FISCAL" not in triagem_df.columns:
        raise KeyError(f"Coluna 'NOTA FISCAL' não encontrada na aba TRIAGEM. Colunas disponíveis: {list(triagem_df.columns)}")
    
    # Criar chave de concatenação na base Cobrança
    cobranca_df["CONCAT_POSIGRAF"] = cobranca_df["NF"].astype(str) + cobranca_df["QTD UND"].astype(str)
    
    # Consolidar quantidades físicas (BOA + RUIM) da triagem
    triagem_consolidado = triagem_df.groupby("NOTA FISCAL").agg({"QTDE FÍSICA (BOM)": "sum", "QTDE FÍSICA (RUIM)": "sum"}).reset_index()
    triagem_consolidado["CONCAT_DEV"] = triagem_consolidado["QTDE FÍSICA (BOM)"] + triagem_consolidado["QTDE FÍSICA (RUIM)"]
    
    # Mesclar os dados
    resultado_df = cobranca_df.merge(triagem_consolidado, left_on="NF", right_on="NOTA FISCAL", how="left")
    
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
    except (ValueError, KeyError) as e:
        st.error(f"Erro: {str(e)}. Verifique se os arquivos contêm as abas e colunas corretas.")
