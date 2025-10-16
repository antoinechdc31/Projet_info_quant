import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from Market import Market
from Option import Option
from Tree import Tree
from BlackScholes import black_scholes

st.set_page_config(page_title="🌳 Arbre Trinomial - Pricing d’Options", layout="wide")

st.title("🌲 Pricing d’options via Arbre Trinomial")

# === 1️⃣ Choix des dates ===
st.sidebar.header("🕓 Dates importantes")

calc_date = st.sidebar.date_input(
    "Date de calcul",
    value=datetime.today(),
    min_value=datetime(2000, 1, 1),
    max_value=datetime(2100, 1, 1)
)
calc_date = datetime.combine(calc_date, datetime.min.time())

maturity = st.sidebar.date_input(
    "Date de maturité",
    value=calc_date + timedelta(days=365),
    min_value=calc_date
)
maturity = datetime.combine(maturity, datetime.min.time())

# === 2️⃣ Paramètres de marché ===
st.sidebar.header("📊 Marché")
S0 = st.sidebar.number_input("Prix initial S₀", value=100.0, step=1.0)
r = st.sidebar.number_input("Taux sans risque r", value=0.05, step=0.01)
sigma = st.sidebar.number_input("Volatilité σ", value=0.3, step=0.01)

# === 3️⃣ Paramètres de l’option ===
st.sidebar.header("💼 Option")
K = st.sidebar.number_input("Strike K", value=100.0, step=1.0)
opt_type = st.sidebar.selectbox("Type d’option", ["call", "put"])
style = st.sidebar.selectbox("Style d’exercice", ["european", "american"])
N = st.sidebar.slider("Nombre d’étapes de l’arbre (N)", 10, 1000, 100)

# Calculs temporels
mat = (maturity - calc_date).days / 365
delta_t = mat / N

# === 4️⃣ Dividende ===
st.sidebar.header("💰 Dividende")
has_div = st.sidebar.checkbox("Inclure un dividende discret ?")

if has_div:
    div = st.sidebar.number_input("Montant du dividende", value=3.0)
    date_div = st.sidebar.date_input(
        "Date du dividende",
        value=calc_date + timedelta(days=int((maturity - calc_date).days * 0.6)),
        min_value=calc_date,
        max_value=maturity
    )
    date_div = datetime.combine(date_div, datetime.min.time())
else:
    div, date_div = 0, None

# === 5️⃣ Lancer le calcul ===
if st.button("🚀 Calculer le prix"):
    with st.spinner("Construction de l’arbre et calcul en cours..."):
        # Création des objets du modèle
        market = Market(S0=S0, r=r, sigma=sigma)
        tree = Tree(market, N=N, delta_t=delta_t)

        option = Option(
            K=K,
            mat=mat,
            opt_type=opt_type,
            style=style,
            isDiv=has_div,
            div=div,
            date_div=date_div,
            calc_date=calc_date
        )

        # Pricing via arbre trinomial
        prix_euro = tree.price_option_recursive(option)
        prix_back = tree.price_node_backward(option)

        # Comparaison avec Black-Scholes
        prix_bs = black_scholes(S0=S0, K=K, T=mat, r=r, sigma=sigma, type=opt_type)

    # === Résultats ===
    st.success(f"✅ **Prix de l’option (trinomial)** : {prix_euro:.6f}")
    st.write(f"🔁 Prix backward : {prix_back:.6f}")
    st.write(f"🧮 Prix Black–Scholes (sans div) : {prix_bs:.6f}")

    # Message de comparaison
    if has_div:
        st.info("💡 Le prix avec dividende doit être **plus faible** que le prix Black–Scholes, "
                "car le sous-jacent chute à la date du versement du dividende.")
    else:
        st.info("💡 En l’absence de dividende, le prix trinomial doit être proche du prix Black–Scholes.")

    # --- Grecques ---
    
    delta = tree.delta(option)
    gamma = tree.gamma(option)
    vega = tree.vega(option)
    volga = tree.volga(option)

    st.subheader("📈 Sensibilités (Grecques)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Δ (Delta)", f"{delta:.4f}")
    col2.metric("Γ (Gamma)", f"{gamma:.4f}")
    col3.metric("Vega", f"{vega:.4f}")
    col4.metric("Volga", f"{volga:.4f}")
    
    # --- Graphique de l’arbre ---
    st.subheader("🌳 Visualisation de l’arbre")
    show_values = st.toggle("Afficher les valeurs d’option (au lieu des sous-jacents)", value=False)
    try:
        tree.plot_tree(option=option, show_option_values=show_values, max_depth=8)
        st.pyplot(plt)
    except Exception:
        st.warning("⚠️ L’arbre n’a pas pu être affiché pour cette profondeur.")

    # --- Résumé final ---
    st.markdown("---")
    st.markdown(f"""
    ### 🧾 Récapitulatif du calcul
    - **Date de calcul :** {calc_date.strftime('%d/%m/%Y')}
    - **Maturité :** {maturity.strftime('%d/%m/%Y')} ({mat:.3f} an)
    - **Type :** {opt_type.upper()} {style.capitalize()}
    - **Strike :** {K}
    - **S₀ :** {S0}  •  **r :** {r}  •  **σ :** {sigma}
    - **Pas de temps Δt :** {delta_t:.5f}
    - **Étapes :** {N}
    - **Dividende :** {'Oui ('+str(div)+' le '+date_div.strftime('%d/%m/%Y')+')' if has_div else 'Aucun'}
    """)
else:
    st.info("🧮 Configure les paramètres dans la barre latérale puis clique sur **Calculer le prix**.")

