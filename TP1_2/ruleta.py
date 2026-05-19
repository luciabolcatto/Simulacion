import argparse
import random
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional

# -------------------------------------------------------------
# Ruleta y utilidades físicas
# -------------------------------------------------------------
class Roulette:
    REDS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    
    def spin(self) -> int:
        return random.randint(0, 36)

    def color(self, number: int) -> Optional[str]:
        if number == 0:
            return None
        return 'red' if number in Roulette.REDS else 'black'

    def is_odd(self, number: int) -> Optional[bool]:
        if number == 0:
            return None
        return (number % 2) == 1

    def column(self, number: int) -> Optional[int]:
        if number == 0:
            return None
        return ((number - 1) % 3) + 1

# -------------------------------------------------------------
# Apuesta (bet) y payout
# -------------------------------------------------------------
def evaluate_bet(bet_type: str, bet_choice, number: int) -> bool:
    r = Roulette()
    if bet_type == 'color':
        return r.color(number) == bet_choice
    if bet_type == 'number':
        return number == bet_choice
    if bet_type == 'column':
        return r.column(number) == bet_choice
    if bet_type == 'odd':
        odd = r.is_odd(number)
        if odd is None: 
            return False
        return odd == bet_choice
    raise ValueError("Unknown bet type")

def payout_multiplier(bet_type: str) -> float:
    if bet_type == 'number':
        return 36.0  
    if bet_type == 'column':
        return 3.0   
    if bet_type == 'color' or bet_type == 'odd':
        return 2.0   
    return 0.0

# -------------------------------------------------------------
# Estructura de Estrategias Económicas
# -------------------------------------------------------------
class Strategy:
    def __init__(self, base_bet: float = 1.0):
        self.base_bet = base_bet
    def bet_amount(self) -> float:
        raise NotImplementedError
    def record_result(self, win: bool):
        raise NotImplementedError
    def reset(self):
        raise NotImplementedError

class Martingale(Strategy):
    def __init__(self, base_bet=1.0):
        super().__init__(base_bet)
        self.current = base_bet
    def bet_amount(self):
        return self.current
    def record_result(self, win: bool):
        if win:
            self.current = self.base_bet
        else:
            self.current *= 2.0
    def reset(self):
        self.current = self.base_bet

class DAlembert(Strategy):
    def __init__(self, base_bet=1.0):
        super().__init__(base_bet)
        self.current = base_bet
    def bet_amount(self):
        return max(1.0, self.current)
    def record_result(self, win: bool):
        if win:
            self.current = max(self.base_bet, self.current - self.base_bet)
        else:
            self.current += self.base_bet
    def reset(self):
        self.current = self.base_bet

class Fibonacci(Strategy):
    def __init__(self, base_bet=1.0):
        super().__init__(base_bet)
        self.seq = [base_bet, base_bet]
        self.idx = 0
    def _ensure_idx(self):
        while self.idx >= len(self.seq):
            self.seq.append(self.seq[-1] + self.seq[-2])
    def bet_amount(self):
        self._ensure_idx()
        return self.seq[self.idx]
    def record_result(self, win: bool):
        if win:
            self.idx = max(0, self.idx - 2)
        else:
            self.idx += 1
    def reset(self):
        self.seq = [self.base_bet, self.base_bet]
        self.idx = 0

# CORRECCIÓN EXTRA: Mapeado oficial del sistema Paroli alineado al informe
class Paroli(Strategy):
    def __init__(self, base_bet=1.0):
        super().__init__(base_bet)
        self.current = base_bet
        self.wins_in_a_row = 0
    def bet_amount(self):
        return self.current
    def record_result(self, win: bool):
        if win:
            self.wins_in_a_row += 1
            if self.wins_in_a_row == 3:  # Fin de ciclo exitoso (3 aciertos)
                self.current = self.base_bet
                self.wins_in_a_row = 0
            else:
                self.current *= 2.0      # Duplica la apuesta usando ganancias
        else:
            self.current = self.base_bet # Resetea la progresión al perder
            self.wins_in_a_row = 0
    def reset(self):
        self.current = self.base_bet
        self.wins_in_a_row = 0

