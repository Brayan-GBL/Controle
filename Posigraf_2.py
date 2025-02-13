import pandas as pd
import streamlit as st

def processar_comparacao(pedidos_file, estoque_file):
    # Carregar os arquivos
    pedidos_df = pd.read_excel(pedidos_file)
    estoque_df = pd.read_excel(estoque_file)
    
    # Limpar nomes das colunas para remover espaços extras
    pedidos_df.columns = pedidos_df.columns.str.strip()
    estoque_df.columns = estoque_df.columns.str.strip()
    
    # Consolidar quantidades por PEG/SKU
    pedidos_consolidado = pedidos_df.groupby("Item").agg({"Quantidade": "sum", "Preço NF": "first"}).reset_index()
    
    # Renomear colunas para padronizar
    estoque_df = estoque_df.rename(columns={"PEG": "Item", "Estoque Fisico": "Estoque"})
    
    # Mesclar os dados
    resultado_df = pd.merge(pedidos_consolidado, estoque_df[["Item", "Estoque"]], on="Item", how="left")
    
    return resultado_df

# Interface no Streamlit
st.title("Comparação de Estoque")

pedidos_file = st.file_uploader("Upload do arquivo RELATORIO_PEDIDOS", type=["xlsx"])
estoque_file = st.file_uploader("Upload do arquivo ESTOQUE", type=["xlsx"])

if pedidos_file and estoque_file:
    try:
        df_resultado = processar_comparacao(pedidos_file, estoque_file)
        st.write("### Resultados da Comparação:")
        st.dataframe(df_resultado)

        # Baixar relatório consolidado
        nome_saida = "comparacao_estoque.xlsx"
        df_resultado.to_excel(nome_saida, index=False)
        with open(nome_saida, "rb") as file:
            st.download_button(
                label="Baixar Relatório Consolidado",
                data=file,
                file_name=nome_saida,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except KeyError as e:
        st.error(f"Erro: {str(e)}. Verifique se os arquivos têm os nomes de colunas corretos.")
