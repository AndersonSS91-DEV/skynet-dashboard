import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================
# CARREGAR DADOS
# ===============================

st.sidebar.subheader("📂 Dados")

arquivo = st.sidebar.file_uploader(
    "Carregar planilha de trades",
    type=["xlsx", "csv"]
)

# ===============================
# CARREGAMENTO
# ===============================

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

if "ENTRADAS" not in df.columns:
    st.error("Coluna ENTRADAS não encontrada na planilha")
    st.stop()

df["ENTRADAS"] = pd.to_numeric(df["ENTRADAS"], errors="coerce")
retornos = df["ENTRADAS"].dropna()

# ===============================
# ABAS
# ===============================

tab_metodo, tab_tools = st.tabs([
    "📊 Validação do Método",
    "🧠 Trading Tools"
])

# =========================================================
# ABA MÉTODO
# =========================================================

with tab_metodo:

    st.subheader("Dados")

    janela = st.radio(
        "Amostras analisadas",
        [100, 500, 1000],
        index=1,
        horizontal=True
    )

    dados_plot = retornos.tail(janela)

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
            line=dict(width=2, color="#38bdf8")
        ))

        fig.update_layout(
            template="plotly_dark",
            title="Curva da banca"
        )

        st.plotly_chart(fig, use_container_width=True)

    with g2:

        fig2 = go.Figure()

        fig2.add_trace(go.Scatter(
            y=drawdown,
            mode="lines",
            line=dict(width=2, color="#ef4444"),
            fill="tozeroy"
        ))

        fig2.update_layout(
            template="plotly_dark",
            title="Drawdown"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # ===============================
    # ESTATÍSTICAS
    # ===============================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📊 Estatísticas")

        st.write(f"PL: {pl:.2f}")
        st.write(f"ROI: {roi*100:.2f}%")
        st.write(f"Desvio padrão: {dp:.2f}")
        st.write(f"Expectância: {expectancy:.2f}")
        st.write(f"Profit Factor: {profit_factor:.2f}")
        st.write(f"Ulcer Index: {ulcer:.2f}")
        st.write(f"SQN: {sqn:.2f}")
        st.write(f"Risco de ruína: {risk_ruin*100:.2f}%")
        st.write(f"Probabilidade de 5 reds: {prob_5_losses*100:.2f}%")

    with col2:

        st.subheader("🛡 Diagnóstico")

        if sqn > 2.5 and profit_factor > 1.5:
            st.success("Sistema forte")
        elif sqn > 1.6:
            st.warning("Sistema moderado")
        else:
            st.error("Sistema fraco")

    # ===============================
    # GAUGE RISCO DE RUÍNA
    # ===============================

    st.subheader("💀 Risco de Ruína")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(risk_ruin*100, 2),
        number={'suffix': "%"},
        gauge={'axis': {'range': [0, 100]}}
    ))

    st.plotly_chart(fig, use_container_width=True)

    # ===============================
    # MONTE CARLO
    # ===============================

    st.subheader("📈 Monte Carlo")

    simulacoes = 500
    trades = volume

    resultados = []

    for i in range(simulacoes):
        sim = np.random.choice(dados_plot, size=trades, replace=True)
        resultados.append(sim.cumsum()[-1])

    fig = go.Figure()

    fig.add_trace(go.Histogram(x=resultados))

    fig.update_layout(
        template="plotly_dark",
        title="Distribuição de resultados"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ===============================
    # SEMÁFORO
    # ===============================

    st.subheader("🚦 Semáforo")

    if sqn > 2.5 and profit_factor > 1.5 and risk_ruin < 0.05:
        st.success("🟢 MÉTODO PROFISSIONAL")
    elif sqn > 1.6:
        st.warning("🟡 MÉTODO OPERÁVEL")
    else:
        st.error("🔴 MÉTODO INSTÁVEL")

# =========================================================
# ABA TRADING TOOLS
# =========================================================

with tab_tools:

    st.title("🧠 Trading Tools")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Cashout",
        "Dutching",
        "Value Bet",
        "Simulador"
    ])

    with tab1:

        st.subheader("Cashout")

        c1, c2, c3 = st.columns(3)

        back_odd = c1.number_input("Back Odd", value=1.80)
        back_stake = c2.number_input("Stake", value=100.0)
        lay_odd = c3.number_input("Lay Odd", value=2.00)

        lay_stake = (back_odd * back_stake) / lay_odd

        st.metric("Stake Lay", f"{lay_stake:.2f}")

    with tab2:

        st.subheader("Dutching")

        n = st.slider("Seleções", 2, 6, 3)

        odds = [st.number_input(f"Odd {i+1}", value=2.0, key=i) for i in range(n)]

        stake_total = st.number_input("Stake total", value=100.0)

        inv = [1/o for o in odds]
        soma = sum(inv)

        stakes = [(stake_total*(i/soma)) for i in inv]

        df_dutch = pd.DataFrame({
            "Odd": odds,
            "Stake": stakes
        })

        st.dataframe(df_dutch)

    with tab3:

        st.subheader("Value Bet")

        odd = st.number_input("Odd", value=2.0)
        prob = st.number_input("Probabilidade (%)", value=55.0)

        prob /= 100
        ev = (prob * odd) - 1

        st.metric("EV", f"{ev:.3f}")

    with tab4:

        st.subheader("Simulador")

        banca = st.number_input("Banca", value=1000.0)
        roi_sim = st.slider("ROI (%)", 0.5, 10.0, 3.0)
        trades = st.slider("Trades", 10, 500, 100)

        curva = [banca]

        for i in range(trades):
            lucro = curva[-1]*(roi_sim/100)
            curva.append(curva[-1] + lucro)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            y=curva,
            mode="lines"
        ))

        fig.update_layout(template="plotly_dark")

        st.plotly_chart(fig, use_container_width=True)
