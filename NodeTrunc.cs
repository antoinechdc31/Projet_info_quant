using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApp1
{
    internal class NodeTrunc : Node
    {
        public NodeTrunc prev { get; set; }

        public NodeTrunc(double underlying, Tree tree,
                         Node up = null, Node down = null, double div = 0,
                         double proba_totale = 1, NodeTrunc prev = null) // on ajoute un attribut prev 
            // pour donner le noeud précédent du tronc
            : base(underlying, tree, up, down, div, proba_totale)
        {
            this.prev = prev;
        }
    }
}
