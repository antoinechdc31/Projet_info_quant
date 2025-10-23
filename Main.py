from Market import Market
from Tree import Tree
from Node import Node
from BlackScholes import black_scholes
from Option import Option
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from dateutil.relativedelta import relativedelta
from OneDimDerivative import OneDimDerivative
from OptionPricingParam import OptionPricingParam
from Greek import  OptionDeltaTreeRecurs, OptionGammaTreeRecurs, OptionVegaTreeRecurs,OptionVommaTreeRecurs



def test_node_prices():
    market = Market(S0=100, r=0.03, sigma=0.2)
    tree = Tree(market, N = 1, delta_t= 1) 
    node = Node(100, tree)

    Smid, Sup, Sdown = node.next
    Pmid, Pup, Pdown = node.proba
    print("Sous-jacent actuel :", node.underlying)
    print("Smid :", round(Smid, 4))
    print("Sup  :", round(Sup, 4))
    print("Sdown:", round(Sdown, 4))
    print(node.forward())
    print(node.variance())
    print("Smid :", round(Pmid, 4))
    print("Sup  :", round(Pup, 4))
    print("Sdown:", round(Pdown, 4))


def test_tree():
    market = Market(S0 = 100, r = 0.03, sigma = 0.2)
    tree = Tree(market, N = 2, delta_t = 1/2)
    option = Option(K = 80, mat = 2, opt_type = "call", style = "european")
    tree.print_tree()
    tree.price_option(option)
    print(black_scholes(S0 = 100, K = 80, T = 1, r = 0.03, sigma = 0.2, type = "call"))

def test_tree_2() :
        
    # Paramètres de marché et d'arbre
    market = Market(S0=100, r=0.03, sigma=0.2)
    tree = Tree(market, N=1, delta_t=1/1)
    
    option = Option(K=100, mat=1, opt_type="call", style="european")

    prix = tree.price_option_recursive(option)
    print("Prix trinomial (recursive) =", prix)

    pass

def test_tree_n_grand() :
    market = Market(S0 = 100, r = 0.03, sigma = 0.2)
    tree = Tree(market, N=100, delta_t=1/100)
    option = Option(K=80, mat=1, opt_type="call", style="european")
    price = tree.price_option(option)
    print("Trinomial =", price)
    print("Black-Scholes =", black_scholes(S0=100, K=80, T=1, r=0.03, sigma=0.2, type="call"))


def test_tree_american() :
    market = Market(S0 = 100, r = -0.3, sigma = 0.2)
    tree = Tree(market, N=100, delta_t=1/100)
    option = Option(K=80, mat=1, opt_type="call", style="american")
    price1 = tree.price_option(option)

    market = Market(S0 = 100, r = -0.3, sigma = 0.2)
    tree = Tree(market, N=100, delta_t=1/100)
    option = Option(K=80, mat=1, opt_type="call", style="european")
    price2 = tree.price_option(option)

    print(price1, price2)

def test_tree_2_bs() :
    # Paramètres de marché et d'arbre
    market = Market(S0=100, r=0.03, sigma=0.2)
    tree = Tree(market, N=100, delta_t=1/100)
    option = Option(K=100, mat=1, opt_type="call", style="european")
    start = time.time()  
    prix_tree = tree.price_option_recursive(option)
    end = time.time()
    start_2 = time.time()
    price = tree.price_option(option)
    end_2 = time.time()
    prix_bs = black_scholes(S0=100, K=100, T=1, r=0.03, sigma=0.2, type="call")
    print("Prix trinomial (recursive) =", prix_tree)
    print("Prix Black–Scholes        =", prix_bs)
    print("Temps calcul trinomial (recursive) =", end - start)
    print("Temps calcul arbre trinomial =",end_2 - start_2)

