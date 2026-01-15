using ConsoleApp1;
using System;
using System.ComponentModel;
using static System.Math;

class Program
{
    static void Main(string[] args)
    {

        console_prix();

        //// --- Dates importantes ---
        //DateTime calcDate = new DateTime(2025, 9, 1);
        //DateTime maturity = new DateTime(2026, 9, 1);
        //DateTime dateDiv = new DateTime(2026, 4, 21);

        //// --- Discrétisation temporelle ---
        //int n = 400;
        //double mat = (maturity - calcDate).TotalDays / 365.0;   // maturité en années (~1.00)
        //double deltaT = mat / n;                                // pas de temps

        //// --- Paramètres du marché ---
        //Market market = new Market(S0: 100, r: 0.05, sigma: 0.3);
        //Tree tree = new Tree(market, N: n, delta_t: deltaT);

        //// --- Option avec dividende discret ---
        //Option option = new Option(
        //    K: 102,
        //    mat: mat,
        //    optType: "call",
        //    style: "european",
        //    isDiv: true,
        //    div: 3,
        //    dateDiv: dateDiv,
        //    calcDate: calcDate
        //);

        //// --- Pricing (méthode récursive et backward) ---
        //double prixEuro = tree.PriceOptionRecursive(option);
        //double prixBack = tree.PriceNodeBackward(option);

        //// --- Comparaison avec un prix Black-Scholes (sans div) ---
        //double prixBS = BlackScholes(S0: 100, K: 102, T: mat, r: 0.05, sigma: 0.3, type: "call");

        //// --- Affichage ---
        //Console.WriteLine($"Date de calcul : {calcDate:yyyy-MM-dd}");
        //Console.WriteLine($"Date du dividende : {dateDiv:yyyy-MM-dd}");
        //Console.WriteLine($"Maturité : {maturity:yyyy-MM-dd} ({mat:F4} an)\n");
        //Console.WriteLine($"Prix via arbre trinomial (avec div) : {prixEuro:F6}");
        //Console.WriteLine($"Prix backward (avec div)            : {prixBack:F6}");
        //Console.WriteLine($"Prix Black-Scholes (sans div)       : {prixBS:F6}");
        //Console.WriteLine("---------------------------------------------");
        //Console.WriteLine("→ Le prix avec dividende doit être PLUS FAIBLE");
        //Console.WriteLine("  car le sous-jacent chute à la date du dividende.");
    }

