using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApp1
{
    internal class Market
    {
        // Attributs
        public double S0;
        public double r;
        public double sigma;

        public Market(double S0, double r, double sigma)
        {
            this.S0 = S0;
            this.r = r;
            this.sigma = sigma;
        }

    }
}
