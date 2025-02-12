import pandas as pd
import streamlit as st
import re

def extrair_dados_po(mensagem):
    """Extrai Item, Preço na NF e Quantidade da mensagem PO."""
    item = re.search(r'Item\s:(\d+\.\d+)', mensagem)
    preco = re.search(r'Preço na NF\s:(\d+,\d+)', mensagem)
    qtd = re.search(r'Qtd:(\d+)', mensagem)
    
    return (
        item.group(1) if item else "N/A",
        preco.group(1).replace(',', '.') if preco else "N/A",
        qtd.group(1) if qtd else "N/A"
    )

def processar_pedidos(pedidos_file, sim_file, nao_file):
    # Carregar os arquivos
    pedidos_df = pd.read_excel(pedidos_file)
    sim_df = pd.read_excel(sim_file)
    nao_df = pd.read_excel(nao_file)
    
    # Renomear colunas para padronizar
    sim_df = sim_df.rename(columns={"NU_PEDIDO_VENDA": "PEDIDO"})
    nao_df = nao_df.rename(columns={"NUMERO_PEDIDO": "PEDIDO"})
    
    # Extrair apenas a coluna de pedidos
    pedidos = pedidos_df.iloc[:, 0].dropna().tolist()
    
    resultados = []
    
    for pedido in pedidos:
        resultado = {"Pedido": pedido}
        
        # Procurar no relatório SIM
        sim_match = sim_df[sim_df["PEDIDO"] == pedido]
        if not sim_match.empty:
            status = sim_match.iloc[0]["STATUS_SEFAZ"]
            tipo_erro = sim_match.iloc[0]["TIPO_ERRO"]
            mensagem = sim_match.iloc[0]["MENSAGEM"]
            
            if tipo_erro == "NA":
                resultado["Resultado"] = mensagem
            elif tipo_erro == "PO":
                item, preco, qtd = extrair_dados_po(mensagem)
                resultado.update({"Item": item, "Preço NF": preco, "Quantidade": qtd})
            elif tipo_erro == "Concurrent":
                resultado["Resultado"] = mensagem
            elif "Ordem de venda" in tipo_erro:
                resultado["Resultado"] = "Necessário mandar para devolução"
            else:
                resultado["Resultado"] = "Sem correspondência específica"
        
        # Se o status for "Finalizado", verificar no relatório NÃO
        if status == "Finalizado":
            nao_match = nao_df[nao_df["PEDIDO"] == pedido]
            if not nao_match.empty:
                data = nao_match.iloc[0]["TRX_DATE"]
                sucesso = nao_match.iloc[0]["STATUS_FLOW"]
                if pd.isna(data) or pd.isna(sucesso):
                    resultado["Resultado"] = "Necessário verificar"
                else:
                    resultado["Resultado"] = "Sucesso"
        
        resultados.append(resultado)
    
    return pd.DataFrame(resultados)

# Interface no Streamlit
st.title("Verificação de Pedidos Posigraf")

pedidos_file = st.file_uploader("Upload do arquivo PEDIDOS POSIGRAF", type=["xlsx"])
sim_file = st.file_uploader("Upload do arquivo Relatório SIM", type=["xlsx"])
nao_file = st.file_uploader("Upload do arquivo Relatório NÃO", type=["xlsx"])

if pedidos_file and sim_file and nao_file:
    df_resultado = processar_pedidos(pedidos_file, sim_file, nao_file)
    st.write("### Resultados da Análise:")
    st.dataframe(df_resultado)
    
    # Baixar relatório consolidado
    nome_saida = "relatorio_pedidos.xlsx"
    df_resultado.to_excel(nome_saida, index=False)
    with open(nome_saida, "rb") as file:
        st.download_button(
            label="Baixar Relatório Consolidado",
            data=file,
            file_name=nome_saida,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
