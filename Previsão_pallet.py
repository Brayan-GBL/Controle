import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Auto ARIMA (pmdarima)
from pmdarima.arima import auto_arima
from sklearn.metrics import mean_squared_error

# Comentado para evitar conflitos de estilo em alguns ambientes
# plt.style.use('ggplot')

st.title("Previsão de Pallets Recebidos (auto_arima)")

st.markdown("""
Este aplicativo carrega um arquivo Excel/CSV com histórico de pallets recebidos, 
agrupa por dia (contando pallets únicos) e utiliza **auto_arima** (da biblioteca `pmdarima`) 
para encontrar automaticamente parâmetros de um modelo ARIMA (ou SARIMA) com possível sazonalidade.

**Observações**:
- Verifique se o arquivo tem as colunas **DATA RECEBIMENTO** e **PALLET**.
- Se o mesmo pallet aparecer várias vezes no mesmo dia, ele será contado apenas 1 vez naquele dia.
- Ajuste a sazonalidade (`m`) no código, caso queira detectar padrões semanais, mensais etc.
""")

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
    
    # Normalizar nomes de colunas para evitar espaços/caracteres ocultos
    df.columns = df.columns.str.strip()
    
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
    
    # Configurar índice de datas como série temporal (freq diária)
    daily_counts = daily_counts.set_index("DATA RECEBIMENTO").asfreq("D")
    daily_counts["qtde_pallets"] = daily_counts["qtde_pallets"].fillna(0)

    # Exibe tabela agregada
    st.subheader("Pallets por dia (após agregação):")
    st.dataframe(daily_counts.head(15))
    
    # Plot do histórico
    st.subheader("Histórico de pallets recebidos (contagem diária)")
    fig_hist, ax_hist = plt.subplots(figsize=(10,4))
    ax_hist.plot(daily_counts.index, daily_counts["qtde_pallets"], label="Pallets/dia", color="blue")
    ax_hist.set_title("Histórico de Pallets Únicos Recebidos por Dia")
    ax_hist.set_xlabel("Data")
    ax_hist.set_ylabel("Qtde de Pallets")
    ax_hist.legend()
    st.pyplot(fig_hist)

    # Dividir dados em treino e teste
    train_size = int(len(daily_counts) * 0.8)
    train_data = daily_counts.iloc[:train_size]
    test_data = daily_counts.iloc[train_size:]

    # Converte para Series
    y_train = train_data["qtde_pallets"]
    y_test = test_data["qtde_pallets"]

    st.subheader("Ajustando modelo auto_arima...")
    # Ajustar auto_arima
    # m=7 para detectar sazonalidade semanal. Ajuste se quiser (m=30, m=365, etc).
    model = auto_arima(
        y=y_train,             # dados de treino
        start_p=1, start_q=1,  # valores iniciais para p e q
        max_p=5, max_q=5,      # valores máximos para p e q
        seasonal=True,         # se queremos capturar sazonalidade
        m=7,                   # período sazonal (7=semanal, 12=mensal, 365=anual, etc)
        d=None,                # auto_arima tenta detectar o grau de diferenciação
        D=None,                # auto_arima também tenta detectar diferenciação sazonal
        trace=True,            # mostra logs do processo de busca
        error_action='ignore', # ignora certos erros
        suppress_warnings=True,
        stepwise=True          # método de busca iterativo (mais rápido que grid completo)
    )

    st.write("Modelo encontrado:", model.summary())

    # Faz previsão no período de teste
    forecast_test = model.predict(n_periods=len(y_test))
    forecast_test = pd.Series(forecast_test, index=y_test.index)

    # Calcula RMSE
    rmse = np.sqrt(mean_squared_error(y_test, forecast_test))
    st.write(f"**RMSE (Teste)**: {rmse:.2f}")

    # Plot Treino, Teste e Previsão (Teste)
    st.subheader("Treino vs. Teste vs. Previsão (Teste)")
    fig_pred, ax_pred = plt.subplots(figsize=(10,4))
    ax_pred.plot(y_train.index, y_train, label="Treino", color="blue")
    ax_pred.plot(y_test.index, y_test, label="Real (Teste)", color="green")
    ax_pred.plot(forecast_test.index, forecast_test, label="Previsão (Teste)", color="red")
    ax_pred.set_title("Treino x Teste x Previsão (auto_arima)")
    ax_pred.set_xlabel("Data")
    ax_pred.set_ylabel("Qtde de Pallets")
    ax_pred.legend()
    st.pyplot(fig_pred)

    st.markdown("---")
    st.subheader("Previsão para o futuro")
    
    # Agora ajustamos o modelo com todos os dados (train + test)
    model_final = auto_arima(
        y=daily_counts["qtde_pallets"], 
        seasonal=True,
        m=7,
        stepwise=True,
        trace=False,
        error_action='ignore',
        suppress_warnings=True
    )
    # Treina no dataset completo
    model_final.fit(daily_counts["qtde_pallets"])

    # Define quantos dias à frente queremos prever
    days_to_forecast = st.slider("Selecione quantos dias prever", min_value=7, max_value=365, value=30)

    forecast_future = model_final.predict(n_periods=days_to_forecast)
    # Gera índice de datas futuras
    last_date = daily_counts.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                 periods=days_to_forecast, freq='D')
    forecast_future = pd.Series(forecast_future, index=future_dates)

    st.write("Previsão de pallets únicos recebidos para os próximos dias:")
    st.dataframe(forecast_future.rename("qtde_pallets_previsao"))

    # Plot do histórico completo + previsão futura
    fig_fut, ax_fut = plt.subplots(figsize=(10,4))
    ax_fut.plot(daily_counts.index, daily_counts["qtde_pallets"], label="Histórico", color="blue")
    ax_fut.plot(forecast_future.index, forecast_future, label="Previsão Futura", color="orange")
    ax_fut.set_title("Histórico x Previsão Futura (auto_arima)")
    ax_fut.set_xlabel("Data")
    ax_fut.set_ylabel("Qtde de Pallets")
    ax_fut.legend()
    st.pyplot(fig_fut)

else:
    st.info("Por favor, faça o upload de um arquivo para começar.")