def benchmark_tree_times():
    # Plus de points : entre 10 et 1000
    Ns = np.unique(np.logspace(1, 3, num=15, dtype=int))
    times_recursive = []
    times_iterative = []

    for N in Ns:
        market = Market(S0=100, r=0.03, sigma=0.2)
        tree = Tree(market, N=N, delta_t=1/N)
        option = Option(K=100, mat=1, opt_type="call", style="european")

        # Recursive method
        start = time.time()
        _ = tree.price_option_recursive(option)
        end = time.time()
        times_recursive.append(end - start)

        # Iterative method
        start = time.time()
        _ = tree.price_option(option)
        end = time.time()
        times_iterative.append(end - start)

    # Conversion log-log pour régression
    logN = np.log(Ns)
    logT_rec = np.log(times_recursive)
    logT_iter = np.log(times_iterative)

    # Régression linéaire (moindre carrés)
    slope_rec, intercept_rec = np.polyfit(logN, logT_rec, 1)
    slope_iter, intercept_iter = np.polyfit(logN, logT_iter, 1)

    # Plot log-log
    plt.figure(figsize=(8,5))
    plt.loglog(Ns, times_recursive, marker='o', label=f"Recursive (pente ~ {slope_rec:.2f})")
    plt.loglog(Ns, times_iterative, marker='o', label=f"Iterative (pente ~ {slope_iter:.2f})")
    plt.xlabel("Timesteps (N)")
    plt.ylabel("Temps de calcul (secondes)")
    plt.title("Comparaison des vitesses de calcul des arbres (log-log)")
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.show()

    print(f"Pente (complexité) - Recursive : {slope_rec:.2f}")
    print(f"Pente (complexité) - Iterative : {slope_iter:.2f}")


def convergence_recursive():
    Ns = [5, 10, 20, 50, 100, 200, 400, 500, 700, 900,1000]  # timesteps testés
    errors = []

    # Prix de référence Black-Scholes
    prix_bs = black_scholes(S0=100, K=100, T=1, r=0.03, sigma=0.2, type="call")

    for N in Ns:
        market = Market(S0=100, r=0.03, sigma=0.2)
        tree = Tree(market, N=N, delta_t=1/N)
        option = Option(K=100, mat=1, opt_type="call", style="european")

        prix_tree = tree.price_option_recursive(option)

        # erreur absolue
        err = abs(prix_tree - prix_bs)
        errors.append(err)

    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(Ns, errors, marker='o', label="Erreur |Prix_tree - Prix_BS|")
    plt.xlabel("Timesteps (N)")
    plt.ylabel("Erreur absolue")
    plt.title("Convergence de la méthode récursive vers Black–Scholes")
    plt.yscale("log")  # échelle log pour mieux voir la décroissance
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.show()