# -------------------------------------------------------------
# Simulación de una corrida experimental
# -------------------------------------------------------------
def simular_corrida(n: int, strategy: Strategy, bet_type: str, bet_choice, 
                    capital_mode: str, initial_capital: float) -> Tuple[List[float], List[float]]:
    r = Roulette()
    capitals: List[float] = []
    wins: List[float] = []
    
    # Límite máximo de apuesta de la mesa por seguridad
    limite_mesa = 500.0

    capital = float('inf') if capital_mode == 'i' else float(initial_capital)
    strategy.reset()

    # Punto inicial del Flujo de caja inicial (fci)
    capitals.append(initial_capital if capital_mode == 'f' else 0.0)

    for spin_idx in range(n):
        bet_amt = strategy.bet_amount()
        
        if bet_amt > limite_mesa:
            bet_amt = limite_mesa

        # Verificación de quiebra / fondos insuficientes
        if capital_mode == 'f' and bet_amt > capital:
            break

        spin = r.spin()
        is_win = evaluate_bet(bet_type, bet_choice, spin)
        wins.append(1.0 if is_win else 0.0)

        if is_win:
            net_profit = (payout_multiplier(bet_type) * bet_amt) - bet_amt
            if capital_mode == 'f':
                capital += net_profit
            else:
                capital += net_profit  # En infinito medimos balance neto acumulado
        else:
            if capital_mode == 'f':
                capital -= bet_amt
            else:
                capital -= bet_amt

        strategy.record_result(is_win)
        capitals.append(capital if capital_mode == 'f' else float(capital))

    # Padding para completar n iteraciones si hubo bancarrota prematura
    while len(capitals) <= n:
        capitals.append(capitals[-1])
    while len(wins) < n:
        wins.append(np.nan)

    return capitals, wins

def multiple_runs(c: int, n: int, strategy_name: str, bet_type: str, bet_choice, 
                  capital_mode: str, initial_capital: float):
    strategy_map = {
        'm': lambda: Martingale(1.0),
        'd': lambda: DAlembert(1.0),
        'f': lambda: Fibonacci(1.0),
        'o': lambda: Paroli(1.0)  # Mapeado oficial a Paroli
    }

    all_capitals = []
    all_wins = []
    for i in range(c):
        strat = strategy_map[strategy_name]()
        capitals, wins = simular_corrida(
            n=n, strategy=strat, bet_type=bet_type, bet_choice=bet_choice,
            capital_mode=capital_mode, initial_capital=initial_capital
        )
        all_capitals.append(capitals)
        all_wins.append(wins)

    return np.array(all_capitals, dtype=float), np.array(all_wins, dtype=float)

