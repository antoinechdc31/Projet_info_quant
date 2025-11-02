import math
from Market import Market
from Node import Node, NodeTrunc
from Option import Option
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys
from datetime import timedelta
import copy
import matplotlib.pyplot as plt
sys.setrecursionlimit(100000)  # limite de recursion car on avait un pb de dépassement de max depth

class Tree : 

    def __init__(self, market: Market, N: int, delta_t):
        self.market = market
        self.N = N
        self.dt = delta_t
        self.alpha = math.exp(market.sigma * math.sqrt(3 * self.dt))
        self.root = NodeTrunc(underlying = market.S0, tree = self, prev = None)

#################### METHODE DES BRIQUES ####################

    def build_columns(self, node_trunc, is_div_date = False, option = None) :
        """
        création d'une colonne de l'arbre
        """
        if is_div_date : # si il y a des dividendes on donne sa valeur a notre var
            div = option.div
        else :
            div = 0
            # current_node = node_trunc
        node_trunc.create_brick(True, direction = "up", div = div) # on crée la brick du tronc,
        # la premiere brick de la colonne
        current_node = node_trunc.up # puis on prend son noeud "superieur" up, 
        # celui au dessus de lui dans la colonne

        while current_node is not None: # temps que le noeud n'est pas None
            current_node.create_brick(False, direction = "up", div = div) # on crée la brique avec comme direction Up
            current_node = current_node.up # le noeud suivant va etre 
            # celui au dessus dans le sens de la colonne
        
        current_node = node_trunc.down # on fait la meme chose avec le noeud en dessous dans le sens de la colonne
        # avec comme diréction down

        while current_node is not None:
            current_node.create_brick(False, direction = "down", div = div)
            current_node = current_node.down

        future_node_trunc = node_trunc.Nmid # on recupere le node tronc de la prochaine colonne
    
        return future_node_trunc

    def tree_construction2(self, option):  # création de l'arbre avec la méthode brique

        node_trunc = self.root # prmeier noeud exploré
        index = -1 # initalisation de la variable index à -1

        if option.isDiv:
            d0 = option.calc_date
            T = d0 + timedelta(days=option.mat * 365) # on utilise cela au cas ou la maturité
            # ne soit pas entiere
            num = max(0, (option.date_div - d0).days)
            den = max(1, (T - d0).days)
            index = num / den # on calcul l'index ou l'on devra appliquer les div
            # print(f"Position du dividende dans la maturité : {index:.4f}")
        div_already_applied = False

        for i in range(1, self.N + 1):
            is_div_date = False
            if option.isDiv and (not div_already_applied):
                if index > i / self.N and index <= (i + 1) / self.N: # si les div doivent etre appliqué
                    is_div_date = True
                    div_already_applied = True # on met nos variables a True pour l'indiquer
            
            node_trunc = self.build_columns(node_trunc, is_div_date, option)

    def price_option_recursive(self, option):
        return self.price_node2(self.root ,option) # appel de la fct recursive

    def price_node2(self, node,option):

        if node is None : # si le noeud n'existe pas on retourne 0
            return 0.0

        if node.Nmid is None or (node.Nup is None and node.Ndown is None): # si c'est la derniere colonne, on retourne le payoff
            val = option.payoff(node.underlying)
            node.option_value = val
        else : # sinon on calcule avec la formule donnée par le cours -> DF * sum(V * proba)

            if node.Nmid.option_value is not None : # si la valeur a deja ete calculé on la recupere
                # sinon on la calcule
                Vmid = node.Nmid.option_value
            else :
                Vmid  = self.price_node2(node.Nmid, option)
                node.Nmid.option_value = Vmid

            if node.Nup.option_value is not None :
                Vup = node.Nup.option_value
            else :
                Vup  = self.price_node2(node.Nup, option)
                node.Nup.option_value = Vup

            if node.Ndown.option_value is not None :
                Vdown = node.Ndown.option_value
            else :
                Vdown  = self.price_node2(node.Ndown, option)
                node.Ndown.option_value = Vdown

            # application de la formule
            p_mid, p_up, p_down = node.calcul_proba()
            df = math.exp(-self.market.r * self.dt)
            moy_pond = df * (p_mid * Vmid + p_up * Vup + p_down * Vdown)

            if option.style.lower() == "american":
                val = max(option.payoff(node.underlying), moy_pond)
            else:
                val = moy_pond  # si c'est européenne on retourne juste sa valeur

        node.option_value = val
        return val # puis on retourne cette valeur
    
    def price_node_backward(self, option):

        # on va jusq'à la dernière colonne (feuilles)
        node_trunc_final = self.root
        while node_trunc_final.Nmid is not None:
            node_trunc_final = node_trunc_final.Nmid

        # valoriser les feuilles
        self.price_last_node(node_trunc_final, option)

        # on remonte colonne par colonne
        node_trunc = node_trunc_final.prev
        while node_trunc is not None:

            # vers le haut
            current = node_trunc

            while current is not None: # tant qu'il y a un noeud au dessus

                val = self.pricing_noeud_indiv(option, current)

                current.option_value = val
                current = current.up

            # vers le bas
            current = node_trunc.down

            while current is not None:

                val = self.pricing_noeud_indiv(option, current)

                current.option_value = val
                current = current.down

            # on passe à la colonne précédente
            node_trunc = node_trunc.prev

        # le prix de l’option = valeur de la racine
        return self.root.option_value
    
    def price_last_node(self, node_trunc_final, option) :
        
        current = node_trunc_final
        # boucle if pour valoriser toutes les feuilles vers le haut
        while current is not None:
            current.option_value = option.payoff(current.underlying)
            current = current.up

        current = node_trunc_final.down
        
        # boucle if pour valoriser toutes les feuilles vers le bas
        while current is not None:
            current.option_value = option.payoff(current.underlying)
            current = current.down

        pass

    def pricing_noeud_indiv(self, option , current): # fonction generale pour pricer un noeud (pas feuille)

        """
        on recupere les valuers des noeuds next pour appliquer
        la formule de valorisation
        """

        Vmid  = current.Nmid.option_value  if current.Nmid  else 0.0
        Vup   = current.Nup.option_value   if current.Nup   else 0.0
        Vdown = current.Ndown.option_value if current.Ndown else 0.0

        p_mid, p_up, p_down = current.calcul_proba()
        df = math.exp(-self.market.r * self.dt)
        moy_pond = df * (p_mid * Vmid + p_up * Vup + p_down * Vdown)

        if option.style.lower() == "american": # si c est une americaine,
            # on applique la formule appropriée
            val = max(option.payoff(current.underlying), moy_pond)
        else :
            val = moy_pond

        return val

    def delta(self,option, h = 1e-2):
        """
        fonction qui permet le calcul du delta avec la formule vu en cours
        """
        S0 = self.market.S0
        h = h * S0 # 1% du prix
        market_up = Market(S0 + h, self.market.r, self.market.sigma) # creation des marchés
        market_down = Market(S0 - h, self.market.r, self.market.sigma)

        tree_up = Tree(market_up, self.N, self.dt) # création des arbres
        tree_up.tree_construction2(option) # construction de ces arbres
        tree_down = Tree(market_down, self.N, self.dt)
        tree_down.tree_construction2(option)

        price_up = tree_up.price_option_recursive(option) # on price en recursif 
        price_down = tree_down.price_option_recursive(option)

        delta = (price_up - price_down) / (2 * h) # et on applique la formule du cours
        print(f"Δ (Delta) = {delta:.6f}")
        return delta

    def gamma(self, option, h=1e-2):
        """
        calcul du gamma avec la fonction vu en cours
        """
        S0 = self.market.S0
        h = h * S0  # 1% du prix
        r = self.market.r
        sigma = self.market.sigma

        market_up = Market(S0 + h, r, sigma) # creation du marché avec le décalage
        market_down = Market(S0 - h, r, sigma)
        market_0 = Market(S0, r, sigma)

        tree_up = Tree(market_up, self.N, self.dt) # on fait les arbres
        tree_down = Tree(market_down, self.N, self.dt)
        tree_0 = Tree(market_0, self.N, self.dt)

        tree_up.tree_construction2(option) # on les construit
        tree_down.tree_construction2(option)
        tree_0.tree_construction2(option)
        price_up = tree_up.price_option_recursive(option) # puis on les price
        price_down = tree_down.price_option_recursive(option)
        price_0 = tree_0.price_option_recursive(option)

        gamma = (price_up - 2 * price_0 + price_down) / (h ** 2) # finalement on applique la formule
        print(f"Γ (Gamma) = {gamma:.6f}")
        return gamma

    def vega(self, option, hVol=0.01):
        """
        calcul du vega avec la formule vue en cours
        """
        sigma = self.market.sigma
        r = self.market.r
        S0 = self.market.S0

        market_up = Market(S0, r, sigma * (1 + hVol)) # creation de marché associé au decalage
        market_down = Market(S0, r, sigma * (1 - hVol))

        tree_up = Tree(market_up, self.N, self.dt) # initialisation des arbres
        tree_down = Tree(market_down, self.N, self.dt)
        
        tree_up.tree_construction2(option) # pricing
        tree_down.tree_construction2(option)
        price_up = tree_up.price_option_recursive(option)
        price_down = tree_down.price_option_recursive(option)

        vega = (price_up - price_down) / (2 * sigma * hVol) # applique la formule
        print(f"Vega = {vega:.6f}")
        return vega

    def volga(self, option, hVol=0.05):
        """
        calcul du volga avec la formule vue en cours
        """
        sigma = self.market.sigma
        r = self.market.r
        S0 = self.market.S0

        market_up = Market(S0, r, sigma * (1 + hVol)) # on crée encore une fois les amrchés associés au décalage
        market_down = Market(S0, r, sigma * (1 - hVol))
        market_0 = Market(S0, r, sigma)

        tree_up = Tree(market_up, self.N, self.dt) # les arbres avec ces amrchés qui ont le décalage
        tree_down = Tree(market_down, self.N, self.dt)
        tree_0 = Tree(market_0, self.N, self.dt)

        tree_up.tree_construction2(option) # on les construit
        tree_down.tree_construction2(option)
        tree_0.tree_construction2(option)

        price_up = tree_up.price_option_recursive(option) # puis on price
        price_down = tree_down.price_option_recursive(option)
        price_0 = tree_0.price_option_recursive(option)

        volga = (price_up - 2 * price_0 + price_down) / ((sigma * hVol) ** 2) # puis application de la formule des
        # différences finies
        print(f"Volga (Vomma) = {volga:.6f}")
        return volga
    
    def plot_trinomial_tree(self, option=None, max_cols=20, annotate=False, show=True):

        if option is None:
            raise ValueError("Vous devez fournir une option pour construire l'arbre.")

        self.tree_construction2(option)

        nodes = []     
        segments = [] 
        visited = set()

        def walk(node, t=0):
            """on fait un parcours récursif pour collecter les node et les liens"""
            if node is None or t > max_cols:
                return
            nid = id(node)
            if (nid, t) in visited:
                return
            visited.add((nid, t))

            # Enregistre le nœud
            nodes.append((t, node.underlying))

            # Enregistre les arêtes
            for child_name in ("Ndown", "Nmid", "Nup"):
                child = getattr(node, child_name)
                if child is not None:
                    segments.append(((t, node.underlying), (t + 1, child.underlying)))
                    walk(child, t + 1)

        walk(self.root, 0)
        
        fig, ax = plt.subplots(figsize=(12, 7))

        # on lie les noeuds entre eux
        for (x1, s1), (x2, s2) in segments:
            ax.plot([x1, x2], [s1, s2], color="gray", linewidth=0.8, alpha=0.5)

        # noeud qui prendront une couleur associée a la valeur du sous jacent
        xs = [x for x, _ in nodes]
        Ss = [s for _, s in nodes]
        scatter = ax.scatter(xs, Ss, c=Ss, cmap="viridis", s=25, zorder=3)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Sous-jacent S")

        # on crée la ligne verticale pour les dividendes afin de bien voir le déclaage
        if option.isDiv and option.date_div is not None:
            d0 = option.calc_date
            T = d0 + relativedelta(years=option.mat)
            num = max(0, (option.date_div - d0).days)
            den = max(1, (T - d0).days)
            index = num / den

            div_step = None
            for i in range(1, self.N + 1): # meme formule etc que pour la création de l'arbre
                if index > i / self.N and index <= (i + 1) / self.N:
                    div_step = i
                    break

            if div_step is not None and div_step <= max_cols:
                ax.axvline(div_step, linestyle="--", alpha=0.8, color="red", linewidth=1.2)
                ax.text(
                    div_step + 0.2,
                    max(Ss),
                    f" Dividende = {option.div} ",
                    color="red",
                    fontsize=9,
                    va="top",
                    ha="left",
                    bbox=dict(facecolor="white", alpha=0.6, edgecolor="none"),
                )

        # axes
        ax.set_xlabel("Colonne (timestep)")
        ax.set_ylabel("Sous-jacent S")
        ax.set_title("Arbre Trinomial (valeurs réelles du sous-jacent)", fontsize=13)
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.set_xlim(-0.3, min(max_cols + 0.3, self.N + 0.3))
        plt.tight_layout()

        if show:
            plt.show()
        else:
            return fig
