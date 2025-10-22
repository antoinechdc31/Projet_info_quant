import Tree
import Market
import math

class Node : 

    def __init__(self, underlying, tree, level = 0, up = None, down = None, div = 0, proba_totale = 1) :

        self.tree = tree
        self.underlying = underlying
        self.level = level
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

    def create_brick(self, trunc, direction = "up", div = 0, is_div = False, epsilon=1e-8) :
        
        alpha = self.tree.alpha
        Smid = self.underlying * (math.exp(self.tree.market.r * self.tree.dt)) - div
        Sup = Smid * self.tree.alpha
        Sdown =  Smid/self.tree.alpha
        self.forward_price = self.forward() - div # on donne la valeur du forward 
        # au noeud pour y avoir acces dans le reste du code
        vf = False
        if self.proba_totale < epsilon:
            vf = True

        if trunc :
            
            self.create_trunc(trunc, div)

            self.mise_a_jour_proba_tot(div)

            return
            
        elif direction == "up" and self.down is not None :

            # Dans ce if on rentre si le noeud d'en bas est tronqué => 
            if self.down.Nup is None or self.down.Ndown is None :
                # le voisin du bas a été tronqué → on ne peut rien construire ici
                self.Ndown = self.down.Nmid
                Smid = self.Ndown.underlying * alpha
                self.Nmid = Node(Smid, self.tree, self.level, down=self.Ndown, div = 0, proba_totale=0)
                Sup = self.Nmid.underlying * self.tree.alpha
                if self.Nup is None:
                    self.Nup = Node(Sup, self.tree, self.level + 1, down=self.Nmid, div=0, proba_totale=0)
                self.Nmid.up = self.Nup
                
                self.recentrage_esp_up()
                self.mise_a_jour_proba_tot(div)

                return
            
            if vf :
                self.Nmid = self.down.Nup
                self.Ndown = None
                self.Nup = None
                return
            self.Ndown = self.down.Nmid
            self.Nmid = self.down.Nup
            Sup = self.Nmid.underlying * self.tree.alpha

            self.Nup = Node(Sup, self.tree, self.level + 1, down = self.Nmid, div = 0, proba_totale=0)
            self.Nmid.up = self.Nup

            
            self.mise_a_jour_proba_tot(div)

            self.recentrage_esp_up()
                
            return
        
        # Si on construit en venant du haut
        elif direction == "down" and self.up is not None :

            if self.up.Ndown is None:
                print(self.up)
                self.Nup = self.up.Nmid
                Smid = self.Nup.underlying / alpha
                self.Nmid = Node(Smid, self.tree, self.level, up=self.Nup, div = 0, proba_totale=0)
                # Création éventuelle du Ndown
                Sdown = self.Nmid.underlying / self.tree.alpha
                if self.Ndown is None:
                    self.Ndown = Node(Sdown, self.tree, self.level - 1, up=self.Nmid, div=0, proba_totale=0)
                self.Nmid.down = self.Ndown
                self.recentrage_esp_down()
                self.mise_a_jour_proba_tot(div)
                return
            if vf :
                self.Nmid = self.up.Ndown
                self.Ndown = None
                self.Nup = None
                return

            self.Nup = self.up.Nmid
            self.Nmid = self.up.Ndown
            Sdown = self.Nmid.underlying / self.tree.alpha
            self.Ndown = Node(Sdown, self.tree, self.level - 1, up=self.Nmid, div = 0, proba_totale=0)
            self.Nmid.down = self.Ndown

            self.mise_a_jour_proba_tot(div)

            self.recentrage_esp_down()
                
            return
        #print("fin create brick")
        pass

    def create_trunc(self, trunc, div) :
        Smid = self.underlying * (math.exp(self.tree.market.r * self.tree.dt)) - div
        Sup = Smid * self.tree.alpha
        Sdown =  Smid/self.tree.alpha

        prev = self if not trunc else None
        self.Nmid = NodeTrunc(Smid, self.tree, self.level, None, None, 0,proba_totale=0, prev=prev)
        self.Nup = Node(Sup, self.tree, self.level + 1, None, self.Nmid, 0,proba_totale=0)
        self.Ndown = Node(Sdown, self.tree, self.level - 1, self.Nmid, None, 0,proba_totale=0)
        self.Nmid.up = self.Nup
        self.Nmid.down = self.Ndown
    
    def mise_a_jour_proba_tot(self, div) :

        Pmid, Pup, Pdown = self.calcul_proba(div)

        # Met à jour les probabilités cumulées
        self.Nup.proba_totale  += self.proba_totale * Pup
        self.Nmid.proba_totale += self.proba_totale * Pmid
        self.Ndown.proba_totale += self.proba_totale * Pdown

        pass

    def recentrage_esp_up(self) :

        alpha = self.tree.alpha

        if self.forward_price > self.Nmid.underlying * (1 + alpha) / 2:
                
                self.Ndown = self.Nmid
                self.Nmid = self.Nmid.up
                Sup = self.Nmid.underlying * self.tree.alpha
                self.Nup = Node(Sup, self.tree, self.level + 1, down = self.Nmid, div = 0, proba_totale=0)
                self.Nmid.up = self.Nup

        if self.forward_price < self.Nmid.underlying * ((1 + 1/alpha) / 2):
            
            self.Nup = self.Nmid
            self.Ndown = self.Ndown.down
            self.Nmid = self.Nmid.down

        pass


    def recentrage_esp_down(self) :
        
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
            self.Ndown = Node(Sdown, self.tree, self.level - 1, up=self.Nmid, div = 0, proba_totale=0)
            self.Nmid.down = self.Ndown

    def forward(self) :
        esp = self.underlying * math.exp(self.tree.market.r * self.tree.dt) 
        return esp
    
    def esp(self, div = 0) :
        esp = self.Nmid.underlying * self.calcul_proba(div)[0] + self.Nup.underlying * self.calcul_proba(div)[1] + self.Ndown.underlying * self.calcul_proba(div)[2]
        return esp
    
    def variance(self) :
        var = (self.underlying**2) * math.exp(2*self.tree.market.r * self.tree.dt) * (math.exp(self.tree.market.sigma**2 *self.tree.dt) - 1) # =B16^2*EXP(2*Rate*DeltaT)*(EXP(Sigma^2*DeltaT)-1)
        return var

    def calcul_proba(self, div = 0) :

        v = self.variance()
        alpha = self.tree.alpha

        Smid = self.Nmid.underlying 
        esp = self.forward_price

        Pdown = (Smid**(-2) * (v + esp**(2)) - 1 - (alpha + 1)*(Smid**(-1) * esp - 1)) / ((1 - alpha)*(alpha**(-2) - 1))

        Pup = ((Smid**(-1) * esp - 1) - (alpha**(-1) - 1)*Pdown) / (alpha - 1)
        Pmid = 1 - Pup - Pdown

        if Pmid<0 or Pup<0 or Pdown<0 or Pmid>1 or Pup>1 or Pdown>1 :
              print("Attention !!!!!!!!!!!!")
              print(Pmid, Pup, Pdown)
              print(alpha)
              print(self.Nmid.underlying, self.Nup.underlying, self.Ndown.underlying)
            
        return [Pmid, Pup, Pdown]



class NodeTrunc(Node) :
    
    def __init__(self, underlying, tree, level=0, up=None, down=None, div=0, proba_totale = 1, prev=None):
        super().__init__(underlying, tree, level, up, down, div, proba_totale)
        self.prev = prev