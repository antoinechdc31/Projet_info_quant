import math
from Market import Market
from Node import Node
from Option import Option
import sys
sys.setrecursionlimit(5000)  # limite de recursion car on avait un pb de dépassement de max depth

class Tree : 

    def __init__(self, market: Market, N: int, delta_t):
        self.market = market
        self.N = N
        self.dt = delta_t
        self.alpha = math.exp(market.sigma * math.sqrt(3 * self.dt))
        self.root = Node(market.S0, self)


    def build_columns(self, node_trunc) :

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

        while current_node is not None:
            current_node.create_brick(False, direction = "down")
            current_node = current_node.down

        future_node_trunc = node_trunc.Nmid # on recupere le tronc de la prochaine colonne pour lui envoyer

        return future_node_trunc

    def tree_construction2(self) : # creation de l'arbre avec la méthode brique
        node_trunc = self.root # on part de la root

        for i in range(1, self.N + 1) : # puis pour chaque niveau souhaité

            node_trunc = self.build_columns(node_trunc) # on crée une colonne

        pass

    def price_option_recursive(self, option):

        self.tree_construction2() # créaction de l'arbre
        memo = {} # valeur des feuilles deja calculée pour eviter le calcul plusieurs fois
        return self.price_node(self.root, 0, option, memo) # appel de la fct recursive

    def price_node(self, node, t, option, memo):

        if node is None : # si le noeud n'existe pas on retourne 0
            return 0.0

        key = (id(node), t) # clé unique pour un nœud
        # puis on crée un memo pour se souvenir des anciennes valeur caculée, cela permet de gagner bcp de temps
        # et d'eviter de calculer plusieurs fois les memes valeurs
        if key in memo :
            return memo[key] # si cela existe, on retourne sa valeur qui a deja ete calculée

        if t == self.N : # si c'est la derniere colonne, on retourne le payoff
            val = option.payoff(node.underlying)
        else : # sinon on calcule avec la formule donnée par le cours -> DF * sum(V * proba)
            Vmid  = self.price_node(node.Nmid,  t+1, option, memo)
            Vup   = self.price_node(node.Nup,   t+1, option, memo)
            Vdown = self.price_node(node.Ndown, t+1, option, memo)
            # applicatio de la formule
            cont_value = (node.proba[0]*Vmid + node.proba[1]*Vup + node.proba[2]*Vdown) * math.exp(-self.market.r * self.dt)

            if option.style.lower() == "american" : # si c'est une américaine, on verifie le max entre le payoff actuel et la valeur calculée
                val = max(option.payoff(node.underlying), cont_value)
            else:
                val = cont_value # si c'est européenne on retourn e juste sa valeur

        memo[key] = val # on ajoute la valeur dans le mémo

        return val # puis on retourne cette valeur

    
    def tree_construction(self) :
        niveau = [[self.root]] # on initialise le premier niveau avec notre root
        for i in range(1, self.N + 1) : # on parcours tous les nv de l'arbre
            nv_niveau = [] # liste des futurs niveaux crées
            for j, noeud in enumerate(niveau[i - 1]):  # on parcourt les Nodes
                Smid, Sup, Sdown = noeud.next # calcul des futurs noeuds
                # print(Smid, Sup, Sdown)
                # print(node.calcul_proba())
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


    def print_tree(self):

        levels = self.tree_construction()
        max_width = len(levels[-1]) * 10  # largeur approx pour centrer

        for i, level in enumerate(levels) :
            prices = [f"{n.underlying:7.2f}" for n in level]
            line = ("   ".join(prices)).center(max_width)
            print(line)
