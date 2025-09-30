import math
from Market import Market
from Node import Node
from Option import Option

class Tree : 

    def __init__(self, market: Market, N: int, delta_t):
        self.market = market
        self.N = N
        self.dt = delta_t
        self.alpha = math.exp(market.sigma * math.sqrt(3 * self.dt))
        self.root = Node(market.S0, self)


    def build_columns(self, node_trunc) :

        # current_node = node_trunc
        node_trunc.create_brick(True, direction = "up")
        current_node = node_trunc.up

        while current_node is not None:
            current_node.create_brick(False, direction = "up")
            current_node = current_node.up
        
        current_node = node_trunc.down

        while current_node is not None:
            current_node.create_brick(False, direction = "down")
            current_node = current_node.down

        future_node_trunc = node_trunc.Nmid

        return future_node_trunc

    def tree_construction2(self) :
        node_trunc = self.root

        for i in range(1, self.N + 1) :

            node_trunc = self.build_columns(node_trunc)

        pass

    def price_option_recursive(self, option):

        self.tree_construction2() # créaction de l'arbre
        memo = {} # valeur des feuilles deja calculée pour eviter le calcul plusieurs fois
        return self.price_node(self.root, 0, option, memo) # appel de la fct recursive

    def price_node(self, node, t, option, memo):

        if node is None : # si le noeud n'existe pas on retourne 0
            return 0.0

        # clé unique pour un nœud
        key = (id(node), t) 
        # memo pour se souvenir des anciennes valeur caculée
        if key in memo :
            return memo[key]

        if t == self.N : # si c'est la derniere colonne, on retourne le payoff
            val = option.payoff(node.underlying)
        else : # sinon on calcule avec la formule donnée par le cours -> DF * sum(V * proba)
            Vmid  = self._price_node(node.Nmid,  t+1, option, memo)
            Vup   = self._price_node(node.Nup,   t+1, option, memo)
            Vdown = self._price_node(node.Ndown, t+1, option, memo)

            cont_value = (
                node.proba[0]*Vmid +
                node.proba[1]*Vup +
                node.proba[2]*Vdown
            ) * math.exp(-self.market.r * self.dt)

            if option.style.lower() == "american":
                val = max(option.payoff(node.underlying), cont_value)
            else:
                val = cont_value

        memo[key] = val

        return val

    
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

                print("niveau ", i - 1)
                print(j, noeud)

                Pmid, Pup, Pdown = noeud.proba # on recupere les probas du noeud (grace à la classe noeud)
                DF = math.exp( - self.market.r * self.dt) # calcul du DF comme dans les slide
    
                valeur = DF * ( Pdown * list_payoff[ j] + Pmid * list_payoff[j + 1] + Pup * list_payoff[j + 2 ] )
                # la valeur vaut le DF fois la somme des proba * nv d'avant

                if option.style == "american":
                    valeur = max(valeur, option.payoff(noeud.underlying)) # pour chaque noeuf la valeur est le max entre ces deux quantités
                    # valeur hold et la valeur d'exercice avec le payoff

                list_val.append(valeur) # on ajoute la valeur calculée pour la stocker pour les prochains niveaux

            list_payoff = list_val  # on remplace pour l'étape suivante
            print(list_payoff)

        return list_payoff[0] # a la fin on a la derniere valeur


    def print_tree(self):

        levels = self.tree_construction()
        max_width = len(levels[-1]) * 10  # largeur approx pour centrer

        for i, level in enumerate(levels) :
            prices = [f"{n.underlying:7.2f}" for n in level]
            line = ("   ".join(prices)).center(max_width)
            print(line)
