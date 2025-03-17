import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

st.title("Previsão de Pallets Recebidos (Grid Search ARIMA)")

st.markdown("""
Este aplicativo carrega um arquivo Excel/CSV com histórico de pallets recebidos, 
agrupa por dia (contando pallets únicos) e executa um **grid search manual** com o 
`statsmodels.ARIMA` para encontrar a melhor combinação de (p, d, q) baseada no **AIC**.

**Passos**:
1. Divide os dados em treino (80%) e teste (20%).
2. Testa várias combinações de (p, d, q).
3. Seleciona a de melhor AIC para o período de treino.
4. Avalia a previsão no período de teste (RMSE).
5. Re-treina o "melhor modelo" em todo o dataset e faz a previsão para o futuro.
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

    # Normalizar nomes de colunas (remove espaços etc.)
    df.columns = df.columns.str.strip()

    # Verifica se as colunas esperadas existem
    expected_cols = ["DATA RECEBIMENTO", "PALLET"]
    for col in expected_cols:
        if col not in df.columns:
            st.error(f"Coluna '{col}' não encontrada no arquivo! Ajuste ou renomeie seu arquivo.")
            st.stop()

    # Converter DATA RECEBIMENTO para datetime
    df["DATA RECEBIMENTO"] = pd.to_datetime(df["DATA RECEBIMENTO"], dayfirst=True, errors='coerce')

    # Remove linhas com data inválida
    df = df.dropna(subset=["DATA RECEBIMENTO"])

    # Ordena pela data
    df = df.sort_values("DATA RECEBIMENTO")

    st.subheader("Resumo das datas de recebimento:")
    st.write(f"Data mínima: {df['DATA RECEBIMENTO'].min()}")
    st.write(f"Data máxima: {df['DATA RECEBIMENTO'].max()}")

    # Agrupar por dia e contar pallets únicos
    daily_counts = df.groupby("DATA RECEBIMENTO")["PALLET"].nunique().reset_index()
    daily_counts.rename(columns={"PALLET": "qtde_pallets"}, inplace=True)

    # Transformar em série temporal diária
    daily_counts = daily_counts.set_index("DATA RECEBIMENTO").asfreq("D")
    daily_counts["qtde_pallets"] = daily_counts["qtde_pallets"].fillna(0)

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

    # Separar em treino e teste
    train_size = int(len(daily_counts) * 0.8)
    train_data = daily_counts.iloc[:train_size]
    test_data = daily_counts.iloc[train_size:]

    y_train = train_data["qtde_pallets"]
    y_test = test_data["qtde_pallets"]

    # Definir faixas de (p, d, q) a testar
    p_values = [0, 1, 2, 3]
    d_values = [0, 1, 2]
    q_values = [0, 1, 2, 3]

    best_aic = float("inf")
    best_order = None
    best_model = None

    st.subheader("Executando grid search para (p, d, q) ...")
    progress_bar = st.progress(0)
    total_comb = len(p_values) * len(d_values) * len(q_values)
    comb_count = 0

    for p, d, q in itertools.product(p_values, d_values, q_values):
        comb_count += 1
        progress_bar.progress(comb_count / total_comb)

        try:
            model = ARIMA(y_train, order=(p, d, q))
            model_fit = model.fit()
            aic = model_fit.aic

            if aic < best_aic:
                best_aic = aic
                best_order = (p, d, q)
                best_model = model_fit
        except:
            # Se der erro (ex. converge failure), ignoramos
            pass

    st.write(f"**Melhor (p,d,q)** encontrado: {best_order} com AIC = {best_aic:.2f}")

    if best_model is not None:
        # Previsão no teste
        forecast_test = best_model.forecast(steps=len(y_test))
        forecast_test = pd.Series(forecast_test, index=y_test.index)

        rmse_test = np.sqrt(mean_squared_error(y_test, forecast_test))
        st.write(f"**RMSE (Teste)**: {rmse_test:.2f}")

        # Plot Treino, Teste e Previsão (Teste)
        st.subheader("Treino vs. Teste vs. Previsão (Teste)")
        fig_pred, ax_pred = plt.subplots(figsize=(10,4))
        ax_pred.plot(y_train.index, y_train, label="Treino", color="blue")
        ax_pred.plot(y_test.index, y_test, label="Real (Teste)", color="green")
        ax_pred.plot(forecast_test.index, forecast_test, label="Previsão (Teste)", color="red")
        ax_pred.set_title(f"Treino x Teste x Previsão (Best ARIMA{best_order})")
        ax_pred.set_xlabel("Data")
        ax_pred.set_ylabel("Qtde de Pallets")
        ax_pred.legend()
        st.pyplot(fig_pred)

        st.markdown("---")
        st.subheader("Previsão para o futuro")

        # Re-treinar em todo o dataset
        full_model = ARIMA(daily_counts["qtde_pallets"], order=best_order).fit()

        # Escolher quantos dias prever
        days_to_forecast = st.slider("Selecione quantos dias prever", min_value=7, max_value=365, value=30)
        forecast_future = full_model.forecast(steps=days_to_forecast)

        # Gera índice de datas futuras
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
        ax_fut.set_title(f"Histórico x Previsão Futura (ARIMA{best_order})")
        ax_fut.set_xlabel("Data")
        ax_fut.set_ylabel("Qtde de Pallets")
        ax_fut.legend()
        st.pyplot(fig_fut)

    else:
        st.warning("Não foi encontrado nenhum modelo ARIMA válido nas combinações testadas. Tente ampliar as faixas de (p,d,q).")

else:
    st.info("Por favor, faça o upload de um arquivo para começar.")
