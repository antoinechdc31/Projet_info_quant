import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from Market import Market
from Option import Option
from Tree import Tree
import pandas as pd
from BlackScholes import black_scholes
import time
from BlackScholes import black_scholes_greeks

# ============ PAGE CONFIG ============
st.set_page_config(page_title="🌲 Arbre Trinomial avec prunning", layout="wide")

# ============ TITRE GLOBAL ============
st.title("🌳 Pricing d’Options avec prunning !!! ")
st.caption("Interface à onglets — claire, moderne et structurée 🧭")

# ============ PARAMÈTRES COMMUNS ============
with st.expander("⚙️ Paramètres du modèle", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    S0 = col1.number_input("Prix initial S₀", value=100.0, step=1.0)
    K = col2.number_input("Strike K", value=100.0, step=1.0)
    r = col3.number_input("Taux sans risque r", value=0.05, step=0.01)
    sigma = col4.number_input("Volatilité σ", value=0.3, step=0.01)

    col5, col6, col7 = st.columns(3)
    opt_type = col5.selectbox("Type d’option", ["call", "put"])
    style = col6.selectbox("Style d’exercice", ["european", "american"])
    N = int(col7.number_input("Nombre d’étapes N", min_value=10, max_value=1000, value=200, step=10))

    col8, col9 = st.columns(2)
    calc_date = col8.date_input("Date de calcul", datetime.today())
    maturity = col9.date_input("Date de maturité", calc_date + timedelta(days=365))
    calc_date = datetime.combine(calc_date, datetime.min.time())
    maturity = datetime.combine(maturity, datetime.min.time())
    mat = (maturity - calc_date).days / 365
    delta_t = mat / N

    st.markdown("### 💰 Dividende")
    has_div = st.checkbox("Inclure un dividende discret ?")
    if has_div:
        col1, col2 = st.columns(2)
        div = col1.number_input("Montant du dividende", value=3.0)
        date_div = col2.date_input(
            "Date du dividende",
            calc_date + timedelta(days=int((maturity - calc_date).days * 0.6))
        )
        date_div = datetime.combine(date_div, datetime.min.time())
    else:
        div, date_div = 0, None

# ============ ONGLETS ============
tab1, tab2, tab3, tab4 = st.tabs(["💸 Pricing", "🌲 Tree", "📈 Convergence", "⚙️ Runtime"])

# -------------------------------
# 💸 Onglet 1 : Pricing
# -------------------------------
with tab1:
    st.header("💰 Pricing et Grecques")
    if st.button("🚀 Lancer le calcul du prix"):
        with st.spinner("Construction de l’arbre et calcul..."):
            t0 = time.time()
            market = Market(S0=S0, r=r, sigma=sigma)
            tree = Tree(market, N=N, delta_t=delta_t)
            option = Option(K=K, mat=mat, opt_type=opt_type, style=style,
                            isDiv=has_div, div=div, date_div=date_div, calc_date=calc_date)
            tree.tree_construction2(option)
            prix_tri = tree.price_option_recursive(option)
            prix_back = tree.price_node_backward(option)
            prix_bs = black_scholes(S0=S0, K=K, T=mat, r=r, sigma=sigma, type=opt_type)
            runtime = time.time() - t0

        st.success(f"**Prix Trinomial :** {prix_tri:.6f}")
        st.write(f"⏱ Temps de calcul : {runtime:.3f} s")

        col1, col2, col3 = st.columns(3)
        col1.metric("Prix Trinomial", f"{prix_tri:.4f}")
        col2.metric("Prix Backward", f"{prix_back:.4f}")
        col3.metric("Black–Scholes", f"{prix_bs:.4f}")

        delta = tree.delta(option)
        gamma = tree.gamma(option)
        vega = tree.vega(option)
        volga = tree.volga(option)

        st.subheader("📈 Sensibilités (Grecques)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Δ Delta", f"{delta:.4f}")
        c2.metric("Γ Gamma", f"{gamma:.4f}")
        c3.metric("Vega", f"{vega:.4f}")
        c4.metric("Volga", f"{volga:.4f}")

        delta_bs, gamma_bs, vega_bs, volga_bs = black_scholes_greeks(S0, K, mat, r, sigma, opt_type)

        greeks_data = {
            "Grecque": ["Delta (Δ)", "Gamma (Γ)", "Vega", "Volga (Vomma)"],
            "Trinomial": [delta, gamma, vega, volga],
            "Black-Scholes": [delta_bs, gamma_bs, vega_bs, volga_bs],
            "Écart relatif (%)": [
                100 * abs((delta - delta_bs) / delta_bs) if delta_bs != 0 else 0,
                100 * abs((gamma - gamma_bs) / gamma_bs) if gamma_bs != 0 else 0,
                100 * abs((vega - vega_bs) / vega_bs) if vega_bs != 0 else 0,
                100 * abs((volga - volga_bs) / volga_bs) if volga_bs != 0 else 0,
            ],
        }

        df_greeks = pd.DataFrame(greeks_data)
        st.markdown("### ⚖️ Comparaison des Grecques — Trinomial vs Black-Scholes")
        st.dataframe(df_greeks.style.format({
            "Trinomial": "{:.6f}",
            "Black-Scholes": "{:.6f}",
            "Écart relatif (%)": "{:.2f}"
        }), use_container_width=True)

# -------------------------------
# 🌲 Onglet 2 : Visualisation de l’Arbre
# -------------------------------
with tab2:
    st.header("🌲 Visualisation de l’Arbre Trinomial")
    show_values = st.toggle("Afficher les valeurs d’option au lieu des sous-jacents", value=False)
    max_depth = min(N, 40)
    if st.button("👁️ Afficher l’arbre (max 40 étapes)"):
        market = Market(S0=S0, r=r, sigma=sigma)
        tree = Tree(market, N=N, delta_t=delta_t)
        option = Option(K=K, mat=mat, opt_type=opt_type, style=style,
                        isDiv=has_div, div=div, date_div=date_div, calc_date=calc_date)
        tree.price_option_recursive(option)
        tree.plot_tree(option=option, show_option_values=show_values, max_depth=max_depth)
        st.pyplot(plt)

    st.markdown("#### 🎲 Probabilités locales (racine)")
    try:
        tree = Tree(Market(S0, r, sigma), N, delta_t)
        option = Option(K, mat, opt_type, style, has_div, div, date_div, calc_date)
        root = tree.root
        p_mid, p_up, p_down = root.calcul_proba()
        st.write(f"Pmid = {p_mid:.4f}, Pup = {p_up:.4f}, Pdown = {p_down:.4f}")
    except Exception:
        st.info("Probabilités non disponibles avant construction complète.")

# -------------------------------
# 📈 Onglet 3 : Convergence
# -------------------------------
with tab3:
    st.header("📈 Étude de convergence du modèle")
    st.write("On observe comment le prix se stabilise quand N augmente.")
    Ns = [10, 25, 50, 100, 200, 400]
    prices = []
    for n in Ns:
        tree = Tree(Market(S0, r, sigma), n, mat/n)
        option = Option(K, mat, opt_type, style, has_div, div, date_div, calc_date)
        prices.append(tree.price_option_recursive(option))
    fig, ax = plt.subplots()
    ax.plot(Ns, prices, marker="o")
    ax.set_xlabel("Nombre d’étapes N")
    ax.set_ylabel("Prix de l’option")
    ax.set_title("Convergence du prix avec N")
    st.pyplot(fig)

# -------------------------------
# ⚙️ Onglet 4 : Runtime
# -------------------------------
with tab4:
    st.header("⚙️ Temps d’exécution selon N")
    st.write("Évalue la complexité du modèle en fonction du nombre d’étapes.")
    Ns = [10, 50, 100, 200, 400]
    times = []
    for n in Ns:
        t0 = time.time()
        tree = Tree(Market(S0, r, sigma), n, mat/n)
        option = Option(K, mat, opt_type, style, has_div, div, date_div, calc_date)
        tree.price_option_recursive(option)
        times.append(time.time() - t0)
    fig, ax = plt.subplots()
    ax.plot(Ns, times, marker="o", color="crimson")
    ax.set_xlabel("Nombre d’étapes N")
    ax.set_ylabel("Temps (s)")
    ax.set_title("Runtime vs N")
    st.pyplot(fig)

    #dire tout ce qu'on a fait dans les 2 langages (surtout exntension ) + resultat => convergence...