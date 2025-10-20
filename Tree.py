import math
from Market import Market
from Node import Node, NodeTrunc
from Option import Option
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys
import copy
import matplotlib.pyplot as plt
sys.setrecursionlimit(5000)  # limite de recursion car on avait un pb de dépassement de max depth
 
class Tree : 

    def __init__(self, market: Market, N: int, delta_t):
        self.market = market
        self.N = N
        self.dt = delta_t
        self.alpha = math.exp(market.sigma * math.sqrt(3 * self.dt))
        self.root = NodeTrunc(underlying = market.S0, tree = self, prev = None)
        self.Smid_tronc = None

#################### METHODE DES BRIQUES ####################

    def build_columns(self, node_trunc, is_div_date = False, option = None) :

        if is_div_date :
            
            div = option.div

            # current_node = node_trunc
            node_trunc.create_brick(True, direction = "up", div = div, is_div = is_div_date) # on crée la brick du tronc, la premiere brick de la colonne
            current_node = node_trunc.up # puis on prend son noeud "superieur" up, celui au dessus de lui dans la colonne

            while current_node is not None: # temps que le noeud n'est pas None (le noeud up sur la colonne de precedent)
                current_node.create_brick(False, direction = "up", div = div) # on crée la brique avec comme direction Up
                current_node = current_node.up # le noeud suivant va etre celui au dessus dans le sens de la colonne
            
            current_node = node_trunc.down # on fait la meme chose avec le noeud en dessous dans le sens de la colonne
            # avec comme diréction down

            while current_node is not None:
                current_node.create_brick(False, direction = "down", div = div)
                current_node = current_node.down

        else : 
            # current_node = node_trunc
            node_trunc.create_brick(True, direction = "up") # on crée la brick du tronc, la premiere brick de la colonne
            current_node = node_trunc.up # puis on prend son noeud "superieur" up, celui au dessus de lui dans la colonne
            # c'est à dire :    
            #           Node up
            #             |     Nup create avec create_bric du tronc
            #             |   /
            #           Trunc --- Nmid
            #             |  \
            #             |    Ndown 
            #           Node down

            while current_node is not None: # temps que le noeud n'est pas None (le noeud up sur la colonne de precedent)
                current_node.create_brick(False, direction = "up") # on crée la brique avec comme direction Up
                current_node = current_node.up # le noeud suivant va etre celui au dessus dans le sens de la colonne
            
            current_node = node_trunc.down # on fait la meme chose avec le noeud en dessous dans le sens de la colonne
            # avec comme diréction down

            while current_node is not None :
                current_node.create_brick(False, direction = "down")
                current_node = current_node.down

        future_node_trunc = node_trunc.Nmid # on recupere le tronc de la prochaine colonne pour lui envoyer
    
        return future_node_trunc

    def tree_construction2(self, option):  # création de l'arbre avec la méthode brique

        node_trunc = self.root
        index = -1

        if option.isDiv:
            d0 = option.calc_date
            T = d0 + relativedelta(years=option.mat)
            num = max(0, (option.date_div - d0).days)
            den = max(1, (T - d0).days)
            index = num / den
            print(f"Position du dividende dans la maturité : {index:.4f}")

        
        div_already_applied = False

        for i in range(1, self.N + 1):
            is_div_date = False

            if option.isDiv and (not div_already_applied):
                if index > i / self.N and index <= (i + 1) / self.N:
                    is_div_date = True
                    div_already_applied = True  # ⚡ le dividende ne sera plus appliqué ensuite
                    print(f"→ Dividende appliqué au pas {i}/{self.N} ({index:.4f})")
            #print(i)
            node_trunc = self.build_columns(node_trunc, is_div_date, option)

    def price_option_recursive(self, option):

        self.tree_construction2(option) # créaction de l'arbre
        # memo = {} # valeur des feuilles deja calculée pour eviter le calcul plusieurs fois
        return self.price_node2(self.root ,option) # appel de la fct recursive

    def price_node2(self, node,option):

        if node is None : # si le noeud n'existe pas on retourne 0
            return 0.0

        if node.Nmid is None : # si c'est la derniere colonne, on retourne le payoff
            val = option.payoff(node.underlying)
            node.option_value = val
        else : # sinon on calcule avec la formule donnée par le cours -> DF * sum(V * proba)

            if node.Nmid.option_value is not None :
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
                val = moy_pond# si c'est européenne on retourn e juste sa valeur

        node.option_value = val
        return val # puis on retourne cette valeur

    def price_node_backward(self, option):

        # on va jusq'à la dernière colonne (feuilles)
        node_trunc_final = self.root
        while node_trunc_final.Nmid is not None:
            node_trunc_final = node_trunc_final.Nmid

        # valoriser les feuilles
        current = node_trunc_final

        while current is not None:
            current.option_value = option.payoff(current.underlying)
            current = current.up

        current = node_trunc_final.down

        while current is not None:
            current.option_value = option.payoff(current.underlying)
            current = current.down

        # on remonte colonne par colonne
        node_trunc = node_trunc_final.prev
        while node_trunc is not None:

            # vers le haut
            current = node_trunc

            while current is not None:

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

    def pricing_noeud_indiv(self, option , current): # fonction generale pour pricer un noeud (pas feuille)

        Vmid = current.Nmid.option_value
        Vup = current.Nup.option_value
        Vdown = current.Ndown.option_value

        p_mid, p_up, p_down = current.calcul_proba()
        df = math.exp(-self.market.r * self.dt)
        moy_pond = df * (p_mid * Vmid + p_up * Vup + p_down * Vdown)

        if option.style.lower() == "american":
            val = max(option.payoff(current.underlying), moy_pond)
        else:
            val = moy_pond

        return val

    def delta(self,option, h=1e-2):

        S0 = self.market.S0
        h = h * S0 # 1% du prix
        market_up = Market(S0 + h, self.market.r, self.market.sigma)
        market_down = Market(S0 - h, self.market.r, self.market.sigma)

        # Reconstruit les arbres complets
        tree_up = Tree(market_up, self.N, self.dt)
        # tree_up.tree_construction2()
        tree_down = Tree(market_down, self.N, self.dt)
        # tree_down.tree_construction2()
        # tree_up = Tree(self.market, self.N, self.dt)
        # tree_down = Tree(self.market, self.N, self.dt)

        # tree_up.market.S0 = S0 + h
        # tree_down.market.S0 = S0 - h

        price_up = tree_up.price_option_recursive(option)
        price_down = tree_down.price_option_recursive(option)

        delta = (price_up - price_down) / (2 * h)
        print(f"Δ (Delta) = {delta:.6f}")
        return delta

    # def gamma(self, option, h=1e-2):

    #     S0 = self.market.S0
    #     h = h * S0
    #     market_up = Market(S0 + h, self.market.r, self.market.sigma)
    #     market_down = Market(S0 - h, self.market.r, self.market.sigma)
    #     tree_up = Tree(market_up, self.N, self.dt)
    #     # tree_up.tree_construction2()
    #     tree_down = Tree(market_down, self.N, self.dt)

    #     price_up = tree_up.price_option_recursive(option)
    #     price_down = tree_down.price_option_recursive(option)
    #     price_0 = self.price_option_recursive(option)

    #     gamma = (price_up - 2 * price_0 + price_down) / ((h)**2) # formule du cours
    #     print(f"Γ (Gamma) = {gamma:.6f}")
    #     return gamma

    def gamma(self, option, h=1e-2):

        S0 = self.market.S0
        h = h * S0  # 1% du prix
        r = self.market.r
        sigma = self.market.sigma

        # 3 marchés indépendants
        market_up = Market(S0 + h, r, sigma)
        market_down = Market(S0 - h, r, sigma)
        market_0 = Market(S0, r, sigma)

        # 3 arbres indépendants
        tree_up = Tree(market_up, self.N, self.dt)
        tree_down = Tree(market_down, self.N, self.dt)
        tree_0 = Tree(market_0, self.N, self.dt)

        # Prix sur chaque arbre
        price_up = tree_up.price_option_recursive(option)
        price_down = tree_down.price_option_recursive(option)
        price_0 = tree_0.price_option_recursive(option)

        # Gamma par différences centrées
        gamma = (price_up - 2 * price_0 + price_down) / (h ** 2)
        print(f"Γ (Gamma) = {gamma:.6f}")
        return gamma

    def vega(self, option, hVol=0.01):
        """
        Calcule le Vega : sensibilité du prix à la volatilité.
        hVol = variation relative (ex: 0.01 = 1%)
        """

        sigma = self.market.sigma
        r = self.market.r
        S0 = self.market.S0

        # Marchés indépendants
        market_up = Market(S0, r, sigma * (1 + hVol))
        market_down = Market(S0, r, sigma * (1 - hVol))

        # Arbres indépendants
        tree_up = Tree(market_up, self.N, self.dt)
        tree_down = Tree(market_down, self.N, self.dt)

        # Calcul des prix
        price_up = tree_up.price_option_recursive(option)
        price_down = tree_down.price_option_recursive(option)

        # Différence centrée
        vega = (price_up - price_down) / (2 * sigma * hVol)
        print(f"Vega = {vega:.6f}")
        return vega


    def volga(self, option, hVol=0.05):
        """
        Calcule la Volga (Vomma) : courbure du prix par rapport à la volatilité.
        """

        sigma = self.market.sigma
        r = self.market.r
        S0 = self.market.S0

        # Marchés indépendants
        market_up = Market(S0, r, sigma * (1 + hVol))
        market_down = Market(S0, r, sigma * (1 - hVol))
        market_0 = Market(S0, r, sigma)

        # Arbres indépendants
        tree_up = Tree(market_up, self.N, self.dt)
        tree_down = Tree(market_down, self.N, self.dt)
        tree_0 = Tree(market_0, self.N, self.dt)

        # Calcul des prix
        price_up = tree_up.price_option_recursive(option)
        price_down = tree_down.price_option_recursive(option)
        price_0 = tree_0.price_option_recursive(option)

        # Différence centrée seconde
        volga = (price_up - 2 * price_0 + price_down) / ((sigma * hVol) ** 2)
        print(f"Volga (Vomma) = {volga:.6f}")
        return volga

    def plot_tree(self, option=None, show_option_values=False, max_depth=10):
        """
        Affiche l’arbre trinomial avec Matplotlib uniquement.
        - option : objet Option pour récupérer les valeurs d’option
        - show_option_values : booléen pour afficher la valeur d’option au lieu du sous-jacent
        - max_depth : limite du nombre de colonnes affichées
        """
        # Construit l’arbre
        self.tree_construction2(option)

        fig, ax = plt.subplots(figsize=(14, 8))
        ax.set_title(f"🌲 Arbre Trinomial ({'Valeurs option' if show_option_values else 'Sous-jacents'})", fontsize=14)
        ax.axis("off")

        # Dictionnaire pour stocker les nœuds par niveau
        niveaux = {}
        queue = [(self.root, 0)]  # (node, niveau)

        while queue:
            node, niveau = queue.pop(0)
            if niveau > max_depth:
                continue
            if niveau not in niveaux:
                niveaux[niveau] = []
            niveaux[niveau].append(node)

            # Enfants
            for child in [node.Ndown, node.Nmid, node.Nup]:
                if child is not None:
                    queue.append((child, niveau + 1))

        # Calcul des positions horizontales
        y_offset = 0
        for niveau, noeuds in niveaux.items():
            x_positions = list(range(len(noeuds)))
            for x, node in zip(x_positions, noeuds):
                y = -niveau
                label = (
                    f"{node.option_value:.2f}"
                    if show_option_values and node.option_value is not None
                    else f"{node.underlying:.2f}"
                )

                ax.text(
                    x,
                    y,
                    label,
                    ha="center",
                    va="center",
                    fontsize=8,
                    bbox=dict(facecolor="#90EE90" if show_option_values else "#ADD8E6", boxstyle="round,pad=0.3"),
                )

        # Tracer les liens entre les niveaux
        for niveau, noeuds in niveaux.items():
            if niveau + 1 not in niveaux:
                continue
            next_nodes = niveaux[niveau + 1]
            for i, node in enumerate(noeuds):
                children = [node.Ndown, node.Nmid, node.Nup]
                for child in children:
                    if child in next_nodes:
                        x_parent = i
                        y_parent = -niveau
                        x_child = next_nodes.index(child)
                        y_child = -(niveau + 1)
                        ax.plot(
                            [x_parent, x_child],
                            [y_parent, y_child],
                            color="gray",
                            linewidth=0.8,
                            alpha=0.6,
                        )

        plt.tight_layout()
        return fig


    # def vega(self, option, hVol=1e-2):

    #     sigma = self.market.sigma
    #     tree_up = Tree(self.market, self.N, self.dt)
    #     tree_down = Tree(self.market, self.N, self.dt)

    #     tree_up.market.sigma = sigma * (1 + hVol)
    #     tree_down.market.sigma = sigma * (1 - hVol)

    #     price_up = tree_up.price_option_recursive(option)
    #     price_down = tree_down.price_option_recursive(option)

    #     vega = (price_up - price_down) / (2 * sigma * hVol)
    #     print(f"Vega = {vega:.6f}")
    #     return vega

    # def volga(self, option, hVol=1e-2):

    #     sigma = self.market.sigma

    #     # Copies indépendantes de l’arbre
    #     tree_up = Tree(self.market, self.N, self.dt)
    #     tree_down = Tree(self.market, self.N, self.dt)

    #     tree_up.market.sigma = sigma * (1 + hVol)
    #     tree_down.market.sigma = sigma * (1 - hVol)

    #     # Calcul des prix pour sigma+h, sigma, sigma−h
    #     price_up = tree_up.price_option_recursive(option)
    #     price_down = tree_down.price_option_recursive(option)
    #     price_0 = self.price_option_recursive(option)

    #     # Formule des différences centrées secondes
    #     Volga = (price_up - 2 * price_0 + price_down) / ((sigma * hVol) ** 2)

    #     print(f"Volga (Vomma) = {Volga:.6f}")
    #     return Volga


