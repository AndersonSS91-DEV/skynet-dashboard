import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# DASHBOARD
# =====================================================

st.sidebar.subheader("📂 Dados")

arquivo = st.sidebar.file_uploader(
    "Carregar planilha de trades",
    type=["xlsx", "csv"]
)

if arquivo is not None:

    if arquivo.name.endswith(".csv"):
        df = pd.read_csv(arquivo)
    else:
        df = pd.read_excel(arquivo)

    st.sidebar.success("Arquivo carregado")

else:

    caminho_padrao = "data/trades_padrao.xlsx"

    if os.path.exists(caminho_padrao):

        df = pd.read_excel(caminho_padrao)
        st.sidebar.info("Usando base padrão")

    else:

        st.info("Carregue uma planilha para iniciar a análise")
        st.stop()

# ===============================
# NORMALIZAR COLUNAS
# ===============================

df.columns = df.columns.str.strip().str.upper()

# ===============================
# VALIDAR COLUNA NECESSÁRIA
# ===============================

if "ENTRADAS" not in df.columns:
    st.error("Coluna ENTRADAS não encontrada na planilha")
    st.stop()

# ===============================
# CONVERTER PARA NUMÉRICO
# ===============================

df["ENTRADAS"] = pd.to_numeric(df["ENTRADAS"], errors="coerce")

retornos = df["ENTRADAS"].dropna()

# ===============================
# SELETOR DE AMOSTRA
# ===============================

st.subheader("Dados")

janela = st.radio(
    "Amostras analisadas",
    [100, 500, 1000],
    index=1,
    horizontal=True
)

dados_plot = retornos.tail(janela)

# ===============================
# CÁLCULOS BÁSICOS
# ===============================

if (df["ENTRADAS"] > 0).any():
    odd_media = df.loc[df["ENTRADAS"] > 0, "ENTRADAS"].mean() + 1
else:
    odd_media = np.nan

pl = retornos.sum()
volume = len(retornos)

roi = pl / volume
dp = retornos.std()

erro = 1.96 / np.sqrt(volume)

robustez = roi / dp if dp != 0 else 0
expectancy = retornos.mean()

sqn = (np.sqrt(volume) * expectancy / dp) if dp != 0 else 0

Celeste = roi / (dp ** 2) if dp != 0 else 0
stake = Celeste * 0.25

equity = dados_plot.cumsum()

drawdown = equity - equity.cummax()
max_dd = drawdown.min()

banca = 0.5
risk_ruin = np.exp(-2 * roi * banca / (dp ** 2)) if dp != 0 else 1

lucros = retornos[retornos > 0].sum()
perdas = abs(retornos[retornos < 0].sum())

profit_factor = lucros / perdas if perdas != 0 else 0

winrate = (retornos > 0).mean()

prob_5_losses = (1 - winrate) ** 5

ulcer = np.sqrt(np.mean(drawdown ** 2))

score = (
    robustez * 30 +
    profit_factor * 20 +
    expectancy * 30 +
    (1 - risk_ruin) * 20
)

st.title("📊 Validação do Método")

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

c1.metric("ROI", f"{roi*100:.2f}%")
c2.metric("Volume", volume)
c3.metric("Drawdown", f"{max_dd:.2f}")
c4.metric("Robustez", f"{robustez:.2f}")
c5.metric("Stake Celeste", f"{stake*100:.2f}%")
c6.metric("P/L", f"{pl:.2f}")
c7.metric("Odd Média", f"{odd_media:.2f}")
