using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApp1
{
    internal class Option
    {
        
        public double Strike { get; set; }     
        public string OptType { get; set; } 
        public string Style { get; set; }      
        public double Mat { get; set; }   
        public bool IsDiv { get; set; }      
        public double Div { get; set; }       
        public DateTime? DateDiv { get; set; }    
        public DateTime CalcDate { get; set; }  

        public Option(double K, double mat, string optType, string style,
                        bool isDiv = false, double div = 0, DateTime? dateDiv = null,
                        DateTime? calcDate = null)
        {
            Strike = K;
            OptType = optType;
            Style = style;
            Mat = mat;
            IsDiv = isDiv;
            Div = div;
            DateDiv = dateDiv;
            CalcDate = calcDate ?? DateTime.Now;  // s'il y a pas de date ca sera ajd
        }

        public double Payoff(double S)
        {
            if (OptType.ToLower() == "call") // formule des payoffs habituelle, une pour
                // call et l'autre put
                return Math.Max(S - Strike, 0);
            else if (OptType.ToLower() == "put")
                return Math.Max(Strike - S, 0);
            else
                throw new ArgumentException("Type d'option non reconnu");
        }

    }
}
