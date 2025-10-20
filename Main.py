from Market import Market
from Tree import Tree
from Node import Node
from BlackScholes import black_scholes
from Option import Option
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

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
    tree = Tree(market, N=100, delta_t=1/100)
    
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
    market = Market(S0=50, r=0.01, sigma=0.8)
    tree = Tree(market, N=100, delta_t=3/100)
    option = Option(K=30, mat=3, opt_type="call", style="european")

    prix_tree = tree.price_option_recursive(option)
    prix_bs = black_scholes(S0=50, K=30, T=3, r=0.01, sigma=0.8, type="call")

    print("Prix trinomial (recursive) =", prix_tree)
    print("Prix Black–Scholes        =", prix_bs)

def test_diff_temps_calcul():
    market = Market(S0=100, r=0.03, sigma=0.2)
    tree = Tree(market, N=100, delta_t=1/100)
    option = Option(K=100, mat=1, opt_type="call", style="european")
        
    start = time.time()   # timestamp au début

    prix_tree = tree.price_option_recursive(option)

    end = time.time()     # timestamp à la fin
    elapsed1 = end - start

    start = time.time()

    price2 = tree.price_option(option)

    end = time.time()     # timestamp à la fin
    elapsed2 = end - start

    prix_bs = black_scholes(S0=100, K=100, T=1, r=0.03, sigma=0.2, type="call")

    print("Prix de l'arbre brique : ", prix_tree, " avec le tps ", elapsed1)
    print("Prix de l'arbre classique", price2, " avec le temps ", elapsed2 ) # on voit que l'arbre brique est plus court

def benchmark_tree(max_N=5000, step=100):
    market = Market(S0=100, r=0.03, sigma=0.2)
    option = Option(K=100, mat=1, opt_type="call", style="european")

    Ns = list(range(100, max_N+1, step))  # ex: [10, 20, 30, ..., 100]
    times_recursive = []
    times_classic = []

    for N in Ns:
        tree = Tree(market, N=N, delta_t=1/N)

        # Méthode récursive (arbre brique)
        start = time.perf_counter()
        tree.price_option_recursive(option)
        end = time.perf_counter()
        times_recursive.append(end - start)

        tree = Tree(market, N=N, delta_t=1/N)

        # Méthode classique (niveau par niveau)
        start = time.perf_counter()
        tree.price_option(option)
        end = time.perf_counter()
        times_classic.append(end - start)

        print(f"N={N} -> recursive={times_recursive[-1]:.6f}s, classic={times_classic[-1]:.6f}s")

    # Tracer les résultats
    plt.figure(figsize=(8,5))
    plt.plot(Ns, times_recursive, marker="o", label="Arbre brique (récursif)")
    plt.plot(Ns, times_classic, marker="s", label="Arbre classique (niveau)")
    plt.xlabel("N (nombre de pas)")
    plt.ylabel("Temps de calcul (secondes)")
    plt.title("Comparaison des temps de calcul")
    plt.legend()
    plt.grid(True)
    plt.show()

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

def test_avec_div() :
    market = Market(S0=50, r= 0.7, sigma=0.8)
    tree = Tree(market, N=1000, delta_t=1/1000)
    date_vid = datetime(2026,1,3)
    option = Option(K=60, mat=1, opt_type="call", style="european", isDiv = True, div = 10, date_div = date_vid)

    prix_euro = tree.price_option_recursive(option)
    print(prix_euro)

    prix_bs = black_scholes(S0=50, K=60, T=1, r=0.7, sigma=0.8, type="call")

    print("Prix de l'arbre brique : ", prix_euro)
    print("Prix de l'arbre classique", prix_bs ) # on voit que l'arbre brique est plus court


def plot_trinomial_tree(S0=100, r=0.03, sigma=0.2,N=40, delta_t=None,K=100, mat=1, opt_type="call", style="european",isDiv=False, div=0, date_div=None,max_cols=20, annotate=False):
   
    # — Préparation
    if delta_t is None:
        delta_t = 1 / N

    market = Market(S0=S0, r=r, sigma=sigma)
    tree = Tree(market, N=N, delta_t=delta_t)
    option = Option(K=K, mat=mat, opt_type=opt_type, style=style,
                    isDiv=isDiv, div=div, date_div=date_div)

    # — Construction de l'arbre (méthode brique)
    tree.tree_construction2(option)

    # — Parcours des nœuds (on ne suit QUE Nup/Nmid/Ndown pour éviter tout cycle vertical)
    nodes = []      # (col, level, S, node_id)
    segments = []   # ((x1,y1), (x2,y2))
    visited = set()

    def walk(node, t=0):
        if node is None or t > max_cols:
            return
        nid = id(node)
        if (nid, t) in visited:
            return
        visited.add((nid, t))

        nodes.append((t, node.level, node.underlying, nid))

        # enfants → colonne t+1
        for child_name in ("Ndown", "Nmid", "Nup"):
            child = getattr(node, child_name)
            if child is not None:
                segments.append(((t, node.level), (t + 1, child.level)))
                walk(child, t + 1)

    walk(tree.root, 0)

    # — Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # arêtes
    for (x1, y1), (x2, y2) in segments:
        ax.plot([x1, x2], [y1, y2], linewidth=0.8, alpha=0.5)

    # nœuds (colorés par S)
    xs = [x for x, _, _, _ in nodes]
    ys = [y for _, y, _, _ in nodes]
    Ss = [s for _, _, s, _ in nodes]
    sc = ax.scatter(xs, ys, c=Ss, cmap="viridis", s=18, zorder=3)
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Sous-jacent S")

    # annotations optionnelles
    if annotate:
        for x, y, s, _ in nodes:
            ax.text(x, y + 0.08, f"{s:.1f}", ha="center", va="bottom", fontsize=7, alpha=0.8)

    # ligne verticale à la date de dividende (si applicable)
    if isDiv and date_div is not None:
        d0 = datetime.now()
        T  = d0 + relativedelta(years=mat)
        num = max(0, (date_div - d0).days)
        den = max(1, (T - d0).days)
        index = num / den  # fraction de la maturité
        # colonne à laquelle on applique le dividende dans tree_construction2
        # (même logique que ton code : seuil dans (i/N, (i+1)/N])
        div_step = None
        for i in range(1, N + 1):
            if index > i / N and index <= (i + 1) / N:
                div_step = i
                break
        if div_step is not None and div_step <= max_cols:
            ax.axvline(div_step, linestyle="--", alpha=0.6, color="red")
            ax.text(div_step, ax.get_ylim()[1], f" div ({div}) ", color="red",
                    va="top", ha="left", fontsize=8, bbox=dict(facecolor="white", alpha=0.6, edgecolor="none"))

    ax.set_xlabel("Colonne (timestep)")
    ax.set_ylabel("Niveau")
    ax.set_title("Arbre trinomial (structure Nup/Nmid/Ndown)")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_xlim(-0.3, min(max_cols + 0.3, N + 0.3))
    plt.tight_layout()
    plt.show()


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
    market = Market(S0=100, r=0.05, sigma=0.3)
    tree = Tree(market, N=n, delta_t=deltat)

    # --- Option avec dividende discret ---
    option = Option(
        K=102,
        mat=mat,     # ✅ utiliser la vraie maturité
        opt_type="put",
        style="american",
        isDiv=True,
        div=3,
        date_div=date_div,
        calc_date=calc_date       # utile si ton modèle l’utilise
    )

    # --- Pricing ---
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

def test_greeks_with_div() :
    from datetime import datetime
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
