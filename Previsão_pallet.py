import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Para séries temporais com ARIMA
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

st.title("Previsão de Pallets Recebidos")

st.markdown("""
Este aplicativo faz upload de um arquivo Excel/CSV com histórico de paletes devolvidos
e prevê a quantidade de pallets que chegarão nos próximos dias.  
**Requisitos mínimos do arquivo**:  
- Coluna **DATA RECEBIMENTO** (datas dos recebimentos, formato dia/mês/ano ou similar)  
- Coluna **PALLET** (ID ou código do palete)  
- Cada linha corresponde a uma combinação de (data, pallet, notas fiscais, etc).  
- Se o mesmo pallet aparece várias vezes numa data, será contado apenas **1** para aquela data.
""")

# REMOVER ou COMENTAR a linha abaixo para evitar o erro de estilo
# plt.style.use('seaborn-whitegrid')  # <-- Linha removida/comentada

# Caso queira usar outro estilo suportado, descomente a seguir:
# plt.style.use('ggplot')
# ou: plt.style.use('classic')
# ou: plt.style.use('default')

# Upload do arquivo
uploaded_file = st.file_uploader("Selecione seu arquivo com histórico de pallets", type=["xlsx", "csv"])

if uploaded_file:
    # Lê o arquivo (XLSX ou CSV)
    file_name = uploaded_file.name.lower()
    if file_name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        # Ajuste o 'sep' se o CSV usar outro delimitador
        df = pd.read_csv(uploaded_file, encoding='utf-8', sep=';', engine='python')  
    
    st.subheader("Visualizando as primeiras linhas do DataFrame:")
    st.dataframe(df.head(10))
    
    # Verifica se as colunas esperadas existem
    expected_cols = ["DATA RECEBIMENTO", "PALLET"]
    for col in expected_cols:
        if col not in df.columns:
            st.error(f"Coluna '{col}' não encontrada no arquivo! Ajuste ou renomeie seu arquivo.")
            st.stop()
    
    # Converter DATA RECEBIMENTO para datetime
    df["DATA RECEBIMENTO"] = pd.to_datetime(df["DATA RECEBIMENTO"], dayfirst=True, errors='coerce')
    
    # Remove linhas onde DATA RECEBIMENTO ficou inválido
    df = df.dropna(subset=["DATA RECEBIMENTO"])
    
    # Ordena pela data de recebimento
    df = df.sort_values("DATA RECEBIMENTO")
    
    st.subheader("Resumo das datas de recebimento:")
    st.write(f"Data mínima: {df['DATA RECEBIMENTO'].min()}")
    st.write(f"Data máxima: {df['DATA RECEBIMENTO'].max()}")

    # Agrupar por dia e contar pallets únicos
    daily_counts = df.groupby("DATA RECEBIMENTO")["PALLET"].nunique().reset_index()
    daily_counts.rename(columns={"PALLET": "qtde_pallets"}, inplace=True)
    
    # Configurar índice de datas como série temporal
    daily_counts = daily_counts.set_index("DATA RECEBIMENTO").asfreq("D")
    # Se houver dias sem registro, teremos NaN; preenchendo com 0
    daily_counts["qtde_pallets"] = daily_counts["qtde_pallets"].fillna(0)
    
    # Exibe tabela agregada
    st.subheader("Pallets por dia (após agregação):")
    st.dataframe(daily_counts.head(15))
    
    # Ver gráfico do histórico
    st.subheader("Histórico de pallets recebidos (contagem diária)")
    fig_hist, ax_hist = plt.subplots(figsize=(10,4))
    ax_hist.plot(daily_counts.index, daily_counts["qtde_pallets"], label="Pallets/dia", color="steelblue")
    ax_hist.set_title("Histórico de Pallets Únicos Recebidos por Dia")
    ax_hist.set_xlabel("Data")
    ax_hist.set_ylabel("Qtde de Pallets")
    plt.legend()
    st.pyplot(fig_hist)
    
    # Dividir dados em treino e teste (80% / 20%)
    train_size = int(len(daily_counts) * 0.8)
    train_data = daily_counts.iloc[:train_size]
    test_data = daily_counts.iloc[train_size:]
    
    # Modelo ARIMA (p, d, q) simples
    p, d, q = 1, 1, 1
    try:
        model = ARIMA(train_data["qtde_pallets"], order=(p, d, q))
        model_fit = model.fit()
        
        # Previsão para o período de teste
        forecast_test = model_fit.forecast(steps=len(test_data))
        forecast_test = pd.Series(forecast_test, index=test_data.index)
        
        # Avaliar desempenho (RMSE)
        rmse = np.sqrt(mean_squared_error(test_data["qtde_pallets"], forecast_test))
        st.write(f"**RMSE (Teste)**: {rmse:.2f}")
        
        # Plot Treino, Teste e Previsão
        st.subheader("Treino vs. Teste vs. Previsão (Teste)")
        fig_pred, ax_pred = plt.subplots(figsize=(10,4))
        ax_pred.plot(train_data.index, train_data["qtde_pallets"], label="Treino", color="blue")
        ax_pred.plot(test_data.index, test_data["qtde_pallets"], label="Real (Teste)", color="green")
        ax_pred.plot(test_data.index, forecast_test, label="Previsão (Teste)", color="red")
        ax_pred.set_title("Treino x Teste x Previsão")
        ax_pred.set_xlabel("Data")
        ax_pred.set_ylabel("Qtde de Pallets")
        ax_pred.legend()
        st.pyplot(fig_pred)
        
        st.markdown("""---""")
        st.subheader("Previsão para o futuro")
        # Re-treina o modelo em todo o dataset
        model_final = ARIMA(daily_counts["qtde_pallets"], order=(p, d, q))
        model_final_fit = model_final.fit()
        
        # Define quantos dias à frente queremos prever
        days_to_forecast = st.slider("Selecione quantos dias prever", min_value=7, max_value=365, value=30)
        
        forecast_future = model_final_fit.forecast(steps=days_to_forecast)
        last_date = daily_counts.index[-1]
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), 
                                     periods=days_to_forecast, freq='D')
        forecast_future = pd.Series(forecast_future.values, index=future_dates)
        
        st.write("Previsão de pallets únicos recebidos para os próximos dias:")
        st.dataframe(forecast_future.rename("qtde_pallets_previsao"))
        
        # Plot do histórico completo + previsão futura
        fig_fut, ax_fut = plt.subplots(figsize=(10,4))
        ax_fut.plot(daily_counts.index, daily_counts["qtde_pallets"], label="Histórico", color="blue")
        ax_fut.plot(forecast_future.index, forecast_future, label="Previsão Futura", color="orange")
        ax_fut.set_title("Histórico x Previsão Futura")
        ax_fut.set_xlabel("Data")
        ax_fut.set_ylabel("Qtde de Pallets")
        ax_fut.legend()
        st.pyplot(fig_fut)
        
    except ValueError as e:
        st.error(f"Ocorreu um erro ao ajustar o modelo ARIMA: {e}")
else:
    st.info("Por favor, faça o upload de um arquivo para começar.")
