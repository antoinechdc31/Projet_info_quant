import Tree
import Market
import math


class Node :

    def __init__(self, underlying, tree, up = None, down = None) :
        self.tree = tree
        self.underlying = underlying
        self.next = self.calcul_next()
        self.proba = self.calcul_proba()
        self.up = up #noeud au dessus mais dans la même colonne
        self.down = down #noeud en dessous mais dans la même colonne
        self.Nup= None #noeud fils supérieur
        self.Nmid= None #noeud fils du milieu
        self.Ndown= None #noeud fils inférieur
        pass

    def create_brick(self, trunc, direction = "up") :

        Smid, Sup, Sdown = self.next

        if trunc : # Si on se trouve sur le tronc (partie centrale de l'arbre) on initialise tous les éléments de la brique
            self.Nmid = Node(Smid, self.tree, None, None)
            self.Nup = Node(Sup, self.tree, None, self.Nmid)
            self.Ndown = Node(Sdown, self.tree, self.Nmid, None)
            self.Nmid.up = self.Nup
            self.Nmid.down = self.Ndown
        elif direction == "up" and self.down is not None: # Sinon on regarde la direction (up ou down) et on initialise seulement les éléments manquants
            self.Ndown = self.down.Nmid # On récupère des noeud déjà créer pour éviter de recréer des noeuds et améliorer l'efficacité  
            self.Nmid = self.down.Nup
            self.Nup = Node(Sup, self.tree, down=self.Nmid)
            self.Nmid.up = self.Nup
            return
        
        elif direction == "down" and self.up is not None:
            self.Nup = self.up.Nmid
            self.Nmid = self.up.Ndown
            self.Ndown = Node(Sdown, self.tree, up=self.Nmid)
            self.Nmid.down = self.Ndown
            return
        pass


    def calcul_next(self) :  #Calcul les valueurs de l'actif sur les noeuds fils
        Smid = self.underlying * math.exp((self.tree.market.r ) * self.tree.dt)
        Sup = Smid * self.tree.alpha #Une fois qu'on a le noeud du milieu on peut calculer les autres en utilisant simplement l'alpha
        Sdown =  Smid/self.tree.alpha
        list_next = [Smid, Sup, Sdown]
        return list_next
    
    def forward(self) : #Calcul du prix dans le neoud fils du milieu
        esp = self.underlying * math.exp((self.tree.market.r) * self.tree.dt)
        return esp
    
    def esp(self) : #Espérence différente du forward dans le cas où il y a des dividendes
        esp = self.next[0] * self.proba[0] + self.next[1] * self.proba[1] + self.next[2] * self.proba[2]
        return esp
    
    def variance(self) : #Necessaire pour calculer les probas
        var = (self.underlying**2) * math.exp(2*(self.tree.market.r ) * self.tree.dt) * (math.exp(self.tree.market.sigma**2 *self.tree.dt) - 1) # =B16^2*EXP(2*Rate*DeltaT)*(EXP(Sigma^2*DeltaT)-1)
        return var

    def calcul_proba(self) : #Calcul les probas pour atteindre les noeuds fils
        v = self.variance()
        alpha = self.tree.alpha
        numerateur = (self.next[0]**(-2))*( v + self.next[0]**2 ) - 1 - ( alpha + 1)*((self.next[0]**(-1))*self.next[0] - 1)
        den = (1 - alpha) * ((alpha**(-2)) - 1)
        Pdown = numerateur/den 
        Pup = Pdown/alpha
        Pmid = ( 1 - (Pdown + Pup))
        return [Pmid, Pup, Pdown]