    static void console_prix()
    {
        //Console.ForegroundColor = ConsoleColor.Cyan;
        Console.WriteLine("═══════════════════════════════════════════════════════════════════════════════");
        Console.WriteLine("                        PRICING D'UNE OPTION PAR ARBRE TRINOMIAL              ");
        Console.WriteLine("═══════════════════════════════════════════════════════════════════════════════\n");
        Console.ResetColor();

        // === Saisie utilisateur ===
        Console.Write("Sous-jacent initial S₀      : ");
        double S0 = double.Parse(Console.ReadLine() ?? "100");

        Console.Write("Taux sans risque r (ex: 0,05): ");
        double r = double.Parse(Console.ReadLine() ?? "0.05");

        Console.Write("Volatilité σ (ex: 0,3)      : ");
        double sigma = double.Parse(Console.ReadLine() ?? "0.3");

        Console.Write("Strike K                    : ");
        double K = double.Parse(Console.ReadLine() ?? "100");

        Console.Write("Dividende discret (ex: 3)   : ");
        double div = double.Parse(Console.ReadLine() ?? "3");

        Console.Write("Nombre de pas N (ex: 400)   : ");
        int N = int.Parse(Console.ReadLine() ?? "400");

        Console.Write("\nDate de calcul (AAAA-MM-JJ) : ");
        DateTime calcDate = DateTime.Parse(Console.ReadLine() ?? "2025-09-01");

        Console.Write("Date de maturité (AAAA-MM-JJ): ");
        DateTime maturity = DateTime.Parse(Console.ReadLine() ?? "2026-09-01");

        Console.Write("Date de dividende (AAAA-MM-JJ): ");
        DateTime dateDiv = DateTime.Parse(Console.ReadLine() ?? "2026-04-21");

        Console.Write("Type d'option (call/put)    : ");
        string optType = Console.ReadLine()?.ToLower() ?? "call";

        Console.Write("Style (european/american)   : ");
        string style = Console.ReadLine()?.ToLower() ?? "european";

        // === Calcul des paramètres ===
        double mat = (maturity - calcDate).TotalDays / 365.0;
        double deltaT = mat / N;

        Market market = new Market(S0, r, sigma);
        Tree tree = new Tree(market, N, deltaT);

        Option option = new Option(
            K: K,
            mat: mat,
            optType: optType,
            style: style,
            isDiv: div > 0,
            div: div,
            dateDiv: dateDiv,
            calcDate: calcDate
        );

        double prixEuro = tree.PriceOptionRecursive(option);
        double prixBack = tree.PriceNodeBackward(option);
        double prixBS = BlackScholes(S0, K, mat, r, sigma, optType);

        Console.ForegroundColor = ConsoleColor.Green;
        Console.WriteLine("\n═══════════════════════════════════════════════════════════════════════════════");
        Console.WriteLine($" Date de calcul       : {calcDate:yyyy-MM-dd}");
        Console.WriteLine($" Dividende            : {div} à la date {dateDiv:yyyy-MM-dd}");
        Console.WriteLine($" Maturité             : {maturity:yyyy-MM-dd}  (T = {mat:F4} an)");
        Console.WriteLine("───────────────────────────────────────────────────────────────────────────────");
        Console.WriteLine($" Prix arbre trinomial (récursif) : {prixEuro,15:F6}");
        Console.WriteLine($" Prix backward (avec div)        : {prixBack,15:F6}");
        Console.WriteLine($" Prix Black-Scholes (sans div)   : {prixBS,15:F6}");
        Console.WriteLine("\n=== GREEKS (via Tree) ===");
        double delta = tree.Delta(option);
        double gamma = tree.Gamma(option);
        double vega = tree.Vega(option);
        double volga = tree.Volga(option);
        Console.WriteLine("============================================\n");
        Console.ResetColor();

        Console.WriteLine("\nAppuyez sur une touche pour quitter...");
        Console.ReadKey();
    } 

    static double BlackScholes(double S0, double K, double T, double r, double sigma, string type = "call")
    {
        double d1 = (Math.Log(S0 / K) + (r + 0.5 * Math.Pow(sigma, 2)) * T) / (sigma * Math.Sqrt(T));
        double d2 = d1 - sigma * Math.Sqrt(T);

        double Nd1 = NormaleCdf(d1);
        double Nd2 = NormaleCdf(d2);
        double Nmoinsd1 = NormaleCdf(-d1);
        double Nmoinsd2 = NormaleCdf(-d2);

        if (type.ToLower() == "call")
            return S0 * Nd1 - K * Math.Exp(-r * T) * Nd2;
        else
            return K * Math.Exp(-r * T) * Nmoinsd2 - S0 * Nmoinsd1;
    }

    static double Erf(double x)
    {
        // Abramowitz & Stegun formula 7.1.26
        // erreur max < 1.5e-7
        double sign = Math.Sign(x);
        x = Math.Abs(x);

        double t = 1.0 / (1.0 + 0.3275911 * x);
        double y = 1.0 - (((((1.061405429 * t - 1.453152027) * t)
                            + 1.421413741) * t - 0.284496736) * t
                            + 0.254829592) * t * Math.Exp(-x * x);

        return sign * y;
    }

    static double NormaleCdf(double x)
    {
        return 0.5 * (1.0 + Erf(x / Math.Sqrt(2.0)));
    }
}

