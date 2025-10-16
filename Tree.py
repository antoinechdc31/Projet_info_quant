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

        S0 = self.S0
        tree_up = copy.deepcopy(self)
        tree_down = copy.deepcopy(self)

        tree_up.S0 = S0 + h
        tree_down.S0 = S0 - h

        price_up = tree_up.price_option_recursive(option)
        price_down = tree_down.price_option_recursive(option)

        delta = (price_up - price_down) / (2 * h)
        print(f"Δ (Delta) = {delta:.6f}")
        return delta

    def gamma(self, option, h=1e-2):

        S0 = self.S0
        tree_up = copy.deepcopy(self)
        tree_down = copy.deepcopy(self)

        tree_up.S0 = S0 + h
        tree_down.S0 = S0 - h

        price_up = tree_up.price_option_recursive(option)
        price_down = tree_down.price_option_recursive(option)
        price_0 = self.price_option_recursive(option)

        gamma = (price_up - 2 * price_0 + price_down) / ((h)**2) # formule du cours
        print(f"Γ (Gamma) = {gamma:.6f}")
        return gamma

    def vega(self, option, hVol=1e-2):

        sigma = self.sigma
        tree_up = copy.deepcopy(self)
        tree_down = copy.deepcopy(self)

        tree_up.sigma = sigma * (1 + hVol)
        tree_down.sigma = sigma * (1 - hVol)

        price_up = tree_up.price_option_recursive(option)
        price_down = tree_down.price_option_recursive(option)

        vega = (price_up - price_down) / (2 * sigma * hVol)
        print(f"Vega = {vega:.6f}")
        return vega

    def volga(self, option, hVol=1e-2):

        sigma = self.sigma

        # Copies indépendantes de l’arbre
        tree_up = copy.deepcopy(self)
        tree_down = copy.deepcopy(self)

        # On modifie légèrement la volatilité
        tree_up.sigma = sigma * (1 + hVol)
        tree_down.sigma = sigma * (1 - hVol)

        # Calcul des prix pour sigma+h, sigma, sigma−h
        price_up = tree_up.price_option_recursive(option)
        price_down = tree_down.price_option_recursive(option)
        price_0 = self.price_option_recursive(option)

        # Formule des différences centrées secondes
        Volga = (price_up - 2 * price_0 + price_down) / ((sigma * hVol) ** 2)

        print(f"Volga (Vomma) = {Volga:.6f}")
        return Volga



    def plot_tree(self, option=None, show_option_values=False,  max_depth=6):
        # (Re)construction de l'arbre
        if option:
            self.tree_construction2(option)
        else:
            from Option import Option
            option = Option(K=0, mat=1, opt_type="call", style="european", isDiv=False)
            self.tree_construction2(option)

        # --- collecte jusqu'à max_depth ---
        levels = []
        current_level = [self.root]
        for _ in range(max_depth):
            levels.append(current_level)
            next_level = []
            for node in current_level:
                if node and node.Nmid:
                    next_level.extend([node.Ndown, node.Nmid, node.Nup])
            current_level = [n for n in next_level if n is not None]

        # --- coordonnées ---
        x_points, y_points = [], []
        lines = []
        for i, level in enumerate(levels):
            for node in level:
                if not node:
                    continue
                x_points.append(i)
                val = node.option_value if show_option_values else node.underlying
                y_points.append(val)

                if node.Nmid and i < max_depth - 1:
                    for child in [node.Ndown, node.Nmid, node.Nup]:
                        if child:
                            lines.append(
                                ((i, i + 1),
                                 (val, child.option_value if show_option_values else child.underlying))
                            )

        # --- affichage ---
        plt.figure(figsize=(10, 6))
        for (xv, yv) in lines:
            plt.plot(xv, yv, color="gray", linewidth=0.7, alpha=0.5)

        plt.scatter(x_points, y_points, s=20, c="royalblue", alpha=0.8)

        # Ligne du dividende
        if option.isDiv and option.date_div:
            d0 = datetime.now()
            T = d0 + relativedelta(years=option.mat)
            pos = (option.date_div - d0).days / max(1, (T - d0).days)
            x_div = int(pos * max_depth)
            plt.axvline(x=x_div, color="red", linestyle="--", linewidth=1.5, label=f"Div ({option.div})")

        plt.title(f"Arbre trinomial - {'Option' if show_option_values else 'Sous-jacent'}")
        plt.xlabel("Étape (t)")
        plt.ylabel("Valeur")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()
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

 