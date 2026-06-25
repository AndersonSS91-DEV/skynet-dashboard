import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# ===============================
# CONFIG
# ===============================

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
# LEITURA
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

# ===============================
# VALIDAR
# ===============================

if "ENTRADAS" not in df.columns:

    st.error("Coluna ENTRADAS não encontrada na planilha")
    st.stop()

# ===============================
# CONVERTER
# ===============================

df["ENTRADAS"] = pd.to_numeric(
    df["ENTRADAS"],
    errors="coerce"
)

df = df.dropna(subset=["ENTRADAS"])

# ===============================
# ORDENAR DATA
# ===============================

if "DATA" in df.columns:

    try:
        df["DATA"] = pd.to_datetime(
            df["DATA"],
            errors="coerce"
        )

        df = df.sort_values("DATA")

    except:
        pass

# ===============================
# RETORNOS
# ===============================

retornos = df["ENTRADAS"].reset_index(drop=True)

# ===============================
# SELETOR
# ===============================

st.subheader("Dados")

opcoes = [
    25, 50, 75, 100, 125, 150, 175, 200,
    225, 250, 275, 300, 325, 350, 375,
    400, 425, 450, 475, 500, 750, 1000,
    1250, 1500, 1750, 2000, 2500, 3000,
    3500, 4000, 4500, 5000, 6000, 7000,
    8000, 9000, 10000
]

max_disponivel = len(retornos)

opcoes_validas = [
    x for x in opcoes if x <= max_disponivel
]

if max_disponivel not in opcoes_validas:
    opcoes_validas.append(max_disponivel)

if len(opcoes_validas) == 0:
    opcoes_validas = [max_disponivel]

janela = st.radio(
    "Amostras analisadas",
    opcoes_validas,
    index=min(2, len(opcoes_validas)-1),
    horizontal=True
)

# ===============================
# CURVA TEMPORAL CORRETA
# ===============================

dados_plot = retornos.iloc[:janela]

# ===============================
# CÁLCULOS
# ===============================

retornos_calc = dados_plot.copy()

volume = len(retornos_calc)

pl = retornos_calc.sum()

yield_medio = (
    pl / volume
    if volume > 0 else 0
)

dp = retornos_calc.std()

erro = (
    1.96 / np.sqrt(volume)
    if volume > 0 else 0
)

expectancy = retornos_calc.mean()

robustez = (
    yield_medio / dp
    if dp != 0 else 0
)

sqn = (
    np.sqrt(volume) *
    expectancy / dp
    if dp != 0 else 0
)

Celeste = (
    yield_medio / (dp ** 2)
    if dp != 0 else 0
)

stake = Celeste * 0.25

# ===============================
# CURVA
# ===============================

capital_inicial = 100

equity = (
    capital_inicial +
    retornos_calc.cumsum()
)

equity_max = equity.cummax()

equity_max[equity_max == 0] = 1e-9

drawdown = (
    (equity - equity_max) /
    equity_max
)

max_dd = drawdown.min()

# ===============================
# MÉTRICAS
# ===============================

lucros = retornos_calc[
    retornos_calc > 0
].sum()

perdas = abs(
    retornos_calc[
        retornos_calc < 0
    ].sum()
)

profit_factor = (
    lucros / perdas
    if perdas != 0 else 0
)

winrate = (
    retornos_calc > 0
).mean()

# ==================================
# AWAY % (REDS)
# ==================================

reds = (retornos_calc < 0).sum()

away_red_pct = (
    reds / volume
    if volume > 0 else 0
)

home_not_lose = 1 - away_red_pct

prob_5_losses = (
    (1 - winrate) ** 5
)

ulcer = np.sqrt(
    np.mean((drawdown * 100) ** 2)
)

# ===============================
# RISCO DE RUÍNA
# ===============================

simulacoes_ruina = 5000

ruinas = 0

# capital inicial evita explosão
# do drawdown no começo da curva
capital_inicial = 12000

for _ in range(simulacoes_ruina):

    sim = np.random.choice(
        retornos_calc,
        size=volume,
        replace=True
    )

    # ===============================
    # CURVA COM CAPITAL INICIAL
    # ===============================

    curva = (
        capital_inicial +
        pd.Series(sim).cumsum()
    )

    # ===============================
    # TOPO HISTÓRICO
    # ===============================

    curva_max = curva.cummax()

    # proteção
    curva_max[curva_max == 0] = 1e-9

    # ===============================
    # DRAWDOWN %
    # ===============================

    dd_ruina = (
        (curva - curva_max) /
        curva_max
    )

    # ===============================
    # RUÍNA = DD MAIOR QUE 50%
    # ===============================

    if dd_ruina.min() <= -0.50:

        ruinas += 1

