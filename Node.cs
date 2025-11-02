using System;
using System.Collections.Generic;
using System.ComponentModel.Design;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;
using static System.Math;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace ConsoleApp1
{
    internal class Node
    {
        public Tree tree { get; set; }
        public double underlying { get; set; }
        public Node up { get; set; }
        public Node down { get; set; }
        public Node Nup { get; set; }
        public Node Ndown { get; set; }
        public Node Nmid { get; set; }
        public double? option_value { get; set; }
        public double forward_price { get; set; }
        public double div { get; set; }
        public double proba_totale { get; set; }

        public Node(double underlying, Tree tree, Node up = null, Node down = null, double div = 0, double proba_totale = 1)
        {
            this.tree = tree;
            this.underlying = underlying;
            this.up = up;
            this.down = down;
            this.Nup = null;
            this.Ndown = null;
            this.Nmid = null;
            this.option_value = null;
            this.forward_price = 0;
            this.div = div;
            this.proba_totale = proba_totale;
        }

        public void CreateBrick(bool trunc, string direction = "up", double div = 0, bool is_div = false)
        {
            double alpha = this.tree.alpha;
            double Smid = this.underlying * Exp(this.tree.market.r * this.tree.dt) - div;
            double Sup = Smid * this.tree.alpha;
            double Sdown = Smid / this.tree.alpha;

            this.forward_price = Forward() - div; // valeur du forward pour y avoir acces dans le reste du code
            
            bool prunning = false; // indicateur de prunning, false si pas besoin de l'apliquer true sinon
            if (this.proba_totale < 1e-10)
            {
                prunning = true;
                this.Ndown = null; // on donne deja les valeurs des noeuds down et up, None, dans le cas
                // ou on applique le prunning
                this.Nup = null;
            }
            if (trunc) // on crée le tronc avec les 3 noeuds associés qui serviront de base pour las uite
            {
                this.Nmid = new NodeTrunc(Smid, this.tree,  null, null, 0, 1, (NodeTrunc)this);
                this.Nup = new Node(Sup, this.tree,  null, this.Nmid, 0);
                this.Ndown = new Node(Sdown, this.tree, this.Nmid, null, 0);
                this.Nmid.up = this.Nup;
                this.Nmid.down = this.Ndown;
            }
            else if (direction == "up" && this.down != null) // direction up, equivalent move up
            {

                if ((this.down.Nup is null) || (this.down.Ndown is null)) // si le noeud du dessous à ete tronqué
                {
                    this.Ndown = this.down.Nmid; // on fait le décalage necessaire
                    Smid = this.Ndown.underlying * this.tree.alpha; // on calcul les valeurs avec le alpha
                    this.Nmid = new Node(Smid, this.tree, null, this.Ndown, 0, 0);
                    Sup = this.Nmid.underlying * this.tree.alpha;
                    this.Nup = new Node(Sup, this.tree, null, this.Nmid, 0, 0);
                    this.Nmid.up = this.Nup; // création des liaisons
                    this.mise_a_jour_proba(div); // on met à jour les proba totale
                }
                else if(prunning)
                {
                    this.Nmid = this.down.Nup; // on donne la valeur du mid grace au down
                    return;
                }
                else
                { // sinon on fait le move up habituel
                   this.Ndown = this.down.Nmid;
                    this.Nmid = this.down.Nup;
                    Sup = this.Nmid.underlying * this.tree.alpha;
                    this.Nup = new Node(Sup, this.tree, null, this.Nmid, 0);
                    this.Nmid.up = this.Nup;
                    this.mise_a_jour_proba(div);
                }
                // recentrage en espérance
                if (this.forward_price > this.Nmid.underlying * (1 + alpha) / 2) // decalage vers le haut
                {
                    this.Ndown = this.Nmid;
                    this.Nmid = this.Nmid.up;
                    Sup = this.Nmid.underlying * this.tree.alpha;
                    this.Nup = new Node(Sup, this.tree, null, this.Nmid, 0);
                    this.Nmid.up = this.Nup;
                }
                if (this.forward_price < this.Nmid.underlying * ((1 + 1 / alpha) / 2)) // decalage vers le bas
                {
                    this.Nup = this.Nmid;
                    this.Ndown = this.Ndown.down;
                    this.Nmid = this.Nmid.down;
                }

                return;
            }
            else if (direction == "down" && this.up != null) // move down
            {
                if ((this.up.Nup is null) || (this.up.Ndown is null)) // si le noeud du dessus a ete tronqué
                {
                    this.Nup = this.up.Nmid;
                    Smid = this.Nup.underlying / this.tree.alpha;
                    this.Nmid = new Node(Smid, this.tree, this.Nup,null, 0, 0);
                    Sdown = this.Nmid.underlying / this.tree.alpha;
                    this.Ndown = new Node(Sdown, this.tree, this.Nmid, null , 0, 0);
                    this.Nmid.down = this.Ndown;
                    this.mise_a_jour_proba(div);
                }
                else if (prunning)
                {
                    this.Nmid = this.up.Ndown;
                    return;
                }
                else
                { // move down habituel
                    this.Nup = this.up.Nmid;
                    this.Nmid = this.up.Ndown;
                    Sdown = this.Nmid.underlying / this.tree.alpha;
                    this.Ndown = new Node(Sdown, this.tree, this.Nmid, null, 0);
                    this.Nmid.down = this.Ndown;
                    this.mise_a_jour_proba(div);
                }

                double val = this.forward_price;
                // recentrage en espérance
                if (val > this.Nmid.underlying * (1 + alpha) / 2) // decalage vers le haut
                {
                    this.Ndown = this.Nmid;
                    this.Nmid = this.Nmid.up;
                    this.Nup = this.Nup.up;
                }
                if (val < this.Nmid.underlying * ((1 + 1 / alpha) / 2)) // decalage vers le bas
                {
                    this.Nup = this.Nmid;
                    this.Nmid = this.Nmid.down;
                    Sdown = this.Nmid.underlying / this.tree.alpha;
                    this.Ndown = new Node(Sdown, this.tree, this.Nmid, null, 0);
                    this.Nmid.down = this.Ndown;
                }

                return;
            }
        }

        public void mise_a_jour_proba(double div = 0)
        {

            double[] probs = this.CalculProba(div); // recuperation des probas de chaque noeud
            double p_mid = probs[0];
            double p_up = probs[1];
            double p_down = probs[2];

            // met à jour les probabilités cumulées
            this.Nup.proba_totale += this.proba_totale * p_up; // calcul est mise à jour des probas totales pour chaque noeud
            this.Nmid.proba_totale += this.proba_totale * p_mid;
            this.Ndown.proba_totale += this.proba_totale * p_down;

        }

        public double Forward()
        {
            double esp = this.underlying * Exp(this.tree.market.r * this.tree.dt);
            return esp;
        }

        public double Esp(double div = 0) // application formule de l'esp usuelle
        {
            var probs = CalculProba(div);
            double esp = this.Nmid.underlying * probs[0] + this.Nup.underlying * probs[1] + this.Ndown.underlying * probs[2];
            return esp;
        }

        public double Variance()
        {
            double var = Pow(this.underlying, 2) * Exp(2 * this.tree.market.r * this.tree.dt) *
                            (Exp(Pow(this.tree.market.sigma, 2) * this.tree.dt) - 1);
            return var;
        }

        public double[] CalculProba(double div = 0)
        {
            //fonctionc alcule proba qui s'applique au cas avec et sans div : 
            //elle applique les formule du cours en recuperant la avr et l'esp du noeud
            double v = this.Variance();
            double alpha = this.tree.alpha;

            double Smid = this.Nmid.underlying;
            double esp = this.forward_price;

            double Pdown = (Pow(Smid, -2) * (v + Pow(esp, 2)) - 1 - (alpha + 1) * (Pow(Smid, -1) * esp - 1)) /
                            ((1 - alpha) * (Pow(alpha, -2) - 1));

            double Pup = ((Pow(Smid, -1) * esp - 1) - (Pow(alpha, -1) - 1) * Pdown) / (alpha - 1);
            double Pmid = 1 - Pup - Pdown;


            return new double[] { Pmid, Pup, Pdown };
        }
        
    }
}
