# =====================================================
# TRADING TOOLS (SEM ALTERAR O DASHBOARD)
# =====================================================

with tab_calc:

    st.session_state["_current_tab"] = "Calculadora"

    st.markdown("### Cashout / Greenbook")

    col1, col2, col3 = st.columns(3)

    back_odd = col1.number_input("Back Odd", value=1.80, key="tt_back_odd")
    back_stake = col2.number_input("Stake", value=100.0, key="tt_back_stake")
    lay_odd = col3.number_input("Lay Odd", value=2.00, key="tt_lay_odd")

    lay_stake = (back_odd * back_stake) / lay_odd
    lucro_loss = lay_stake - back_stake

    c4, c5 = st.columns(2)
    c4.metric("Stake Lay", f"{lay_stake:.2f}")
    c5.metric("Green", f"{lucro_loss:.2f}")

    st.markdown("---")
    st.markdown("### Dutching")

    n = st.slider("Número de seleções", 2, 6, 3, key="tt_n")

    odds = []
    for i in range(n):
        odds.append(
            st.number_input(f"Odd {i+1}", value=2.0, key=f"tt_odd_{i}")
        )

    stake_total = st.number_input("Stake total", value=100.0, key="tt_stake_total")

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

    odd = c1.number_input("Odd mercado", value=2.0, key="tt_vb_odd")
    prob_modelo = c2.number_input("Probabilidade modelo (%)", value=55.0, key="tt_vb_prob")

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

    banca = st.number_input("Banca inicial", value=1000.0, key="tt_banca")
    roi = st.slider("ROI médio (%)", 0.5, 10.0, 3.0, key="tt_roi")
    trades = st.slider("Trades", 10, 500, 100, key="tt_trades")

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
        height=300,
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)
