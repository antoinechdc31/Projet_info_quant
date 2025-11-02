import Tree
import Market
import math

class Node : 

    def __init__(self, underlying, tree, up = None, down = None, div = 0, proba_totale = 1) :

        self.tree = tree
        self.underlying = underlying
        self.up = up
        self.down = down
        self.Nup = None
        self.Ndown = None
        self.Nmid = None
        self.option_value = None
        self.forward_price = 0
        self.div = div
        self.proba_totale = proba_totale
        pass

    def create_brick(self, trunc, direction = "up", div = 0, epsilon=1e-8) :
        
        alpha = self.tree.alpha
        self.forward_price = self.forward() - div # on donne la valeur du forward 
        # au noeud pour y avoir acces dans le reste du code
        vf = False # bool pour savoir si on doit faire un prunning
        if self.proba_totale < epsilon: # si la proba est inferieur a notre epsilon
            vf = True # on met à vrai notre bool et on met les autres noeuds en none
            self.Ndown = None
            self.Nup = None

        if trunc :
            
            self.create_trunc(trunc, div) # on crée le tronc 
            return
            
        elif direction == "up" and self.down is not None :

            # Dans ce if on rentre si le noeud d'en bas est tronqué => 
            if self.down.Nup is None or self.down.Ndown is None :
                self.if_prun_up(alpha, div)
                return
            if vf : # si on doit tronquer le noeud actuel
                self.Nmid = self.down.Nup
                return
            
            self.move_up(div) # sinon, on fait le move up classique
            return
        
        # direction down (de haut en bas)
        elif direction == "down" and self.up is not None :
            # si le noeud du dessus est tronqué
            if self.up.Ndown is None:
                self.if_prun_down(alpha, div)
                return
            if vf : # si on doit tronquer notre noeud actuel
                self.Nmid = self.up.Ndown
                return

            # sinon on move down commme d'habitude
            self.move_down(div) 
                
            return
        pass

    def create_trunc(self, trunc, div) :
        # creation des valeurs a injecter dans notre noeud
        Smid = self.underlying * (math.exp(self.tree.market.r * self.tree.dt)) - div
        Sup = Smid * self.tree.alpha
        Sdown =  Smid/self.tree.alpha

        prev = self # on crée le variable qui contiendra le noeuf d'avant (celui actuel)
        self.Nmid = NodeTrunc(Smid, self.tree, None, None, 0,proba_totale=0, prev=prev) # creation de chaque noeud
        self.Nup = Node(Sup, self.tree, None, self.Nmid, 0,proba_totale=0)
        self.Ndown = Node(Sdown, self.tree, self.Nmid, None, 0,proba_totale=0)
        self.Nmid.up = self.Nup # liaison des noeuds
        self.Nmid.down = self.Ndown

        self.mise_a_jour_proba_tot(div) # on met a jour les probas
    
    def if_prun_up(self, alpha, div) :
        """
        fonction appliquée lorsque le noeud du dessous a été tronqué donc 
        on crée le mid et le up grace à la formule du alpha
        """
        self.Ndown = self.down.Nmid
        Smid = self.Ndown.underlying * alpha
        self.Nmid = Node(Smid, self.tree, down=self.Ndown, div = 0, proba_totale=0)
        Sup = self.Nmid.underlying * self.tree.alpha
        if self.Nup is None:
            self.Nup = Node(Sup, self.tree, down=self.Nmid, div=0, proba_totale=0)
        self.Nmid.up = self.Nup
        
        self.recentrage_esp_up() # on recentre
        self.mise_a_jour_proba_tot(div) # et on met à jour les probas

    def if_prun_down(self, alpha, div) :
        """
        fonction appliquée lorsque le noeud du dessus a été tronqué donc 
        on crée le mid et le down grace à la formule du alpha
        """
        self.Nup = self.up.Nmid
        Smid = self.Nup.underlying / alpha
        self.Nmid = Node(Smid, self.tree, up=self.Nup, div = 0, proba_totale=0)
        # Création du Ndown
        Sdown = self.Nmid.underlying / self.tree.alpha
        if self.Ndown is None:
            self.Ndown = Node(Sdown, self.tree, up=self.Nmid, div=0, proba_totale=0)
        self.Nmid.down = self.Ndown

        self.recentrage_esp_down() # recnetrage en esperance
        self.mise_a_jour_proba_tot(div) # mise à jour des porba totale

    def move_up(self, div) :
        """
        creation des noeuds enfants (next) lorsqu'on va vers le haut
        """
        self.Ndown = self.down.Nmid
        self.Nmid = self.down.Nup
        Sup = self.Nmid.underlying * self.tree.alpha # creation du up grace à la formule
        # du alpha
        self.Nup = Node(Sup, self.tree, down = self.Nmid, div = 0, proba_totale=0)
        self.Nmid.up = self.Nup

        self.mise_a_jour_proba_tot(div)
        self.recentrage_esp_up()
        pass

    def move_down(self,div) :
        """
        creation des noeuds enfants lorsqu'on va vers le bas
        """
        self.Nup = self.up.Nmid # on donne la valeur au nup
        self.Nmid = self.up.Ndown # nmid
        Sdown = self.Nmid.underlying / self.tree.alpha # et on crée le down
        self.Ndown = Node(Sdown, self.tree, up=self.Nmid, div = 0, proba_totale=0)
        self.Nmid.down = self.Ndown

        self.mise_a_jour_proba_tot(div)
        self.recentrage_esp_down()
        pass

    def mise_a_jour_proba_tot(self, div) :

        Pmid, Pup, Pdown = self.calcul_proba(div) # recupération des probas

        # Met à jour les probabilités cumulées
        self.Nup.proba_totale  += self.proba_totale * Pup # calcul et mise à jour des probas totales
        self.Nmid.proba_totale += self.proba_totale * Pmid
        self.Ndown.proba_totale += self.proba_totale * Pdown

        pass

    def recentrage_esp_up(self) :

        alpha = self.tree.alpha

        if self.forward_price > self.Nmid.underlying * (1 + alpha) / 2: # si on doit décaler vers le haut
                
                self.Ndown = self.Nmid
                self.Nmid = self.Nmid.up # on move up
                Sup = self.Nmid.underlying * self.tree.alpha
                self.Nup = Node(Sup, self.tree, down = self.Nmid, div = 0, proba_totale=0)
                self.Nmid.up = self.Nup

        if self.forward_price < self.Nmid.underlying * ((1 + 1/alpha) / 2): # si on doit decaler vers le bas
            
            self.Nup = self.Nmid # on move down
            self.Ndown = self.Ndown.down
            self.Nmid = self.Nmid.down

        pass

    def recentrage_esp_down(self) :
        """
        fonction qui sert à faire le recentrage en esperance lorsque qu'on est dans la direction down
        elle va verifier si on doit décaler vers le haut et le bas en fonction de l'esp et faire ce décalage proprement
        """
        alpha = self.tree.alpha
        
        val = self.forward_price
        if val> self.Nmid.underlying * (1 + alpha) / 2:
            
            self.Ndown = self.Nmid
            self.Nmid = self.Nmid.up
            self.Nup = self.Nup.up

        if val < self.Nmid.underlying * ((1 + 1/alpha) / 2):
            self.Nup = self.Nmid
            self.Nmid = self.Nmid.down
            Sdown = self.Nmid.underlying / self.tree.alpha
            self.Ndown = Node(Sdown, self.tree, up=self.Nmid, div = 0, proba_totale=0)
            self.Nmid.down = self.Ndown

    def forward(self) :
        esp = self.underlying * math.exp(self.tree.market.r * self.tree.dt) 
        return esp
    
    def esp(self, div = 0) : # calcul esp
        esp = self.Nmid.underlying * self.calcul_proba(div)[0] \
              + self.Nup.underlying * self.calcul_proba(div)[1] \
              + self.Ndown.underlying * self.calcul_proba(div)[2]
        # application de la formule d'esperance
        return esp
    
    def variance(self) :
        var = (self.underlying**2) \
            * math.exp(2*self.tree.market.r * self.tree.dt) \
            * (math.exp(self.tree.market.sigma**2 *self.tree.dt) - 1)
        return var

    def calcul_proba(self, div = 0) :
        """
        fonctionc alcule proba qui s'applique au cas avec et sans div : 
        elle applique les formule du cours en recuperant la avr et l'esp du noeud
        """
        v = self.variance()
        alpha = self.tree.alpha

        Smid = self.Nmid.underlying 
        esp = self.forward_price

        Pdown = (Smid**(-2) * (v + esp**(2)) - 1 - (alpha + 1)*(Smid**(-1) * esp - 1)) / ((1 - alpha)*(alpha**(-2) - 1))

        Pup = ((Smid**(-1) * esp - 1) - (alpha**(-1) - 1)*Pdown) / (alpha - 1)
        Pmid = 1 - Pup - Pdown

        if Pmid<0 or Pup<0 or Pdown<0 or Pmid>1 or Pup>1 or Pdown>1 : # verification des probas negatives
            print("Attention !!!!!!!!!!!!")
            print(Pmid, Pup, Pdown)
            print(alpha)
            print(self.Nmid.underlying, self.Nup.underlying, self.Ndown.underlying)
            
        return [Pmid, Pup, Pdown]

"""
création de la classe Node Trunc qui herite de la classe Node, qui defini en plus un noeud
precédent
"""
class NodeTrunc(Node) :
    
    def __init__(self, underlying, tree, up=None, down=None, div=0, proba_totale = 1, prev=None):
        super().__init__(underlying, tree, up, down, div, proba_totale)
        self.prev = prev