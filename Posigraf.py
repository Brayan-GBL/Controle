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

def processar_pedidos(pedidos_file, sim_file, nao_file, erro_file):
    # Carregar os arquivos
    pedidos_df = pd.read_excel(pedidos_file)
    sim_df = pd.read_excel(sim_file)
    nao_df = pd.read_excel(nao_file)
    erro_df = pd.read_excel(erro_file)
    
    # Limpar nomes das colunas para remover espaços extras
    sim_df.columns = sim_df.columns.str.strip()
    nao_df.columns = nao_df.columns.str.strip()
    erro_df.columns = erro_df.columns.str.strip()
    
    # Renomear colunas para padronizar
    if "NU_PEDIDO_VENDA" in sim_df.columns:
        sim_df = sim_df.rename(columns={"NU_PEDIDO_VENDA": "PEDIDO"})
    else:
        raise KeyError("Coluna 'NU_PEDIDO_VENDA' não encontrada no relatório SIM.")
    
    if "NUMERO_PEDIDO" in nao_df.columns:
        nao_df = nao_df.rename(columns={"NUMERO_PEDIDO": "PEDIDO"})
    else:
        raise KeyError("Coluna 'NUMERO_PEDIDO' não encontrada no relatório NÃO.")
    
    if "NF_PEDIDO" in erro_df.columns:
        erro_df = erro_df.rename(columns={"NF_PEDIDO": "PEDIDO"})
    else:
        raise KeyError("Coluna 'NF_PEDIDO' não encontrada no relatório ERRO NOTAS ATUALIZADAS.")
    
    # Extrair apenas a coluna de pedidos
    pedidos = pedidos_df.iloc[:, 0].dropna().tolist()
    resultados = []
    
    for pedido in pedidos:
        resultado = {"Pedido": pedido}
        
        # Procurar no relatório SIM
        sim_match = sim_df[sim_df["PEDIDO"] == pedido]
        if not sim_match.empty:
            tipo_erro = str(sim_match.iloc[0].get("TIPO_ERRO", "")).strip()
            status_sefaz = str(sim_match.iloc[0].get("STATUS_SEFAZ", "")).strip()
            mensagem = sim_match.iloc[0].get("MENSAGEM", "")
            
            if tipo_erro and tipo_erro != "-" and tipo_erro.lower() != "nan":
                resultado["Resultado"] = tipo_erro
            elif status_sefaz and status_sefaz.lower() != "nan":
                resultado["Resultado"] = status_sefaz
            else:
                resultado["Resultado"] = "Sem informação disponível"
            
            if tipo_erro == "NA":
                resultado["Resultado"] = mensagem
            elif tipo_erro == "PO":
                item, preco, qtd = extrair_dados_po(mensagem)
                resultado.update({"Item": item, "Preço NF": preco, "Quantidade": qtd})
            elif tipo_erro == "Concurrent":
                resultado["Resultado"] = mensagem
            elif "Ordem de venda" in tipo_erro:
                resultado["Resultado"] = "Necessário mandar para devolução"
        
        # Verificar no relatório ERRO NOTAS ATUALIZADAS
        if resultado.get("Resultado") in ["SEFAZ Rejeitado", "Erro"]:
            erro_match = erro_df[erro_df["PEDIDO"] == pedido]
            if not erro_match.empty:
                erro_mensagem = str(erro_match.iloc[0].get("NFE_MENSAGEM", "")).strip()
                resultado["Mensagem Erro"] = erro_mensagem
        
        resultados.append(resultado)
    
    return pd.DataFrame(resultados)

# Interface no Streamlit
st.title("Verificação de Pedidos Posigraf")

pedidos_file = st.file_uploader("Upload do arquivo PEDIDOS POSIGRAF", type=["xlsx"])
sim_file = st.file_uploader("Upload do arquivo Relatório SIM", type=["xlsx"])
nao_file = st.file_uploader("Upload do arquivo Relatório NÃO", type=["xlsx"])
erro_file = st.file_uploader("Upload do arquivo ERRO NOTAS ATUALIZADAS", type=["xlsx"])

if pedidos_file and sim_file and nao_file and erro_file:
    try:
        df_resultado = processar_pedidos(pedidos_file, sim_file, nao_file, erro_file)
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
