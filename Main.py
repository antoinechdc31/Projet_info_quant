from Market import Market
from Tree import Tree
from Node import Node
from BlackScholes import black_scholes
from Option import Option
import time
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
    Ns = [10, 20, 50, 100, 200, 400, 800]  # différents timesteps
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

    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(Ns, times_recursive, marker='o', label="Recursive")
    plt.plot(Ns, times_iterative, marker='o', label="Iterative")
    plt.xlabel("Timesteps (N)")
    plt.ylabel("Temps de calcul (secondes)")
    plt.title("Comparaison des vitesses de calcul des arbres")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    benchmark_tree_times()