# ===============================
# RESULTADO FINAL
# ===============================

risk_ruin = (
    ruinas / simulacoes_ruina
)

# ===============================
# SCORE
# ===============================

pf_score = min(
    profit_factor / 3,
    1
)

sqn_score = min(
    sqn / 7,
    1
)

robustez_score = min(
    robustez / 1,
    1
)

dd_score = max(
    0,
    1 + max_dd
)

score = (
    pf_score * 30 +
    sqn_score * 30 +
    robustez_score * 20 +
    dd_score * 20
)

# ===============================
# ODD MÉDIA
# ===============================

if "ODD" in df.columns:

    odd_media = df["ODD"].mean()

elif "ODD_H" in df.columns:

    odd_media = df["ODD_H"].mean()

else:

    odd_media = np.nan

# ===============================
# TÍTULO
# ===============================

st.markdown("""
<style>
.titulo-principal {
    font-size: 26px;
    font-weight: 600;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="titulo-principal">📊 Validação do Método</div>',
    unsafe_allow_html=True
)

# ===============================
# CARDS
# ===============================

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

c1.metric(
    "Yield Médio",
    f"{yield_medio*100:.2f}%"
)

c2.metric(
    "Volume",
    volume
)

c3.metric(
    "Drawdown",
    f"{max_dd*100:.2f}%"
)

c4.metric(
    "Robustez",
    f"{robustez:.2f}"
)

c5.metric(
    "Stake Celeste",
    f"{stake*100:.2f}%"
)

c6.metric(
    "Unidades",
    f"{pl:.2f}"
)

c7.metric(
    "Odd Média",
    f"{odd_media:.2f}"
)

c8.metric(
    "Controle(-)%",
    f"{away_red_pct*100:.2f}%"
)


# ===============================
# GRÁFICOS
# ===============================

from plotly.subplots import make_subplots

# ===============================
# GRÁFICO ÚNICO
# ===============================

st.subheader("📈 Equity + Drawdown")

fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.75, 0.25]
)

# ===============================
# EQUITY
# ===============================

fig.add_trace(

    go.Scatter(
        y=equity,
        mode="lines",
        line=dict(
            width=3,
            color="#38bdf8"
        ),
        name="Equity"
    ),

    row=1,
    col=1
)

# ===============================
# DRAWDOWN
# ===============================

fig.add_trace(

    go.Scatter(
        y=drawdown * 100,
        mode="lines",
        fill="tozeroy",

        fillcolor="rgba(250,204,21,0.35)",

        line=dict(
            width=2,
            color="#facc15"
        ),

        name="Drawdown %"
    ),

    row=2,
    col=1
)
# ===============================
# LAYOUT
# ===============================

fig.update_layout(

    template="plotly_dark",

    height=700,

    margin=dict(
        l=20,
        r=20,
        t=40,
        b=20
    ),

    hovermode="x unified",

    showlegend=False
)


# ===============================
# EIXOS
# ===============================

equity_min = equity.min()
equity_max = equity.max()

amplitude = equity_max - equity_min

# Apenas 5% de folga
margem = amplitude * 0.05

if margem < 2:
    margem = 2

# Escala automática
if amplitude <= 50:
    dtick = 5
elif amplitude <= 100:
    dtick = 10
elif amplitude <= 200:
    dtick = 20
elif amplitude <= 500:
    dtick = 50
elif amplitude <= 1000:
    dtick = 100
else:
    dtick = 200

fig.update_yaxes(
    title_text="Equity",
    range=[
        np.floor((equity_min - margem) / dtick) * dtick,
        np.ceil((equity_max + margem) / dtick) * dtick
    ],
    dtick=dtick,
    row=1,
    col=1
)

# Drawdown
dd_min = drawdown.min() * 100

fig.update_yaxes(
    title_text="DD %",
    range=[
        dd_min * 1.10,
        0
    ],
    dtick=0.5,
    row=2,
    col=1
)

fig.update_xaxes(
    showgrid=False
)

# ===============================
# PLOT
# ===============================

st.plotly_chart(
    fig,
    use_container_width=True
)

# ===============================
# ESTATÍSTICAS
# ===============================

col1, col2 = st.columns(2)

with col1:

    st.subheader("📊 Estatísticas")

    cor_pl = "#10b981" if pl > 0 else "#ef4444"

    st.markdown(
        f"**Unidades:** <span style='color:{cor_pl}'>{pl:.2f}</span>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"**Yield Médio:** {yield_medio*100:.2f}%"
    )

    st.markdown(
        f"**Desvio Padrão:** {dp:.2f}"
    )

    st.markdown(
        f"**Intervalo Confiança:** {erro:.2f}"
    )

    st.markdown(
        f"**Robustez:** {robustez:.2f}"
    )

    st.markdown(
        f"**Expectância:** {expectancy:.2f}"
    )

    st.markdown(
        f"**Profit Factor:** {profit_factor:.2f}"
    )
    
    st.markdown(
        f"**Controle(-)%:** {away_red_pct*100:.2f}%"
    )
    
    st.markdown(
        f"**Home Não Perde:** {home_not_lose*100:.2f}%"
    )
    
    st.markdown(
        f"**Ulcer Index:** {ulcer:.2f}"
    )

    st.markdown(
        f"**SQN:** {sqn:.2f}"
    )

    st.markdown(
        f"**Celeste:** {Celeste*100:.2f}%"
    )

    st.markdown(
        f"**Risco de Ruína:** {risk_ruin*100:.2f}%"
    )

    st.markdown(
        f"**Probabilidade de 5 Reds Seguidos:** {prob_5_losses*100:.2f}%"
    )

    st.markdown(
        f"**Score do Método:** {score:.2f}"
    )

# ===============================
# DIAGNÓSTICO
# ===============================

with col2:

    st.subheader("🛡 Diagnóstico")

    if erro < 0.05:
        st.success("Amostra Estatística Forte")
    elif erro < 0.1:
        st.info("Amostra Aceitável")
    else:
        st.warning("Amostra Pequena")

    if max_dd > -0.25:
        st.success("Drawdown Saudável")
    else:
        st.warning("Drawdown Elevado")

    if sqn > 3:
        st.success(
            "SQN Excelente — Sistema Profissional"
        )
    elif sqn > 2:
        st.info(
            "SQN bom — vantagem Consistente"
        )
    elif sqn > 1.6:
        st.warning("SQN Moderado")
    else:
        st.error("SQN Fraco")

    if profit_factor > 1.7:
        st.success("Profit Factor Excelente")
    elif profit_factor > 1.3:
        st.info("Profit Factor Saudável")
    else:
        st.warning("Profit Factor Baixo")

    if away_red_pct < 0.13:
        st.success("Controle(-)% Excelente")
    elif away_red_pct < 0.15:
        st.info("Controle(-)% Saudável")
    elif away_red_pct < 0.17:
        st.warning("Controle(-)% Atenção")
    else:
        st.error("Controle(-)% Crítico")
        
    if ulcer < 3:
        st.success("Ulcer Baixo — Saudável")
    elif ulcer < 5:
        st.info("Ulcer Controlado")
    elif ulcer < 8:
        st.warning("Ulcer Moderado")
    else:
        st.error("Ulcer Alto")

    if robustez < 0.2:
        st.warning(
            "Robustez Baixa — Stake Conservadora"
        )
    elif robustez < 0.4:
        st.info("Robustez Moderada")
    else:
        st.success("Robustez Forte")

st.divider()

# ===============================
# GAUGE
# ===============================

st.subheader("💀🎯☠️ Risco de Ruína")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=round(risk_ruin*100, 2),
    number={
        'suffix': "%",
        'valueformat': ".2f"
    },
    title={
        'text': "Probabilidade (%)"
    },
    gauge={
        'axis': {'range': [0, 100]},
        'steps': [
            {'range': [0, 3], 'color': '#10b981'},
            {'range': [3, 10], 'color': '#facc15'},
            {'range': [10, 25], 'color': '#fb923c'},
            {'range': [25, 100], 'color': '#ef4444'}
        ]
    }
))

st.plotly_chart(
    fig,
    use_container_width=True
)

# ===============================
# MONTE CARLO
# ===============================

st.subheader("📈 Simulação Monte Carlo")

simulacoes = 2000

trades = len(retornos_calc)

resultados = []

for _ in range(simulacoes):

    sim = np.random.choice(
        retornos_calc,
        size=trades,
        replace=True
    )

    resultados.append(
        sim.cumsum()[-1]
    )

fig = go.Figure()

fig.add_trace(go.Histogram(
    x=resultados,
    nbinsx=50
))

fig.update_layout(
    template="plotly_dark",
    title="Distribuição de Resultados Simulados"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ===============================
# SEMÁFORO
# ===============================

st.subheader("🚦 Semáforo do Método")

if (
    sqn > 2.5 and
    profit_factor > 1.5 and
    risk_ruin < 0.05
):

    st.success("🟢 MÉTODO PROFISSIONAL")

elif (
    sqn > 1.6 and
    profit_factor > 1.2
):

    st.warning("🟡 MÉTODO OPERÁVEL")

else:

    st.error("🔴 MÉTODO INSTÁVEL")

