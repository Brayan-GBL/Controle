import pandas as pd
import streamlit as st

def processar_consolidacao(arquivo_excel):
    # Carregar o arquivo Excel
    df = pd.read_excel(arquivo_excel)
    
    # Agrupar por SKU e somar os valores relevantes
    df_sku = df.groupby("SKU").agg({
        "Qtde Solicitada (SQL)": "sum",
        "Qtde Recebida (Gráfica)": "sum",
        "Faltas": "sum",
        "Sobras": "sum",
        "Saldo Estoque": "max"  # Mantemos o maior saldo disponível para análise
    }).reset_index()
    
    # Criar coluna para indicar necessidade de baixa
    df_sku["Baixa Necessária"] = df_sku.apply(
        lambda row: "✅ Saldo OK" if row["Faltas"] == 0 else "❌ Ajuste Necessário", axis=1
    )
    
    # Comparar com o Estoque do Oracle para verificar se há saldo suficiente
    df_sku["Ajuste Estoque"] = df_sku.apply(
        lambda row: "⚠️ Precisa Ajuste" if row["Faltas"] > row["Saldo Estoque"] else "✅ Estoque OK", axis=1
    )
    
    return df_sku

# Interface Streamlit
st.title("Upload de Arquivo - Consolidação de Saldos")

uploaded_file = st.file_uploader("Faça o upload do arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    df_resultado = processar_consolidacao(uploaded_file)
    st.write("### Dados Consolidados:")
    st.dataframe(df_resultado)
    
    # Permitir download do arquivo processado
    nome_arquivo_saida = "relatorio_consolidado.xlsx"
    df_resultado.to_excel(nome_arquivo_saida, index=False)
    with open(nome_arquivo_saida, "rb") as file:
        st.download_button(
            label="Baixar Relatório Consolidado",
            data=file,
            file_name=nome_arquivo_saida,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
