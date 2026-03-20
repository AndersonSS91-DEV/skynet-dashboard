
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
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

import os

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

st.markdown("""
<style>
.titulo-principal {
    font-size: 26px;
    font-weight: 600;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo-principal">📊 Validação do Método</div>', unsafe_allow_html=True)

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

# ===============================
# CURVA DA BANCA (GLOW AZUL)
# ===============================

with g1:

    fig = go.Figure()

    # glow externo
    fig.add_trace(go.Scatter(
        y=equity,
        mode="lines",
        line=dict(width=10, color="rgba(0,150,255,0.15)"),
        hoverinfo="skip",
        showlegend=False
    ))

    # glow médio
    fig.add_trace(go.Scatter(
        y=equity,
        mode="lines",
        line=dict(width=6, color="rgba(0,150,255,0.35)"),
        hoverinfo="skip",
        showlegend=False
    ))

    # linha principal
    fig.add_trace(go.Scatter(
        y=equity,
        mode="lines",
        line=dict(width=2, color="#38bdf8"),
        name="Equity"
    ))

    fig.update_layout(
        template="plotly_dark",
        title="Curva da banca",
        height=350,
        margin=dict(l=20,r=20,t=40,b=20),
        yaxis=dict(
            range=[equity.min()*1.1, equity.max()*1.1],
            showgrid=True,
            gridcolor="rgba(255,255,255,0.1)"
        ),
        xaxis=dict(showgrid=False)
    )

    st.plotly_chart(fig, use_container_width=True)

# ===============================
# DRAWDOWN (GLOW VERMELHO)
# ===============================

with g2:

    fig2 = go.Figure()

    # glow externo
    fig2.add_trace(go.Scatter(
        y=drawdown,
        mode="lines",
        line=dict(width=10, color="rgba(255,0,0,0.15)"),
        hoverinfo="skip",
        showlegend=False
    ))

    # glow médio
    fig2.add_trace(go.Scatter(
        y=drawdown,
        mode="lines",
        line=dict(width=6, color="rgba(255,0,0,0.35)"),
        hoverinfo="skip",
        showlegend=False
    ))

    # linha principal
    fig2.add_trace(go.Scatter(
        y=drawdown,
        mode="lines",
        line=dict(width=2, color="#ef4444"),
        fill="tozeroy",
        name="Drawdown"
    ))

    fig2.update_layout(
        template="plotly_dark",
        title="Drawdown",
        height=350,
        margin=dict(l=20,r=20,t=40,b=20),
        yaxis=dict(
            range=[drawdown.min()*1.1, 0],
            showgrid=True,
            gridcolor="rgba(255,255,255,0.1)"
        ),
        xaxis=dict(showgrid=False)
    )

    st.plotly_chart(fig2, use_container_width=True)
    
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

    st.markdown(f"**P/L:** <span style='color:{cor_pl}'>{pl:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**ROI:** <span style='color:{cor_roi}'>{roi*100:.2f}%</span>", unsafe_allow_html=True)
    st.markdown(f"**Desvio Padrão:** <span style='color:{cor_dp}'>{dp:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**Intervalo Confiança:** <span style='color:{cor_ic}'>{erro:.2f}</span>", unsafe_allow_html=True)

    st.markdown(f"**Robustez:** {robustez:.2f}")
    st.markdown(f"**Expectância:** {expectancy:.2f}")
    st.markdown(f"**Profit Factor:** {profit_factor:.2f}")
    st.markdown(f"**Ulcer Index:** {ulcer:.2f}")
    st.markdown(f"**SQN:** {sqn:.2f}")

    st.markdown(f"**Celeste:** <span style='color:{cor_celeste}'>{Celeste*100:.2f}%</span>", unsafe_allow_html=True)
    st.markdown(f"**Risco de Ruína:** <span style='color:{cor_ruina}'>{risk_ruin*100:.2f}%</span>", unsafe_allow_html=True)

    st.markdown(f"**Probabilidade de 5 Reds Seguidos:** {prob_5_losses*100:.2f}%")
    st.markdown(f"**Score do Método:** {score:.2f}")
    
# ===============================
# DIAGNÓSTICO
# ===============================

with col2:

    st.subheader("🛡 Diagnóstico")

    # Amostra
    if erro < 0.05:
        st.success("Amostra Estatística Forte")
    elif erro < 0.1:
        st.info("Amostra Aceitável")
    else:
        st.warning("Amostra Pequena")

    # Drawdown
    if max_dd > -0.25:
        st.success("Drawdown Saudável")
    else:
        st.warning("Drawdown Elevado")

    # SQN
    if sqn > 3:
        st.success("SQN Excelente — Sistema Profissional")
    elif sqn > 2:
        st.info("SQN bom — vantagem Consistente")
    elif sqn > 1.6:
        st.warning("SQN Moderado")
    else:
        st.error("SQN Fraco")

    # Profit Factor
    if profit_factor > 1.7:
        st.success("Profit Factor Excelente")
    elif profit_factor > 1.3:
        st.info("Profit Factor Saudável")
    else:
        st.warning("Profit Factor Baixo")

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

st.subheader("💀🎯☠️ Risco de Ruína de 50%")

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

# ===============================
# MONTE CARLO LIMPO (SEM CAP)
# ===============================

st.subheader("🏦 Simulação Institucional (1000 trades)")

simulacoes = 2000
trades_simulados = 1000

stake_pct = stake
banca_inicial = 1000

ret_array = retornos.values

resultados_finais = []
curvas = []
ruina_count = 0

for _ in range(simulacoes):

    banca = banca_inicial
    seq = ret_array[np.random.randint(0, len(ret_array), size=trades_simulados)]

    curva = []

    for r in seq:

        banca += banca * stake_pct * r

        if banca <= banca_inicial * 0.1:
            ruina_count += 1
            break

        if len(curvas) < 150:
            curva.append(banca)

    resultados_finais.append(banca)

    if len(curvas) < 150:
        curvas.append(curva)

# ===============================
# ESTATÍSTICAS
# ===============================

resultados_finais = np.array(resultados_finais)

p10 = np.percentile(resultados_finais, 10)
p50 = np.percentile(resultados_finais, 50)
p90 = np.percentile(resultados_finais, 90)

prob_ruina = ruina_count / simulacoes

# ===============================
# CARDS
# ===============================

c1, c2, c3, c4 = st.columns(4)

c1.metric("P10 (pior cenário)", f"R$ {p10:,.0f}")
c2.metric("Mediana (P50)", f"R$ {p50:,.0f}")
c3.metric("P90 (top cenário)", f"R$ {p90:,.0f}")
c4.metric("Prob. Ruína", f"{prob_ruina*100:.1f}%")

# ===============================
# HISTOGRAMA (TRATADO)
# ===============================

# remove só os absurdos extremos (sem distorcer tudo)
limite = np.percentile(resultados_finais, 99.5)
dados_plot = resultados_finais[resultados_finais <= limite]

fig = go.Figure()

fig.add_trace(go.Histogram(
    x=dados_plot,
    nbinsx=50
))

fig.update_layout(
    template="plotly_dark",
    title="Distribuição da Banca Final"
)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# CURVAS
# ===============================

fig_curvas = go.Figure()

for curva in curvas:
    fig_curvas.add_trace(go.Scatter(
        y=curva,
        mode="lines",
        line=dict(width=1),
        opacity=0.2,
        showlegend=False
    ))

fig_curvas.update_layout(
    template="plotly_dark",
    title="Curvas Simuladas"
)

st.plotly_chart(fig_curvas, use_container_width=True)

st.plotly_chart(fig_curvas, use_container_width=True)
