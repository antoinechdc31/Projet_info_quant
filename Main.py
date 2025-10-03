from Market import Market
from Tree import Tree
from Node import Node
from BlackScholes import black_scholes
from Option import Option
import time
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
    Ks = np.linspace(89, 109, 100)  # strikes testés
    prix_tree = []
    prix_bs = []
    diffs = []

    market = Market(S0=100, r=0.03, sigma=0.2)
    option_template = {"mat":1, "opt_type":"call", "style":"european"}

    for K in Ks:
        tree = Tree(market, N=400, delta_t=1/400)
        option = Option(K=K, **option_template)

        p_tree = tree.price_option_recursive(option)
        p_bs = black_scholes(S0=100, K=K, T=1, r=0.03, sigma=0.2, type="call")

        prix_tree.append(p_tree)
        prix_bs.append(p_bs)
        diffs.append(p_tree - p_bs)

    prix_tree = np.array(prix_tree)
    prix_bs = np.array(prix_bs)
    diffs = np.array(diffs)

    # Approximation de la pente (dérivée ≈ delta numérique)
    slope_tree = np.gradient(prix_tree, Ks)
    slope_bs = np.gradient(prix_bs, Ks)

    # --- Graphique 1 : prix + pentes ---
    plt.figure(figsize=(9,6))
    plt.plot(Ks, prix_tree, label="Trinomial (recursive)")
    plt.plot(Ks, prix_bs, label="Black–Scholes")
    plt.xlabel("Strike K")
    plt.ylabel("Prix de l’option")
    plt.title("Prix en fonction du strike")
    plt.grid(True)
    plt.legend()

    # Ajouter les pentes sur le même graphe
    plt.twinx()
    plt.plot(Ks, slope_tree, color="blue", alpha=0.6, label="Pente Tree")
    plt.plot(Ks, slope_bs, color="orange", alpha=0.6, label="Pente BS")
    plt.ylabel("Pente (∂Prix/∂K)")
    plt.legend(loc="lower right")

    plt.show()

    # --- Graphique 2 : différence ---
    plt.figure(figsize=(8,5))
    plt.plot(Ks, diffs, marker="o", label="Prix Tree - Prix BS")
    plt.axhline(0, color="black", linestyle="--")
    plt.xlabel("Strike K")
    plt.ylabel("Écart de prix")
    plt.title("Écart entre Trinomial récursif et Black–Scholes")
    plt.grid(True)
    plt.legend()
    plt.show()

def test_avec_div() :
    market = Market(S0=50, r= 0.7, sigma=0.8)
    tree = Tree(market, N=1000, delta_t=1/1000)
    option = Option(K=60, mat=1, opt_type="call", style="european")

    prix_euro = tree.price_option_recursive(option)
    print(prix_euro)

    prix_bs = black_scholes(S0=50, K=60, T=1, r=0.7, sigma=0.8, type="call")

    print("Prix de l'arbre brique : ", prix_euro)
    print("Prix de l'arbre classique", prix_bs ) # on voit que l'arbre brique est plus court

if __name__ == "__main__":
    #compare_tree_bs_vs_strike()
    #test_avec_div()
    #convergence_recursive()
    benchmark_tree_times()