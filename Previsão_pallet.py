import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# SARIMAX em statsmodels
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error

st.title("Previsão Semanal de Pallets (DATA TRIAGEM)")

st.markdown("""
**Objetivo**: Ler um arquivo Excel/CSV com histórico de pallets, usando **DATA TRIAGEM** como data de referência,
agrupar por semana e prever a quantidade futura de pallets via um _grid search_ de SARIMAX.

**Requisitos**:
- Colunas **DATA TRIAGEM** e **PALLET** em seu arquivo.
- Cada linha representa um registro de pallet; se o mesmo pallet aparecer várias vezes numa semana, será contado 1 vez.
- Ajuste o range de parâmetros conforme a complexidade dos dados.
- Ajuste **m=52** se quiser detectar sazonalidade anual em série semanal.
""")

# Upload do arquivo
uploaded_file = st.file_uploader("Selecione seu arquivo Excel ou CSV", type=["xlsx", "csv"])

if uploaded_file:
    # Ler CSV ou Excel
    if uploaded_file.name.lower().endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        # Ajuste se seu CSV tem outro delimitador
        df = pd.read_csv(uploaded_file, encoding='utf-8', sep=';', engine='python')
    
    st.subheader("Visualizando as primeiras linhas do DataFrame:")
    st.dataframe(df.head(10))

    # Limpar espaços nos nomes das colunas
    df.columns = df.columns.str.strip()

    # Verificar se temos as colunas necessárias
    expected_cols = ["DATA TRIAGEM", "PALLET"]
    for col in expected_cols:
        if col not in df.columns:
            st.error(f"Coluna '{col}' não encontrada! Ajuste o arquivo.")
            st.stop()

    # Converter DATA TRIAGEM para datetime
    df["DATA TRIAGEM"] = pd.to_datetime(df["DATA TRIAGEM"], dayfirst=True, errors='coerce')

    # Remover linhas com data inválida
    df = df.dropna(subset=["DATA TRIAGEM"])

    # Ordenar pelas datas de triagem
    df = df.sort_values("DATA TRIAGEM")

    st.write(f"Data mínima: {df['DATA TRIAGEM'].min()}")
    st.write(f"Data máxima: {df['DATA TRIAGEM'].max()}")

    # -------------------------------------------------------
    # AGRUPAR POR SEMANA
    # -------------------------------------------------------
    # 1) Definir a coluna de data como índice
    df = df.set_index("DATA TRIAGEM")

    # 2) Agrupar por semana ("W") e contar pallets únicos
    weekly_counts = df.resample("W")["PALLET"].nunique()

    # 3) Converter de volta para DataFrame (opcional)
    weekly_counts = weekly_counts.to_frame(name="qtde_pallets")

    # Preencher semanas sem ocorrência com 0
    weekly_counts["qtde_pallets"] = weekly_counts["qtde_pallets"].fillna(0)

    st.subheader("Dados após agregação semanal:")
    st.dataframe(weekly_counts.head(15))

    # Plot do histórico semanal
    st.subheader("Histórico de pallets (semanal, por DATA TRIAGEM)")
    fig_hist, ax_hist = plt.subplots(figsize=(10,4))
    ax_hist.plot(weekly_counts.index, weekly_counts["qtde_pallets"], label="Pallets/semana", color="blue")
    ax_hist.set_title("Histórico de Pallets Únicos por Semana (Triagem)")
    ax_hist.set_xlabel("Data (Semanas)")
    ax_hist.set_ylabel("Qtde de Pallets")
    ax_hist.legend()
    st.pyplot(fig_hist)

    # Dividir em treino (80%) e teste (20%)
    train_size = int(len(weekly_counts) * 0.8)
    train_data = weekly_counts.iloc[:train_size]
    test_data = weekly_counts.iloc[train_size:]

    y_train = train_data["qtde_pallets"]
    y_test = test_data["qtde_pallets"]

    # ---------------------------------------------------
    # GRID SEARCH SARIMAX
    # ---------------------------------------------------
    p_values = [0, 1, 2]
    d_values = [0, 1]
    q_values = [0, 1, 2]

    # Sazonalidade: se quiser capturar padrão anual em série semanal, m=52
    P_values = [0, 1]  
    D_values = [0, 1]
    Q_values = [0, 1]
    seasonal_period = 52  # Semanas no ano (aprox. 52)

    best_aic = np.inf
    best_order = None
    best_seasonal_order = None
    best_model = None

    with st.spinner("Executando grid search SARIMAX (agrupamento semanal)..."):
        for p in p_values:
            for d in d_values:
                for q in q_values:
                    for P in P_values:
                        for D in D_values:
                            for Q in Q_values:
                                try:
                                    model = SARIMAX(
                                        y_train,
                                        order=(p, d, q),
                                        seasonal_order=(P, D, Q, seasonal_period),
                                        enforce_stationarity=False,
                                        enforce_invertibility=False
                                    )
                                    result = model.fit(disp=False)
                                    if result.aic < best_aic:
                                        best_aic = result.aic
                                        best_order = (p, d, q)
                                        best_seasonal_order = (P, D, Q, seasonal_period)
                                        best_model = result
                                except:
                                    pass

    if best_model is None:
        st.error("Nenhum modelo foi ajustado com sucesso na grid search!")
        st.stop()
    
    st.write(f"**Melhor AIC**: {best_aic:.2f}")
    st.write(f"**Melhor order**: {best_order}")
    st.write(f"**Melhor seasonal_order**: {best_seasonal_order}")

    # Previsão no conjunto de teste
    forecast_test = best_model.forecast(steps=len(test_data))
    forecast_test = pd.Series(forecast_test, index=test_data.index)

    # Avaliar RMSE
    rmse_test = np.sqrt(mean_squared_error(y_test, forecast_test))
    st.write(f"**RMSE no teste**: {rmse_test:.2f}")

    # Plot Treino/Teste/Previsão
    st.subheader("Treino vs. Teste vs. Previsão no teste (Semanal)")
    fig_pred, ax_pred = plt.subplots(figsize=(10,4))
    ax_pred.plot(y_train.index, y_train, label="Treino", color="blue")
    ax_pred.plot(y_test.index, y_test, label="Teste (Real)", color="green")
    ax_pred.plot(forecast_test.index, forecast_test, label="Previsão (Teste)", color="red")
    ax_pred.set_title("Treino x Teste x Previsão (SARIMAX - Semanal)")
    ax_pred.set_xlabel("Data (Semanas)")
    ax_pred.set_ylabel("Qtde de Pallets")
    ax_pred.legend()
    st.pyplot(fig_pred)

    # ---------------------------------------------------
    # MODELO FINAL: Ajustar em todo o dataset
    # ---------------------------------------------------
    st.markdown("---")
    st.subheader("Previsão futura (semanal)")

    final_model = SARIMAX(
        weekly_counts["qtde_pallets"],
        order=best_order,
        seasonal_order=best_seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    final_result = final_model.fit(disp=False)

    # Quantas semanas prever?
    weeks_to_forecast = st.slider("Semanas para prever:", 4, 52, 12)
    forecast_future = final_result.forecast(steps=weeks_to_forecast)

    # Índice de datas futuras (semanal)
    last_date = weekly_counts.index[-1]
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=7), 
        periods=weeks_to_forecast, 
        freq='W'
    )
    forecast_future = pd.Series(forecast_future.values, index=future_dates)

    st.write("Previsão de pallets (semana) para as próximas semanas:")
    st.dataframe(forecast_future.rename("qtde_pallets_previsao"))

    # Plot do histórico + previsão futura
    fig_fut, ax_fut = plt.subplots(figsize=(10,4))
    ax_fut.plot(weekly_counts.index, weekly_counts["qtde_pallets"], label="Histórico", color="blue")
    ax_fut.plot(forecast_future.index, forecast_future, label="Previsão Futura", color="orange")
    ax_fut.set_title("Histórico x Previsão Futura (SARIMAX - Semanal)")
    ax_fut.set_xlabel("Data (Semanas)")
    ax_fut.set_ylabel("Qtde de Pallets")
    ax_fut.legend()
    st.pyplot(fig_fut)

else:
    st.info("Faça upload de um arquivo para iniciar a previsão.")
