import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("📊 Painel Executivo")

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

# -------------------------
# CARDS
# -------------------------

c1,c2,c3,c4,c5 = st.columns(5)

c1.metric("ROI", f"{roi*100:.2f}%")
c2.metric("Volume", volume)
c3.metric("Drawdown", f"{max_dd:.2f}")
c4.metric("Robustez", f"{robustez:.2f}")
c5.metric("Stake Ideal", f"{stake*100:.2f}%")

# -------------------------
# CURVA
# -------------------------

st.subheader("📈 Curva da banca")

fig = px.line(equity)
st.plotly_chart(fig,use_container_width=True)

# -------------------------
# DRAWDOWN
# -------------------------

st.subheader("📉 Drawdown")

fig2 = px.area(drawdown)
st.plotly_chart(fig2,use_container_width=True)
