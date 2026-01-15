using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;
using static System.Math;
using static System.Net.Mime.MediaTypeNames;

namespace ConsoleApp1
{
    internal class Tree
    {
        public Market market { get; set; }
        public int N { get; set; }
        public double dt { get; set; }
        public double alpha { get; set; }
        public NodeTrunc root { get; set; }

        public Tree(Market market, int N, double delta_t)
        {
            this.market = market;
            this.N = N;
            this.dt = delta_t;
            this.alpha = Exp(market.sigma * Sqrt(3 * this.dt));
            this.root = new NodeTrunc(underlying: market.S0, tree: this, prev: null);
        }

        // ===================== METHODE DES BRIQUES =====================

        public NodeTrunc BuildColumns(NodeTrunc node_trunc, bool is_div_date = false, Option option = null)
        {
            double div;
            // création d'une colonne de l'arbre
            if (is_div_date) // si il y a des div on applique la valeur à la var div
            {
                div = option.Div;
                
            }
            else
            {
                div = 0;
            }

            node_trunc.CreateBrick(true, "up", div, is_div_date); // création du noeud trunc
            Node current_node = node_trunc.up; // on recupere le up

            while (current_node != null) // move up
            {
                current_node.CreateBrick(false, "up", div);
                current_node = current_node.up;
            }

            current_node = node_trunc.down;

            while (current_node != null) // move down
            {
                current_node.CreateBrick(false, "down", div);
                current_node = current_node.down;
            }

            NodeTrunc future_node_trunc = (NodeTrunc)node_trunc.Nmid;
            future_node_trunc.prev = node_trunc; // renvoie du futur noeud du tronc pour la prochaine colonne
            // correspond au Nmid de notre noeud du tronc actuel
            return future_node_trunc;
        }

        public void TreeConstruction2(Option option)
        {
            NodeTrunc node_trunc = this.root;
            double index = -1;

            if (option.IsDiv)
            {
                DateTime d0 = option.CalcDate;
                DateTime T = d0.AddDays(option.Mat * 365.0);
                double num = Math.Max(0, (option.DateDiv - d0).Value.Days);
                double den = Math.Max(1, (T - d0).Days); //  on calcul l'index ou l'on devra appliquer les div
                index = num / den;
            }

            bool div_already_applied = false;

            for (int i = 1; i <= this.N; i++)
            {
                bool is_div_date = false;

                if (option.IsDiv && !div_already_applied) // si la div doit etre appliquée 
                {
                    if (index > (double)i / this.N && index <= (double)(i + 1) / this.N)
                    {
                        is_div_date = true;
                        div_already_applied = true; // on met nos variables a True pour indiquer l'application des div
                    }
                }

                node_trunc = BuildColumns(node_trunc, is_div_date, option);
            }
        }

        public double PriceOptionRecursive(Option option)
        {
            TreeConstruction2(option);
            return PriceNode2(this.root, option); // appel de la fonction recursive
        }

        public double PriceNode2(Node node, Option option)
        {
            if (node == null) // si le noeud n'existe pas on retourne 0
                return 0.0;

            double val;
            if ((node.Nmid == null) || ((node.Nup == null) && (node.Ndown == null))) // si c'est la derniere colonne, on retourne le payoff
            {
                val = option.Payoff(node.underlying);
                node.option_value = val;
            }
            else
            {

                if (node.Nmid == null)
                {
                    val = option.Payoff(node.underlying);
                    node.option_value = val;
                }
                else
                {
                    double Vmid, Vup, Vdown;
                    //  si la valeur a deja ete calculé on la recupere sinon on la calcule pour chaque noeud next (mid, up et down)
                    if (node.Nmid.option_value.HasValue)
                        Vmid = node.Nmid.option_value.Value;
                    else
                    {
                        Vmid = PriceNode2(node.Nmid, option);
                        node.Nmid.option_value = Vmid;
                    }

                    if (node.Nup.option_value.HasValue)
                        Vup = node.Nup.option_value.Value;
                    else
                    {
                        Vup = PriceNode2(node.Nup, option);
                        node.Nup.option_value = Vup;
                    }

                    if (node.Ndown.option_value.HasValue)
                        Vdown = node.Ndown.option_value.Value;
                    else
                    {
                        Vdown = PriceNode2(node.Ndown, option);
                        node.Ndown.option_value = Vdown;
                    }

                    double[] probs = node.CalculProba(); // onc alcul les probas
                    double p_mid = probs[0];
                    double p_up = probs[1];
                    double p_down = probs[2];

                    double df = Exp(-this.market.r * this.dt); // facteur d'actualisation
                    double moy_pond = df * (p_mid * Vmid + p_up * Vup + p_down * Vdown); // formule de cours

                    if (option.Style.ToLower() == "american") // application de la formule au cas americain
                        val = Math.Max(option.Payoff(node.underlying), moy_pond);
                    else
                        val = moy_pond;
                }
            }


            node.option_value = val; // on met à jour la valeur
            return val;
        }

