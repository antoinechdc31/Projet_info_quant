import Tree
import Market
import math


class Node :

    def __init__(self, underlying, tree, level = 0, up = None, down = None, div = 0,proba_totale=0.0, proba_locale=None) :
        self.tree = tree
        self.underlying = underlying
        self.level = level
        self.up = up
        self.down = down
        self.next = self.calcul_next(div)
        self.Nup = None
        self.Ndown = None
        self.Nmid = None
        self.option_value= None
        self.proba_totale = proba_totale   # probabilité d'arriver ici depuis la racine
        #self.proba_locale = proba_locale   # probabilité de transition depuis le parent
        self.proba = self.calcul_proba(div)
        pass

    def create_brick(self, trunc, direction="up", div=0, is_div=False, proba_min=0.01):
        # Calcul des prix futurs
        if not is_div:
            Smid, Sup, Sdown = self.next
        else:
            Smid, Sup, Sdown = self.calcul_next(div, is_div)
            self.next = [Smid, Sup, Sdown]

        # Si le parent est trop improbable
        if self.proba_totale < proba_min:
            # On ne crée que le mid
            self.Nmid = NodeTrunc(Smid, self.tree, self.level, up=None, down=None, div=div, prev=self)
            self.Nmid.proba_totale = self.proba_totale       # on conserve la proba totale du parent
            self.Nmid.proba[0] = 1.0                        # la proba locale du mid = 1
            self.Nup = None
            self.Ndown = None
            return

        # Sinon, création normale des 3 enfants
        if trunc:
            self.Nmid = NodeTrunc(Smid, self.tree, self.level, up=None, down=None, div=div, prev=self)
            self.Nmid.proba_totale = self.proba_totale * self.proba[0]

            self.Nup = Node(Sup, self.tree, self.level + 1, up=None, down=self.Nmid, div=div)
            self.Nup.proba_totale = self.proba_totale * self.proba[1]

            self.Ndown = Node(Sdown, self.tree, self.level - 1, up=self.Nmid, down=None, div=div)
            self.Ndown.proba_totale = self.proba_totale * self.proba[2]

            self.Nmid.up = self.Nup
            self.Nmid.down = self.Ndown

    def calcul_next(self, div = 0, is_div = False) :

        if not is_div :

            Smid = self.underlying * (math.exp(self.tree.market.r * self.tree.dt)) - div
            Sup = Smid * self.tree.alpha
            Sdown =  Smid/self.tree.alpha
            list_next = [Smid, Sup, Sdown]

        else :
            alpha = self.tree.alpha
            r = self.tree.market.r
            dt = self.tree.dt

            if self.level == 0 :
                Smid = self.underlying * math.exp(r * dt) - div
                self.tree.Smid_tronc = Smid  # mémoriser

            elif self.tree.Smid_tronc is not None :

                Smid = self.tree.Smid_tronc * (alpha ** self.level)

            else :
                raise ValueError
            
            Sup = Smid * alpha
            Sdown = Smid / alpha

            list_next = [Smid, Sup, Sdown]

        return list_next
    
    def forward(self) :
        esp = self.underlying * math.exp(self.tree.market.r * self.tree.dt)
        return esp
    
    def esp(self) :
        esp = self.next[0] * self.proba[0] + self.next[1] * self.proba[1] + self.next[2] * self.proba[2]
        return esp
    
    def variance(self) :
        var = (self.underlying**2) * math.exp(2*self.tree.market.r * self.tree.dt) * (math.exp(self.tree.market.sigma**2 *self.tree.dt) - 1) # =B16^2*EXP(2*Rate*DeltaT)*(EXP(Sigma^2*DeltaT)-1)
        return var

    def calcul_proba(self, div = 0) :
        v = self.variance()
        alpha = self.tree.alpha

        if div == 0 :
            numerateur = (self.next[0]**(-2))*( v + self.next[0]**2 ) - 1 - ( alpha + 1)*((self.next[0]**(-1))*self.next[0] - 1)
            den = (1 - alpha) * ((alpha**(-2)) - 1)
            Pdown = numerateur/den
            Pup = Pdown/alpha
            Pmid = ( 1 - (Pdown + Pup))

        else : 
            Smid = self.next[0] # sur le tronc Smid = esp
            esp = self.forward() - div
            Smid = self.next[0] # car ici c'est que le fwd
            esp = Smid - div

            numerateur = (Smid**(-2)) * (v + esp**2) - 1 - (alpha + 1) * ((Smid**(-1)) * esp - 1)
            den = (1 - alpha) * (alpha**(-2) - 1)
            Pdown = numerateur / den

            # Formule
            Pup = ((Smid**(-1)) * esp - 1 - (alpha**(-1) - 1) * Pdown) / (alpha - 1)
            # Pmid
            Pmid = 1 - (Pdown + Pup)

        if Pmid < 0 or Pup < 0 or Pdown < 0 or Pmid > 1 or Pup > 1 or Pdown > 1 :
            print("Probabilité négative ou > 1")

        return [Pmid, Pup, Pdown]
    
   
    
class NodeTrunc(Node) :
    def __init__(self, underlying, tree, level = 0, up = None, down = None, div = 0 , prev = None) :
        super().__init__(underlying, tree, level, up, down, div)
        self.prev = prev
        pass