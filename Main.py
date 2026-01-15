from Market import Market
from Tree import Tree
from Node import Node
from BlackScholes import black_scholes
from Option import Option
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def comparaison_euro_amer(): # ici on verifie que l americain est + cher 
    # lorsque c'est call et r negatif
    market = Market(S0=50, r = 0.7, sigma=0.8)
    tree = Tree(market, N=100, delta_t=3/100)
    option = Option(K=60, mat=3, opt_type="put", style="european")

    prix_euro = tree.price_option_recursive(option)

    option = Option(K=60, mat=3, opt_type="put", style="american")

    prix_amer = tree.price_option_recursive(option)

    market = Market(S0=50, r=0.05, sigma=0.8)
    tree = Tree(market, N=100, delta_t=3/100)
    option = Option(K=60, mat=3, opt_type="put", style="european")
    print(tree.price_option_recursive(option))
    option = Option(K=60, mat=3, opt_type="put", style="american")
    print(tree.price_option_recursive(option))


    print("Prix euro =", prix_euro)
    print("Prix americain =", prix_amer)


def test_avec_div2():
    # --- Dates importantes ---
    calc_date = datetime(2025, 9, 1)
    maturity = datetime(2026, 9, 1)
    date_div = datetime(2026, 4, 21)

    # --- Discrétisation temporelle ---
    n = 400
    mat = (maturity - calc_date).days / 365  # maturité en années (≈ 1.00)
    deltat = mat / n                         # pas de temps

    # --- Paramètres du marché ---
    market = Market(S0=100, r=0.05, sigma=0.9)
    tree = Tree(market, N=n, delta_t=deltat)

    # --- Option avec dividende discret ---
    option = Option(
        K=102,
        mat=mat,     # ✅ utiliser la vraie maturité
        opt_type="call",
        style="european",
        isDiv=True,
        div=3,
        date_div=date_div,
        calc_date=calc_date       # utile si ton modèle l’utilise
    )

    # --- Pricing ---
    tree.tree_construction2(option)
    prix_euro = tree.price_option_recursive(option)
    prix_back = tree.price_node_backward(option)
    # tree.plot_tree(max_levels=40)
    prix_bs = black_scholes(S0=100, K=102, T=mat, r=0.05, sigma=0.3, type="call")

    print("\n===== Test avec dividende discret =====")
    print("---------------------------------------")
    print(f"Prix via arbre trinomial (avec div) : {prix_euro:.6f}")
    print(f"Prix backward (avec div)            : {prix_back:.6f}")
    print(f"Prix Black-Scholes (sans div)       : {prix_bs:.6f}")
    print("---------------------------------------")

def test_greeks_with_div() :
    market = Market(S0=70, r=0.01, sigma=0.2)
    tree = Tree(market, N=100, delta_t=1/100)
    date_div = datetime(2025, 12, 9)

    option = Option(
        K=60,
        mat=1,
        opt_type="call",
        style="european",
        isDiv=True,
        div=0,
        date_div=date_div
    )

    greeks = tree.compute_greeks(option)
    print("\n=== Grecques avec dividende discret ===")
    for k, v in greeks.items():
        print(f"{k:<8s} : {v:.6f}")

if __name__ == "__main__":
    test_avec_div2()
