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
# CARREGAMENTO HÍBRIDO
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

        st.warning("Nenhum arquivo encontrado")
        st.stop()

else:
    st.info("Carregue a Planilha para Iniciar a Análise.")
    st.stop()

if "ENTRADAS" not in df.columns:
    st.error("Coluna ENTRADAS não encontrada na planilha")
    st.stop()

retornos = pd.to_numeric(df["ENTRADAS"], errors="coerce").dropna()

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

# Robustez (ex-Sharpe)
robustez = roi / dp if dp != 0 else 0

# Expectância
expectancy = retornos.mean()

# SQN (System Quality Number)
sqn = (np.sqrt(volume) * expectancy / dp) if dp != 0 else 0

# Kelly (Celeste)
Celeste = roi / (dp ** 2) if dp != 0 else 0
stake = Celeste * 0.25

# Curva
equity = dados_plot.cumsum()

drawdown = equity - equity.cummax()
max_dd = drawdown.min()

# ===============================
# RISCO DE RUÍNA
# ===============================

banca = 0.5
risk_ruin = np.exp(-2 * roi * banca / (dp ** 2)) if dp != 0 else 1

# ===============================
# MÉTRICAS AVANÇADAS
# ===============================

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
        line=dict(width=3, color="#10b981")
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
        fill="tozeroy",
        line=dict(color="red")
    ))

    fig2.update_layout(
        template="plotly_dark",
        title="Drawdown",
        height=350
    )

    st.plotly_chart(fig2, use_container_width=True)
    
st.divider()
    
# ===============================
# ESTATÍSTICAS
# ===============================

col1, col2 = st.columns(2)

with col1:

    st.subheader("📊 Estatísticas")

    cor_pl = "#10b981" if pl > 0 else "#ef4444"
    cor_roi = "#10b981" if roi > 0 else "#ef4444"
    cor_dp = "#10b981"
    cor_ic = "#10b981" if erro < 0.1 else "#f59e0b"
    cor_celeste = "#38bdf8"
    cor_ruina = "#ef4444" if risk_ruin > 0.25 else "#f59e0b" if risk_ruin > 0.10 else "#10b981"

    st.markdown(f"**PL:** <span style='color:{cor_pl}'>{pl:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**ROI:** <span style='color:{cor_roi}'>{roi*100:.2f}%</span>", unsafe_allow_html=True)
    st.markdown(f"**Desvio padrão:** <span style='color:{cor_dp}'>{dp:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**Intervalo confiança:** <span style='color:{cor_ic}'>{erro:.2f}</span>", unsafe_allow_html=True)

    st.markdown(f"**Robustez:** {robustez:.2f}")
    st.markdown(f"**Expectância:** {expectancy:.2f}")
    st.markdown(f"**Profit Factor:** {profit_factor:.2f}")
    st.markdown(f"**Ulcer Index:** {ulcer:.2f}")
    st.markdown(f"**SQN:** {sqn:.2f}")

    st.markdown(f"**Celeste:** <span style='color:{cor_celeste}'>{Celeste*100:.2f}%</span>", unsafe_allow_html=True)
    st.markdown(f"**Risco de ruína:** <span style='color:{cor_ruina}'>{risk_ruin*100:.2f}%</span>", unsafe_allow_html=True)

    st.markdown(f"**Probabilidade de 5 reds seguidos:** {prob_5_losses*100:.2f}%")
    st.markdown(f"**Score do método:** {score:.2f}")
    
# ===============================
# DIAGNÓSTICO
# ===============================

with col2:

    st.subheader("🛡 Diagnóstico")

    # Amostra
    if erro < 0.05:
        st.success("Amostra estatística forte")
    elif erro < 0.1:
        st.info("Amostra aceitável")
    else:
        st.warning("Amostra pequena")

    # Drawdown
    if max_dd > -0.25:
        st.success("Drawdown saudável")
    else:
        st.warning("Drawdown elevado")

    # SQN
    if sqn > 3:
        st.success("SQN excelente — sistema profissional")
    elif sqn > 2:
        st.info("SQN bom — vantagem consistente")
    elif sqn > 1.6:
        st.warning("SQN moderado")
    else:
        st.error("SQN fraco")

    # Profit Factor
    if profit_factor > 1.7:
        st.success("Profit Factor excelente")
    elif profit_factor > 1.3:
        st.info("Profit Factor saudável")
    else:
        st.warning("Profit Factor baixo")

    # Ulcer
    if ulcer < 3:
        st.success("Ulcer Baixo — Saudável")
    elif ulcer < 5:
        st.info("Ulcer Controlado")
    elif ulcer < 8:
        st.warning("Ulcer Moderado")
    else:
        st.error("Ulcer Alto")

    # Robustez
    if robustez < 0.2:
        st.warning("Robustez Baixa — Stake Conservadora")
    elif robustez < 0.4:
        st.info("Robustez Moderada")
    else:
        st.success("Robustez Forte")
                
st.divider()

# ===============================
# GAUGE RISCO DE RUÍNA
# ===============================

st.subheader("🎯 Risco de Ruína")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=round(risk_ruin*100, 2),
    number={'suffix': "%", 'valueformat': ".2f"},
    title={'text': "Probabilidade (%)"},
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

st.plotly_chart(fig, use_container_width=True)

# ===============================
# MONTE CARLO
# ===============================

st.subheader("📈 Simulação Monte Carlo")

simulacoes = 500
trades = volume

resultados = []

for i in range(simulacoes):

    sim = np.random.choice(dados_plot, size=trades, replace=True)
    resultados.append(sim.cumsum()[-1])

fig = go.Figure()

fig.add_trace(go.Histogram(
    x=resultados,
    nbinsx=50
))

fig.update_layout(
    template="plotly_dark",
    title="Distribuição de Resultados Simulados"
)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# SEMÁFORO
# ===============================

st.subheader("🚦 Semáforo do Método")

if sqn > 2.5 and profit_factor > 1.5 and risk_ruin < 0.05:

    st.success("🟢 MÉTODO PROFISSIONAL")

elif sqn > 1.6 and profit_factor > 1.2:

    st.warning("🟡 MÉTODO OPERÁVEL")

else:

    st.error("🔴 MÉTODO INSTÁVEL")
