import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ==============================
# CSS DO DASHBOARD
# ==============================

st.markdown("""
<style>

.stApp{
background: radial-gradient(circle at top,#1f2937,#020617);
color:white;
}

.dashboard-title{
font-size:34px;
font-weight:600;
margin-bottom:30px;
}

.cards{
display:grid;
grid-template-columns:repeat(5,1fr);
gap:20px;
margin-bottom:30px;
}

.card{
background:rgba(30,41,59,0.8);
padding:22px;
border-radius:12px;
border:1px solid rgba(255,255,255,0.06);
box-shadow:0 10px 30px rgba(0,0,0,0.4);
}

.card-title{
font-size:14px;
color:#9ca3af;
}

.card-value{
font-size:32px;
font-weight:700;
margin-top:6px;
}

.section{
background:rgba(15,23,42,0.8);
padding:25px;
border-radius:12px;
border:1px solid rgba(255,255,255,0.06);
margin-bottom:25px;
}

.section-title{
font-size:20px;
margin-bottom:15px;
}

</style>
""",unsafe_allow_html=True)

# ==============================
# DADOS
# ==============================

df = pd.read_excel("data/PADRAO_CALCULO.xlsx")

pl = df["ENTRADAS"].sum()
volume = len(df)

roi = pl/volume
dp = df["ENTRADAS"].std()

robustez = roi/dp

kelly = roi/(dp**2)
stake = kelly*0.25

equity = df["ENTRADAS"].cumsum()

drawdown = equity - equity.cummax()
max_dd = drawdown.min()

# ==============================
# TÍTULO
# ==============================

st.markdown(
'<div class="dashboard-title">📊 Painel Executivo — Validação do Método</div>',
unsafe_allow_html=True
)

# ==============================
# CARDS
# ==============================

st.markdown(f"""
<div class="cards">

<div class="card">
<div class="card-title">ROI</div>
<div class="card-value">{roi*100:.2f}%</div>
</div>

<div class="card">
<div class="card-title">Volume</div>
<div class="card-value">{volume}</div>
</div>

<div class="card">
<div class="card-title">Drawdown</div>
<div class="card-value">{max_dd:.2f}</div>
</div>

<div class="card">
<div class="card-title">Robustez</div>
<div class="card-value">{robustez:.2f}</div>
</div>

<div class="card">
<div class="card-title">Stake Ideal</div>
<div class="card-value">{stake*100:.2f}%</div>
</div>

</div>
""",unsafe_allow_html=True)

# ==============================
# GRÁFICOS
# ==============================

col1,col2 = st.columns(2)

with col1:

    st.markdown('<div class="section-title">📈 Curva da banca</div>',unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=equity,
        mode='lines',
        line=dict(color='#6ee7b7',width=3)
    ))

    fig.update_layout(
        template="plotly_dark",
        height=380,
        margin=dict(l=0,r=0,t=30,b=0)
    )

    st.plotly_chart(fig,use_container_width=True)


with col2:

    st.markdown('<div class="section-title">📉 Drawdown</div>',unsafe_allow_html=True)

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        y=drawdown,
        fill='tozeroy',
        mode='lines',
        line=dict(color='#ef4444',width=2)
    ))

    fig2.update_layout(
        template="plotly_dark",
        height=380,
        margin=dict(l=0,r=0,t=30,b=0)
    )

    st.plotly_chart(fig2,use_container_width=True)
