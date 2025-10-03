from Market import Market
from Tree import Tree
from Node import Node
from BlackScholes import black_scholes
from Option import Option
import time
from datetime import datetime
import matplotlib.pyplot as plt

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
    market = Market(S0=50, r= 0.7, sigma=0.8)
    tree = Tree(market, N=100, delta_t=3/100)
    option = Option(K=60, mat=3, opt_type="put", style="european")

    prix_euro = tree.price_option_recursive(option)

    option = Option(K=60, mat=3, opt_type="put", style="american")

    prix_amer = tree.price_option_recursive(option)

    print("Prix euro =", prix_euro)
    print("Prix americain =", prix_amer)

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
    test_avec_div()