# -------------------------------------------------------------
# Módulo de Graficado Alineado al Boceto del TP
# -------------------------------------------------------------
def plot_results(all_capitals: np.ndarray, all_wins: np.ndarray, params):
    initial_capital = params['initial_capital']
    capital_mode = params['a']
    estrategia = params['s']
    c = params['c']
    n = params['n']
    
    mapa_est = {'m': 'Martingala', 'd': "D'Alembert", 'f': 'Fibonacci', 'o': 'Paroli'}
    mapa_cap = {'i': 'Infinito', 'f': 'Finito'}
    
    nombre_est = mapa_est[estrategia]
    nombre_cap = mapa_cap[capital_mode]
    
    eje_x_tiradas = range(1, n + 1)
    eje_x_fc = range(0, n + 1)
    colores = plt.cm.tab10.colors
    
    fig, (ax_frsa, ax_fc) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle(
        f"Estudio Económico: {nombre_est} (Capital {nombre_cap})\n"
        f"Simulación de {c} Corridas | {n} Tiradas máximas",
        fontsize=13, fontweight='bold'
    )
    
    # ── GRÁFICA 1: Frecuencia Relativa Favorable (frsa) ──
    # Calcula la evolución de aciertos acumulados paso a paso
    frsa_por_corrida = []
    for row in all_wins:
        valid_wins = row[~np.isnan(row)]
        if len(valid_wins) == 0:
            frsa_por_corrida.append(np.zeros(n))
            continue
        acum_wins = np.cumsum(valid_wins)
        tiradas_indices = np.arange(1, len(valid_wins) + 1)
        frsa_evolucion = acum_wins / tiradas_indices
        # Rellenar con el último valor si cortó antes por banca
        if len(frsa_evolucion) < n:
            frsa_evolucion = np.pad(frsa_evolucion, (0, n - len(frsa_evolucion)), 'edge')
        frsa_por_corrida.append(frsa_evolucion)
        
    frsa_promediada = np.mean(frsa_por_corrida, axis=0)
    ax_frsa.plot(eje_x_tiradas, frsa_promediada, color='red', linewidth=2, label='frsa simulada promedio')
    
    prob_teorica = 18.0 / 37.0
    ax_frsa.axhline(prob_teorica, color='black', linestyle='--', linewidth=1.5,
                    label=f'Prob. Teórica SS ({prob_teorica:.4f})')
    ax_frsa.set_title("Frecuencia Relativa de Apuesta Favorable (frsa)")
    ax_frsa.set_xlabel("n (número de tiradas)")
    ax_frsa.set_ylabel("fr")
    ax_frsa.legend(fontsize=9)
    ax_frsa.grid(True, alpha=0.3)
    
    # ── GRÁFICA 2: Flujo de Caja Multi-corrida Simultánea (fc) ──
    for i in range(c):
        ax_fc.plot(eje_x_fc, all_capitals[i], color=colores[i % 10], linewidth=0.9, alpha=0.75, label=f'Corrida {i+1}')
    
    fci_valor = initial_capital if capital_mode == 'f' else 0.0
    ax_fc.axhline(fci_valor, color='blue', linestyle='-', linewidth=2, label=f'fci (Flujo Inicial = {fci_valor:.0f})')
    
    if capital_mode == 'f':
        ax_fc.axhline(0.0, color='darkred', linestyle=':', linewidth=1.5, label='Línea de Bancarrota')
        
    ax_fc.set_title("Evolución del Flujo de Caja (cc)")
    ax_fc.set_xlabel("n (número de tiradas)")
    ax_fc.set_ylabel("cc (cantidad de capital)")
    ax_fc.legend(fontsize=8, ncol=2)
    ax_fc.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    nombre_archivo = f"grafica_{estrategia}_{capital_mode}_c{c}_n{n}.png"
    plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
    print(f"  → Gráfica exportada con éxito: {nombre_archivo}")
    plt.close()

# -------------------------------------------------------------
# Interfaz Principal (Lector de Consola Obligatorio Argparse)
# -------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description='TP1.2 — Estudio Económico-Matemático de Apuestas en la Ruleta (UTN-FRRO)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-c', '--corridas', type=int, required=True, help='Cantidad de corridas independientes')
    parser.add_argument('-n', '--tiradas', type=int, required=True, help='Cantidad de tiradas por corrida')
    parser.add_argument('-s', '--estrategia', type=str, required=True, choices=['m', 'd', 'f', 'o'],
                        help='Estrategia: m (Martingala), d (D\'Alembert), f (Fibonacci), o (Paroli)')
    parser.add_argument('-a', '--capital', type=str, required=True, choices=['i', 'f'],
                        help='Tipo de capital: i (Infinito), f (Finito)')
    parser.add_argument('-e', '--elegido', type=int, default=None, required=False, help='Número apostado (plenos)')
    
    args = parser.parse_args()
    
    # Configuración estándar para apuestas externas de suerte sencilla (Rojo)
    bet_type = 'color'
    bet_choice = 'red'
    initial_capital = 1000.0 # Caja fija estándar de inicio

    print(f"\n{'='*70}")
    print("  TP 1.2 — SIMULACIÓN ECONÓMICA DE LA RULETA (OBJETOS COHESIONADOS) — UTN FRRO")
    print(f"  Estrategia: {args.estrategia.upper()} | Capital: {args.capital.upper()} | Corridas: {args.corridas} | Tiradas: {args.tiradas}")
    print(f"{'='*70}\n")

    all_capitals, all_wins = multiple_runs(
        c=args.corridas,
        n=args.tiradas,
        strategy_name=args.estrategia,
        bet_type=bet_type,
        bet_choice=bet_choice,
        capital_mode=args.capital,
        initial_capital=initial_capital
    )

    plot_params = {
        'initial_capital': initial_capital,
        'a': args.capital,
        's': args.estrategia,
        'c': args.corridas,
        'n': args.tiradas
    }
    
    plot_results(all_capitals, all_wins, plot_params)
    print("\n¡Simulación completada! Imagen lista para subir a Overleaf.\n")

if __name__ == "__main__":
    main()