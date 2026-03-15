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
# ABAS
# =====================================================

tab1, tab2 = st.tabs(["📊 Dashboard", "🧠 Calculadora"])

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.subheader("📂 Dados")

arquivo = st.sidebar.file_uploader(
    "Carregar planilha de trades",
    type=["xlsx", "csv"]
)

df = None

# =====================================================
# CARREGAMENTO HÍBRIDO
# =====================================================

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

# =====================================================
# DASHBOARD
# =====================================================

with tab1:

    if df is None:
        st.info("📂 Carregue uma planilha para iniciar a análise")
        st.stop()

    # ===============================
    # NORMALIZAR COLUNAS
    # ===============================

    df.columns = df.columns.str.strip().str.upper()

    # ===============================
    # VALIDAR COLUNA
    # ===============================

    if "ENTRADAS" not in df.columns:
        st.error("Coluna ENTRADAS não encontrada na planilha")
        st.stop()

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
    # CÁLCULOS
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

    # ===============================
    # TÍTULO
    # ===============================

    st.title("📊 Validação do Método")

    # ===============================
    # CARDS
    # ===============================

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

    c1.metric("ROI", f"{roi*100:.2f}%")
    c2.metric("Volume", volume)
    c3.metric("Drawdown", f"{max_dd:.2f}")
    c4.metric("Robustez", f"{robustez:.2f}")
    c5.metric("Stake Celeste", f"{stake*100:.2f}%")
    c6.metric("P/L", f"{pl:.2f}")
    c7.metric("Odd Média", f"{odd_media:.2f}")

    # ===============================
    # GRÁFICOS
    # ===============================

    g1, g2 = st.columns(2)

    with g1:

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            y=equity,
            mode="lines",
            line=dict(width=3, color="#38bdf8")
        ))

        fig.update_layout(
            template="plotly_dark",
            title="Curva da banca",
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    with g2:

        fig2 = go.Figure()

        fig2.add_trace(go.Scatter(
            y=drawdown,
            mode="lines",
            line=dict(width=3, color="#ef4444"),
            fill="tozeroy"
        ))

        fig2.update_layout(
            template="plotly_dark",
            title="Drawdown",
            height=350
        )

        st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# CALCULADORA
# =====================================================

with tab2:

    st.title("🧠 Trading Tools")

    st.markdown("### Cashout / Greenbook")

    col1, col2, col3 = st.columns(3)

    back_odd = col1.number_input("Back Odd", value=1.80)
    back_stake = col2.number_input("Stake", value=100.0)
    lay_odd = col3.number_input("Lay Odd", value=2.00)

    lay_stake = (back_odd * back_stake) / lay_odd
    lucro_loss = lay_stake - back_stake

    c4, c5 = st.columns(2)
    c4.metric("Stake Lay", f"{lay_stake:.2f}")
    c5.metric("Green", f"{lucro_loss:.2f}")

    st.markdown("---")

    st.markdown("### Dutching")

    n = st.slider("Número de seleções", 2, 6, 3)

    odds = []

    for i in range(n):
        odds.append(
            st.number_input(f"Odd {i+1}", value=2.0, key=f"odd_{i}")
        )

    stake_total = st.number_input("Stake total", value=100.0)

    inv = [1/o for o in odds]
    soma = sum(inv)

    stakes = [(stake_total*(i/soma)) for i in inv]

    df_dutch = pd.DataFrame({
        "Odd": odds,
        "Stake": stakes
    })

    st.dataframe(df_dutch, use_container_width=True)

    st.markdown("---")

    st.markdown("### Detector de Value Bet")

    c1, c2 = st.columns(2)

    odd = c1.number_input("Odd mercado", value=2.0)
    prob_modelo = c2.number_input("Probabilidade modelo (%)", value=55.0)

    prob_modelo /= 100
    prob_imp = 1/odd
    ev = (prob_modelo * odd) - 1

    c3, c4, c5 = st.columns(3)

    c3.metric("Prob Implícita", f"{prob_imp*100:.2f}%")
    c4.metric("Prob Modelo", f"{prob_modelo*100:.2f}%")
    c5.metric("EV", f"{ev:.3f}")

    if ev > 0:
        st.success("Aposta com valor esperado positivo")
    else:
        st.error("Sem valor esperado")

    st.markdown("---")

    st.markdown("### Simulador de Banca")

    banca = st.number_input("Banca inicial", value=1000.0)
    roi = st.slider("ROI médio (%)", 0.5, 10.0, 3.0)
    trades = st.slider("Trades", 10, 500, 100)

    curva = [banca]

    for _ in range(trades):
        lucro = curva[-1] * (roi/100)
        curva.append(curva[-1] + lucro)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=curva,
        mode="lines",
        line=dict(width=3, color="#38bdf8")
    ))

    fig.update_layout(
        template="plotly_dark",
        title="Crescimento da banca",
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)