def compare_tree_bs_vs_strike():
    # --- Paramètres de base ---
    Ks = np.linspace(69, 109, 89)  # strikes testés
    prix_tree, prix_bs, diffs = [], [], []

    # Paramètres du marché
    market = Market(S0=100, r=0.03, sigma=0.2)
    maturity = 1.0  # 1 an
    N = 400
    dt = maturity / N

    # Template option
    option_template = {"mat": maturity, "opt_type": "call", "style": "european"}

    # --- Calcul des prix ---
    for K in Ks:
        tree = Tree(market, N=N, delta_t=dt)
        option = Option(K=K, **option_template)

        # Prix arbre trinomial
        p_tree = tree.price_node_backward(option)

        # Prix Black–Scholes
        p_bs = black_scholes(S0=market.S0, K=K, T=maturity, r=market.r, sigma=market.sigma, type="call")

        prix_tree.append(p_tree)
        prix_bs.append(p_bs)
        diffs.append(p_tree - p_bs)

    prix_tree = np.array(prix_tree)
    prix_bs = np.array(prix_bs)
    diffs = np.array(diffs)

    # --- Pentes (approximations numériques de ∂Prix/∂K) ---
    slope_tree = np.gradient(prix_tree, Ks)
    slope_bs = np.gradient(prix_bs, Ks)

    # === GRAPHIQUE 1 : Prix et pentes ===
    fig, ax1 = plt.subplots(figsize=(9,6))
    ax1.set_title("Tree and Black–Scholes prices as functions of the strike")
    ax1.set_xlabel("Strike K")
    ax1.set_ylabel("Option Price")

    ax1.plot(Ks, prix_bs, color="green", lw=2, label="BS")
    ax1.plot(Ks, prix_tree, color="gold", lw=2, label="Tree")

    # Second axe : différence Tree - BS
    # ax2 = ax1.twinx()
    # ax2.plot(Ks, diffs, color="red", lw=2, label="Tree - BS ->")
    # ax2.set_ylabel("Tree - BS")

    # Ajouter les pentes
    ax1.plot(Ks, slope_bs, "g--", label="Slope BS ->")
    ax1.plot(Ks, slope_tree, "y--", label="Slope Tree ->")

    # Grilles et légendes
    ax1.grid(True, ls="--", alpha=0.6)
    ax1.legend(loc="upper left")
    #ax2.legend(loc="upper right")

    plt.tight_layout()
    plt.show()

    # === GRAPHIQUE 2 : Écart Tree - BS ===
    plt.figure(figsize=(8,5))
    plt.plot(Ks, diffs, color="red", label="Tree - BS")
    plt.axhline(0, color="black", ls="--", lw=1)
    plt.xlabel("Strike K")
    plt.ylabel("Écart de prix")
    plt.title("Écart entre le modèle Trinomial et Black–Scholes")
    plt.grid(True, ls="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def test_avec_div2():
    # --- Dates importantes ---
    calc_date = datetime(2025, 9, 1)
    maturity = datetime(2026, 9, 1)
    date_div = datetime(2026, 4, 21)

    # --- Discrétisation temporelle ---
    n = 980
    mat = (maturity - calc_date).days / 365  # maturité en années (≈ 1.00)
    deltat = mat / n                         # pas de temps

    # --- Paramètres du marché ---
    market = Market(S0=100, r=0.05, sigma=0.3)
    tree = Tree(market, N=n, delta_t=deltat)

    # --- Option avec dividende discret ---
    option = Option(
        K=102,
        mat=mat,     # ✅ utiliser la vraie maturité
        opt_type="call",
        style="european",
        isDiv=True,
        div=0,
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
    print(f"Date de calcul : {calc_date.strftime('%Y-%m-%d')}")
    print(f"Date du dividende : {date_div.strftime('%Y-%m-%d')}")
    print(f"Maturité : {maturity.strftime('%Y-%m-%d')} ({mat:.4f} an)")
    print("---------------------------------------")
    print(f"Prix via arbre trinomial (avec div) : {prix_euro:.6f}")
    print(f"Prix backward (avec div)            : {prix_back:.6f}")
    print(f"Prix Black-Scholes (sans div)       : {prix_bs:.6f}")
    print("---------------------------------------")
    print("→ Le prix avec dividende doit être PLUS FAIBLE\n"
          "  car le sous-jacent chute à la date de versement du dividende.")
    
    #dS = OneDimDerivative(_PriceTreeBackward_S0, OptionPricingParam(market, tree, option), shift=0.01*market.S0)
    #dsigma = OneDimDerivative(_PriceTreeBackward_sigma, OptionPricingParam(market, tree, option), shift=0.01*market.sigma)
    delta = OptionDeltaTreeRecurs(market,tree,option,0.01)
    gamma = OptionGammaTreeRecurs(market,tree,option,0.01)
    vega = OptionVegaTreeRecurs(market,tree,option,0.01)
    vomma = OptionVommaTreeRecurs(market,tree,option,0.01)
    
    print(f"Vrai Delta = {delta}")
    print(f"Vrai Gamma = {gamma}")
    print(f"Vrai Vega = {vega}")
    print(f"Vrai Vomma = {vomma}")
    #print(f"Delta = {dS.first(market.S0):.6f}")
    #print(f"Gamma = {dS.second(market.S0):.6f}")
    #print(f"Vega  = {dsigma.first(market.sigma):.6f}")
    #print(f"Vomma = {dsigma.second(market.sigma):.6f}")


def plot_gamma_vs_shift():
     # --- Dates importantes ---
    calc_date = datetime(2025, 9, 1)
    maturity = datetime(2026, 9, 1)
    date_div = datetime(2026, 4, 21)

    # --- Discrétisation temporelle ---
    n = 600
    mat = (maturity - calc_date).days / 365  # maturité en années (≈ 1.00)
    deltat = mat / n                         # pas de temps

    # --- Paramètres du marché ---
    market = Market(S0=100, r=0.05, sigma=0.3)
    tree = Tree(market, N=n, delta_t=deltat)

    # --- Option avec dividende discret ---
    option = Option(
        K=102,
        mat=mat,     # ✅ utiliser la vraie maturité
        opt_type="call",
        style="european",
        isDiv=True,
        div=0,
        date_div=date_div,
        calc_date=calc_date       # utile si ton modèle l’utilise
    )
    shifts = np.logspace(-7, 1, 20)  # de 0.001 à 1
    gammas = []

    for h in shifts:
        g = tree.gamma(option,h)
        gammas.append(g)

    plt.figure(figsize=(8,5))
    plt.plot(shifts, gammas, marker='o')
    plt.xscale('log')
    plt.title("Sensibilité du Gamma par rapport au shift h")
    plt.xlabel("Shift (h)")
    plt.ylabel("Gamma estimé")
    plt.grid(True, which="both", ls="--")
    plt.show()

def benchmark_recursive_vs_backward():
    # --- Paramètres constants ---
    S0, K, r, sigma = 100, 102, 0.05, 0.3
    calc_date = datetime(2025, 9, 1)
    maturity = datetime(2026, 9, 1)
    mat = (maturity - calc_date).days / 365

    market = Market(S0=S0, r=r, sigma=sigma)
    option = Option(K=K, mat=mat, opt_type="call", style="european")

    # --- Liste de valeurs de N ---
    N_values = [10, 25, 50, 100, 200, 400,500,600,700,800,900,1000]
    times_recursive = []
    times_backward = []

    for N in N_values:
        delta_t = mat / N
        tree = Tree(market, N=N, delta_t=delta_t)

        # Test récursif
        t1 = time.time()
        tree = Tree(market, N=N, delta_t=delta_t)
        tree.tree_construction2(option)
        tree.price_option_recursive(option)
        t2 = time.time()
        times_recursive.append(t2 - t1)

        # Test backward
        t3 = time.time()
        tree = Tree(market, N=N, delta_t=delta_t)
        tree.tree_construction2(option)
        tree.price_node_backward(option)
        t4 = time.time()
        times_backward.append(t4 - t3)

        print(f"N={N:3d} → Recursive={times_recursive[-1]:.4f}s, Backward={times_backward[-1]:.4f}s")

    # --- Plot ---
    plt.figure(figsize=(8,5))
    plt.plot(N_values, times_recursive, marker='o', label='Récursif')
    plt.plot(N_values, times_backward, marker='s', label='Backward')
    plt.xlabel("Nombre d’étapes N")
    plt.ylabel("Temps de calcul (s)")
    plt.title("Comparaison du temps de calcul : Recursive vs Backward")
    plt.legend()
    plt.grid(True, ls='--', alpha=0.6)
    plt.show()

if __name__ == "__main__":
    test_avec_div2() 
    #convergence_recursive() #=> Convergence de l'arbre récursif vers black scholes
    #compare_tree_bs_vs_strike() #=> Comparaison des prix en fonction du strike
    #test_plot_tree()
    #plot_trinomial_tree(S0=100, r=0.1, sigma=0.2,N=60, delta_t=1/60,K=80, mat=1, opt_type="call", style="european",isDiv=True, div=6, date_div=datetime(2025, 12, 9),max_cols=100, annotate=False)
    #plot_gamma_vs_shift()
    #benchmark_recursive_vs_backward() => Comparaison des temps de calcul entre les deux méthodes



#si on demande le vega on doit trouver la variation de prix pour 1%
#sur le papier => regularite quand on bouge S0 => est ce que le gamma saute
#question delta hedge 
#savoir comment on se hedge avec le vega (nb d'action)
#l'erreur sur le prix decroit en 1/pas de temps
