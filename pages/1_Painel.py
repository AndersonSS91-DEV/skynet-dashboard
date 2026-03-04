import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ------------------------------
# DADOS
# ------------------------------

df = pd.read_excel("data/PADRAO_CALCULO.xlsx")

pl = df["ENTRADAS"].sum()
volume = len(df)

roi = pl/volume
dp = df["ENTRADAS"].std()

erro = 1.96/np.sqrt(volume)
robustez = roi/dp

kelly = roi/(dp**2)
stake = kelly*0.25

equity = df["ENTRADAS"].cumsum()

drawdown = equity - equity.cummax()
max_dd = drawdown.min()

# ------------------------------
# TÍTULO
# ------------------------------

st.title("📊 Painel Executivo — Validação do Método")

# ------------------------------
# CARDS
# ------------------------------

c1,c2,c3,c4,c5 = st.columns(5)

c1.metric("ROI",f"{roi*100:.2f}%")
c2.metric("Volume",volume)
c3.metric("Drawdown",f"{max_dd:.2f}")
c4.metric("Robustez",f"{robustez:.2f}")
c5.metric("Stake Ideal",f"{stake*100:.2f}%")

st.write("")

# ------------------------------
# GRÁFICOS
# ------------------------------

g1,g2 = st.columns(2)

with g1:

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=equity,
        mode="lines",
        line=dict(width=3)
    ))

    fig.update_layout(
        template="plotly_dark",
        title="Curva da banca",
        height=350
    )

    st.plotly_chart(fig,use_container_width=True)


with g2:

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        y=drawdown,
        fill="tozeroy",
        mode="lines",
        line=dict(width=2,color="red")
    ))

    fig2.update_layout(
        template="plotly_dark",
        title="Drawdown",
        height=350
    )

    st.plotly_chart(fig2,use_container_width=True)

# ------------------------------
# ESTATÍSTICAS + DIAGNÓSTICO
# ------------------------------

col1,col2 = st.columns(2)

with col1:

    st.subheader("📊 Estatísticas")

    st.write("PL:",round(pl,2))
    st.write("ROI:",f"{roi*100:.2f}%")
    st.write("Desvio padrão:",round(dp,2))
    st.write("Intervalo confiança:",round(erro,2))
    st.write("Kelly:",f"{kelly*100:.2f}%")

with col2:

    st.subheader("🛡 Diagnóstico")

    if erro < 0.1:
        st.success("Amostra estatisticamente confiável")

    if max_dd > -0.25:
        st.success("Drawdown saudável")

    if robustez < 0.2:
        st.warning("Robustez baixa — stake conservadora")

    if robustez > 0.4:
        st.success("Robustez forte")
