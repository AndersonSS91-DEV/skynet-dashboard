import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# carregar CSS
with open("style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<div class="title">📊 Painel Executivo — Validação do Método</div>', unsafe_allow_html=True)

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

# -----------------------------
# CARDS
# -----------------------------

c1,c2,c3,c4,c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="card">
    ROI<br>
    <div class="metric">{roi*100:.2f}%</div>
    </div>
    """,unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
    Volume<br>
    <div class="metric">{volume}</div>
    </div>
    """,unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
    Drawdown<br>
    <div class="metric">{max_dd:.2f}</div>
    </div>
    """,unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
    Robustez<br>
    <div class="metric">{robustez:.2f}</div>
    </div>
    """,unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="card">
    Stake Ideal<br>
    <div class="metric">{stake*100:.2f}%</div>
    </div>
    """,unsafe_allow_html=True)

# -----------------------------
# GRÁFICOS
# -----------------------------

col1,col2 = st.columns(2)

with col1:
    st.subheader("📈 Curva da banca")

    fig = px.line(
        equity,
        template="plotly_dark"
    )

    st.plotly_chart(fig,use_container_width=True)

with col2:
    st.subheader("📉 Drawdown")

    fig2 = px.area(
        drawdown,
        template="plotly_dark"
    )

    st.plotly_chart(fig2,use_container_width=True)
