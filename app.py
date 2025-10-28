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
from Greek import (
    OptionDeltaTreeRecurs,
    OptionGammaTreeRecurs,
    OptionVegaTreeRecurs,
    OptionVommaTreeRecurs,
)
# ============ PAGE CONFIG ============
st.set_page_config(page_title="Arbre Trinomial avec prunning", layout="wide")

# ============ TITRE GLOBAL ============
st.title("Pricing d’Options avec prunning !!! ")
st.caption("Antoine CHANDECLERC et Lou GIRAULT")

# ============ PARAMÈTRES COMMUNS ============
with st.expander("Paramètres du modèle", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    S0 = col1.number_input("Prix initial S₀", value=100.0, step=1.0)
    K = col2.number_input("Strike K", value=100.0, step=1.0)
    r = col3.number_input("Taux sans risque r", value=0.05, step=0.01)
    sigma = col4.number_input("Volatilité σ", value=0.3, step=0.01)

    col5, col6, col7 = st.columns(3)
    opt_type = col5.selectbox("Type d’option", ["call", "put"])
    style = col6.selectbox("Style d’exercice", ["european", "american"])
    N = int(col7.number_input("Nombre d’étapes N", min_value=10, max_value=10000, value=200, step=10))

    col8, col9 = st.columns(2)
    calc_date = col8.date_input("Date de calcul", datetime.today())
    maturity = col9.date_input("Date de maturité", calc_date + timedelta(days=365))
    calc_date = datetime.combine(calc_date, datetime.min.time())
    maturity = datetime.combine(maturity, datetime.min.time())
    mat = (maturity - calc_date).days / 365
    delta_t = mat / N

    st.markdown("### Dividende")
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
tab1, tab2 = st.tabs(["Pricing", "Tree"])

# -------------------------------
# 💸 Onglet 1 : Pricing
# -------------------------------
with tab1:
    st.header("Pricing et Grecques")
    if st.button("Lancer le calcul du prix"):
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
        st.write(f"Temps de calcul : {runtime:.3f} s")

        col1, col2, col3 = st.columns(3)
        col1.metric("Prix Trinomial", f"{prix_tri:.4f}")
        col2.metric("Prix Backward", f"{prix_back:.4f}")
        col3.metric("Black–Scholes", f"{prix_bs:.4f}")

        delta = tree.delta(option)
        gamma = tree.gamma(option)
        vega = tree.vega(option)
        volga = tree.volga(option)
                
        delta_rec = OptionDeltaTreeRecurs(market, tree, option, 0.01)
        gamma_rec = OptionGammaTreeRecurs(market, tree, option, 0.01)
        vega_rec = OptionVegaTreeRecurs(market, tree, option, 0.01)
        volga_rec = OptionVommaTreeRecurs(market, tree, option, 0.01)


        st.subheader("Sensibilités (Grecques)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Δ Delta", f"{delta:.4f}")
        c2.metric("Γ Gamma", f"{gamma:.4f}")
        c3.metric("Vega", f"{vega:.4f}")
        c4.metric("Volga", f"{volga:.4f}")

        delta_bs, gamma_bs, vega_bs, volga_bs = black_scholes_greeks(S0, K, mat, r, sigma, opt_type)

        greeks_data = {
            "Grecque": ["Delta (Δ)", "Gamma (Γ)", "Vega", "Volga (Vomma)"],
            "Trinomial": [delta, gamma, vega, volga],
            "Greek.py (numérique)": [delta_rec, gamma_rec, vega_rec, volga_rec],
            "Black-Scholes": [delta_bs, gamma_bs, vega_bs, volga_bs],
            "Écart relatif (%)": [
                100 * abs((delta - delta_bs) / delta_bs) if delta_bs != 0 else 0,
                100 * abs((gamma - gamma_bs) / gamma_bs) if gamma_bs != 0 else 0,
                100 * abs((vega - vega_bs) / vega_bs) if vega_bs != 0 else 0,
                100 * abs((volga - volga_bs) / volga_bs) if volga_bs != 0 else 0,
            ],
        }

        df_greeks = pd.DataFrame(greeks_data)
        st.markdown("### Comparaison des Grecques — Trinomial vs Black-Scholes")
        st.dataframe(df_greeks.style.format({
            "Trinomial": "{:.6f}",
            "Greek.py (numérique)": "{:.6f}",
            "Black-Scholes": "{:.6f}",
            "Écart relatif (%)": "{:.2f}"
        }), use_container_width=True)

# -------------------------------
# 🌲 Onglet 2 : Visualisation de l’Arbre
# -------------------------------
# 🌲 Onglet : Arbre Trinomial graphique
with tab2:
    st.header("Visualisation graphique de l'arbre trinomial")

    max_cols = st.slider("Profondeur maximale à afficher :", 5, min(N, 40), 15)
    annotate = st.toggle("Afficher les valeurs des sous-jacents sur les nœuds", value=False)

    if st.button("Générer l'arbre graphique"):
        with st.spinner("Construction et affichage de l’arbre..."):
            market = Market(S0=S0, r=r, sigma=sigma)
            option = Option(K=K, mat=mat, opt_type=opt_type, style=style,
                            isDiv=has_div, div=div, date_div=date_div, calc_date=calc_date)
            tree = Tree(market, N=N, delta_t=delta_t)
            fig = tree.plot_trinomial_tree(option=option, max_cols=max_cols, annotate=annotate, show=False)
            st.pyplot(fig)