################# METHODE SANS BRIQUE ###################

    def tree_construction(self) : # version sans brique

        niveau = [[self.root]] # on initialise le premier niveau avec notre root
        for i in range(1, self.N + 1) : # on parcours tous les nv de l'arbre
            nv_niveau = [] # liste des futurs niveaux crées
            for j, noeud in enumerate(niveau[i - 1]):  # on parcourt les Nodes et leurs indices
                Smid, Sup, Sdown = noeud.next # calcul des futurs noeuds

                # pour le premier noeud on crée les 3 enfants
                if j == 0 :
                    down_node = Node(Sdown, self)
                    mid_node = Node(Smid, self)
                    up_node = Node(Sup, self)
                    nv_niveau.extend([down_node, mid_node, up_node])
                else :
                    # pour les autres on ne garde que le up car sinon ils ont deja été crée
                    up_node = Node(Sup, self)
                    nv_niveau.append(up_node)
            niveau.append(nv_niveau) # ajout du nv niveau

        return niveau

    def price_option(self, option: Option):
        niveau = self.tree_construction() # on crée l'arbre
        # ensuite on calcule les payoff a maturité
        # donc on prend le dernier niveau t_N = T

        dernier_nv = niveau[-1]
        # print(dernier_nv)
        list_payoff = []
        for n in dernier_nv :
            list_payoff.append(option.payoff(n.underlying)) # ajout de chaque payoff de la dernier ligne
        # print(list_payoff) payoff validé

        # niveau t_N-1 etc

        for i in range(len(niveau) - 1, 0 , -1) :

            list_val = []
            # print(niveau[i-1])
            for j, noeud in enumerate(niveau[i-1]) :

                # print("niveau ", i - 1)
                # print(j, noeud)

                Pmid, Pup, Pdown = noeud.proba # on recupere les probas du noeud (grace à la classe noeud)
                DF = math.exp( - self.market.r * self.dt) # calcul du DF comme dans les slide
    
                valeur = DF * ( Pdown * list_payoff[ j] + Pmid * list_payoff[j + 1] + Pup * list_payoff[j + 2 ] )
                # la valeur vaut le DF fois la somme des proba * nv d'avant

                if option.style == "american":
                    valeur = max(valeur, option.payoff(noeud.underlying)) # pour chaque noeuf la valeur est le max entre ces deux quantités
                    # valeur hold et la valeur d'exercice avec le payoff

                list_val.append(valeur) # on ajoute la valeur calculée pour la stocker pour les prochains niveaux

            list_payoff = list_val  # on remplace pour l'étape suivante
            # print(list_payoff)

        return list_payoff[0] # a la fin on a la derniere valeur

 