        public double PriceNodeBackward(Option option)
        {
            // function qui sert a calculer les valeurs des Noeud up mid et down dans el cadre de la valorisation

            NodeTrunc node_trunc_final = this.root;

            // on va jusq'à la dernière colonne (feuilles)
            while (node_trunc_final.Nmid != null)
                node_trunc_final = (NodeTrunc)node_trunc_final.Nmid;

            Node current = node_trunc_final;

            while (current != null)
            { // on valorise les feuilles
                current.option_value = option.Payoff(current.underlying);
                current = current.up;
            }

            current = node_trunc_final.down;

            while (current != null)
            { // on valorise les feuilles
                current.option_value = option.Payoff(current.underlying);
                current = current.down;
            }
            // on remonte colonne par colonne
            NodeTrunc node_trunc = node_trunc_final.prev;

            while (node_trunc != null)
            {
                current = node_trunc; // on price d'abord vers le haut
                while (current != null)
                {
                    double val;
                    if ((current.Nup != null) && (current.Ndown != null)) // si le noeud a pas été tronqué on le valorise avec la formule habituelle
                    {
                        val = PricingNoeudIndiv(option, current);
                    }
                    else
                    {
                        val = option.Payoff(current.underlying);
                    }
                    current.option_value = val;
                    current = current.up;
                }

                current = node_trunc.down; // puis on price vers le bas
                while (current != null)
                {
                    double val;
                    if ((current.Nup != null) && (current.Ndown != null))
                    {
                        val = PricingNoeudIndiv(option, current);
                    }
                    else
                    {
                        val = option.Payoff(current.underlying);
                    }
                    current.option_value = val;
                    current = current.down;
                }

                node_trunc = node_trunc.prev;
            }

            return this.root.option_value.Value;
        }

        public double PricingNoeudIndiv(Option option, Node current)
        {
            // on recupere les valuers des noeuds next pour appliquer
            // la formule de valorisation
            double Vmid = current.Nmid.option_value.Value;
            double Vup = current.Nup.option_value.Value;
            double Vdown = current.Ndown.option_value.Value;

            double[] probs = current.CalculProba();
            double p_mid = probs[0];
            double p_up = probs[1];
            double p_down = probs[2];

            double df = Exp(-this.market.r * this.dt);
            double moy_pond = df * (p_mid * Vmid + p_up * Vup + p_down * Vdown);

            double val = option.Style.ToLower() == "american"
                ? Math.Max(option.Payoff(current.underlying), moy_pond)
                : moy_pond;

            return val;
        }


        private const double EPSILON = 0.01; // 1% de variation par défaut

        public double Delta(Option option, double hRatio = 0.01)
        { // application de la formule des differences finies vu en cours
            double S0 = market.S0;
            double h = S0 * hRatio; // calcul de h

            var market_up = new Market(S0 + h, market.r, market.sigma); // on applique le decalage a nos nv marchés
            var market_down = new Market(S0 - h, market.r, market.sigma);

            var tree_up = new Tree(market_up, N, dt); // creation des arbres
            var tree_down = new Tree(market_down, N, dt);

            tree_up.TreeConstruction2(option); // on construit les arbres
            tree_down.TreeConstruction2(option);

            double price_up = tree_up.PriceOptionRecursive(option); // on price les options
            double price_down = tree_down.PriceOptionRecursive(option);

            double delta = (price_up - price_down) / (2 * h); // formule
            Console.WriteLine($"Δ (Delta) = {delta:F6}");
            return delta;
        }

        public double Gamma(Option option, double hRatio = 0.01)
        {
            // application de la formule des differences finies vu en cours
            double S0 = market.S0;
            double h = S0 * hRatio; // calcul de h

            var market_up = new Market(S0 + h, market.r, market.sigma); // on applique le decalage a nos nv marchés
            var market_down = new Market(S0 - h, market.r, market.sigma);
            var market_0 = new Market(S0, market.r, market.sigma);

            var tree_up = new Tree(market_up, N, dt); // creation des arbres
            var tree_down = new Tree(market_down, N, dt);
            var tree_0 = new Tree(market_0, N, dt);

            tree_up.TreeConstruction2(option); // on construit les arbres
            tree_down.TreeConstruction2(option);
            tree_0.TreeConstruction2(option);

            double price_up = tree_up.PriceOptionRecursive(option); // on price les options
            double price_down = tree_down.PriceOptionRecursive(option);
            double price_0 = tree_0.PriceOptionRecursive(option);

            double gamma = (price_up - 2 * price_0 + price_down) / (h * h);
            Console.WriteLine($"Γ (Gamma) = {gamma:F6}");
            return gamma;
        }

        public double Vega(Option option, double hVol = 0.01)
        {
            double sigma = market.sigma;
            double r = market.r;
            double S0 = market.S0;

            var market_up = new Market(S0, r, sigma * (1 + hVol));
            var market_down = new Market(S0, r, sigma * (1 - hVol));

            var tree_up = new Tree(market_up, N, dt);
            var tree_down = new Tree(market_down, N, dt);

            tree_up.TreeConstruction2(option);
            tree_down.TreeConstruction2(option);

            double price_up = tree_up.PriceOptionRecursive(option);
            double price_down = tree_down.PriceOptionRecursive(option);

            double vega = (price_up - price_down) / (2 * sigma * hVol);
            Console.WriteLine($"Vega (ν) = {vega:F6}");
            return vega;
        }

        public double Volga(Option option, double hVol = 0.05)
        {
            double sigma = market.sigma;
            double r = market.r;
            double S0 = market.S0;

            var market_up = new Market(S0, r, sigma * (1 + hVol));
            var market_down = new Market(S0, r, sigma * (1 - hVol));
            var market_0 = new Market(S0, r, sigma);

            var tree_up = new Tree(market_up, N, dt);
            var tree_down = new Tree(market_down, N, dt);
            var tree_0 = new Tree(market_0, N, dt);

            tree_up.TreeConstruction2(option);
            tree_down.TreeConstruction2(option);
            tree_0.TreeConstruction2(option);

            double price_up = tree_up.PriceOptionRecursive(option);
            double price_down = tree_down.PriceOptionRecursive(option);
            double price_0 = tree_0.PriceOptionRecursive(option);

            double volga = (price_up - 2 * price_0 + price_down) / Math.Pow(sigma * hVol, 2);
            Console.WriteLine($"Volga (Λ) = {volga:F6}");
            return volga;
        }
    }
}
      
