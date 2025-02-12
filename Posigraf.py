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
    
    # Limpar nomes das colunas para remover espaços extras
    sim_df.columns = sim_df.columns.str.strip()
    nao_df.columns = nao_df.columns.str.strip()
    
    # Renomear colunas para padronizar
    if "NU_PEDIDO_VENDA" in sim_df.columns:
        sim_df = sim_df.rename(columns={"NU_PEDIDO_VENDA": "PEDIDO"})
    else:
        raise KeyError("Coluna 'NU_PEDIDO_VENDA' não encontrada no relatório SIM.")
    
    if "NUMERO_PEDIDO" in nao_df.columns:
        nao_df = nao_df.rename(columns={"NUMERO_PEDIDO": "PEDIDO"})
    else:
        raise KeyError("Coluna 'NUMERO_PEDIDO' não encontrada no relatório NÃO.")
    
    # Extrair apenas a coluna de pedidos
    pedidos = pedidos_df.iloc[:, 0].dropna().tolist()
    
    resultados = []
    
    for pedido in pedidos:
        resultado = {"Pedido": pedido}
        
        # Procurar no relatório SIM
        sim_match = sim_df[sim_df["PEDIDO"] == pedido]
        if not sim_match.empty:
            tipo_erro = str(sim_match.iloc[0].get("TIPO_ERRO", "N/A"))
            mensagem = sim_match.iloc[0].get("MENSAGEM", "")
            
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
        
        # Verificar no relatório NÃO para status finalizado
        nao_match = nao_df[nao_df["PEDIDO"] == pedido]
        if not nao_match.empty:
            data_envio = nao_match.iloc[0].get("DATA_ENVIO_NF_OPERADOR", None)
            status_envio = nao_match.iloc[0].get("STATUS_ENVIO_NF_OPERADOR", None)
            if pd.isna(data_envio) or pd.isna(status_envio):
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
    try:
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
    except KeyError as e:
        st.error(f"Erro: {str(e)}. Verifique se os arquivos têm os nomes de colunas corretos.")
