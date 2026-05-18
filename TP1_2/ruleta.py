import random
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from typing import List, Tuple, Optional

# -----------------------------
# Ruleta y utilidades
# -----------------------------
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
        # columns: 1 -> 1,4,7,... 2 -> 2,5,8,... 3 -> 3,6,9,...
        return ((number - 1) % 3) + 1

# -----------------------------
# Apuesta (bet) y payout
# -----------------------------
def evaluate_bet(bet_type: str, bet_choice, number: int) -> bool:
    # bet_type: 'color', 'number', 'column', 'odd'
    r = Roulette()
    if bet_type == 'color':
        c = r.color(number)
        return c == bet_choice
    if bet_type == 'number':
        return number == bet_choice
    if bet_type == 'column':
        col = r.column(number)
        return col == bet_choice
    if bet_type == 'odd':
        odd = r.is_odd(number)
        if odd is None: return False
        return odd == bet_choice
    raise ValueError("Unknown bet type")

def payout_multiplier(bet_type: str) -> float:
    # returns multiplier of stake on win (not net profit)
    if bet_type == 'number':
        return 36.0  # betting 1 returns 36 (European roulette pays 35:1 so multiplier = 36 total returned)
    if bet_type == 'column':
        return 3.0   # pays 2:1 => 3 returned
    if bet_type == 'color' or bet_type == 'odd':
        return 2.0   # pays 1:1 => 2 returned
    return 0.0

# -----------------------------
# Estrategias
# -----------------------------
class Strategy:
    def __init__(self, base_bet: int = 1):
        self.base_bet = base_bet
    def bet_amount(self) -> int:
        raise NotImplementedError
    def record_result(self, win: bool):
        raise NotImplementedError
    def reset(self):
        raise NotImplementedError

class Martingale(Strategy):
    def __init__(self, base_bet=1):
        super().__init__(base_bet)
        self.current = base_bet
    def bet_amount(self):
        return self.current
    def record_result(self, win: bool):
        if win:
            self.current = self.base_bet
        else:
            self.current *= 2
    def reset(self):
        self.current = self.base_bet

class DAlembert(Strategy):
    def __init__(self, base_bet=1):
        super().__init__(base_bet)
        self.current = base_bet
    def bet_amount(self):
        return max(1, self.current)
    def record_result(self, win: bool):
        if win:
            self.current = max(self.base_bet, self.current - self.base_bet)
        else:
            self.current += self.base_bet
    def reset(self):
        self.current = self.base_bet

class Fibonacci(Strategy):
    def __init__(self, base_bet=1):
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
            # step back two in sequence
            self.idx = max(0, self.idx - 2)
        else:
            self.idx += 1
    def reset(self):
        self.seq = [self.base_bet, self.base_bet]
        self.idx = 0

class Labouchere(Strategy):
    def __init__(self, base_sequence: Optional[List[int]] = None):
        super().__init__(1)
        if base_sequence is None:
            base_sequence = [1,1,1,1]  # example line
        self.initial = list(base_sequence)
        self.seq = deque(self.initial)
    def bet_amount(self):
        if not self.seq:
            return 0
        if len(self.seq) == 1:
            return self.seq[0]
        return self.seq[0] + self.seq[-1]
    def record_result(self, win: bool):
        if not self.seq:
            return
        if win:
            # borrar el primero y el ultimo
            if len(self.seq) == 1:
                self.seq.pop()
            else:
                self.seq.popleft()
                self.seq.pop()
        else:
            lost = self.bet_amount()
            self.seq.append(lost)
    def reset(self):
        self.seq = deque(self.initial)

# -----------------------------
# Simulación de una corrida
# -----------------------------
def simular_corrida(n: int,
                 strategy: Strategy,
                 bet_type: str,
                 bet_choice,
                 capital_mode: str,
                 initial_capital: Optional[float] = None,
                 stop_on_bankruptcy: bool = True,
                 rng_seed: Optional[int] = None) -> Tuple[List[float], List[int], int]:
    """
    Returns:
      capitals: cant de capital dsps de cada iteracion de ruleta
      wins: muestra 0 o 1 si gana la apuesta o no
      bankruptcies: cant de bancarrotas en la corrida
    """
    if rng_seed is not None:
        random.seed(rng_seed)
    r = Roulette()
    capitals = []
    wins = []
    bankruptcies = 0

    capital = float('inf') if capital_mode == 'i' else float(initial_capital)
    strategy.reset()

    for spin_idx in range(n):
        bet_amt = strategy.bet_amount()
        # If bet 0 (Labouchere finished), stop
        if bet_amt <= 0:
            capitals.append(capital)
            wins.append(0)
            break

        # if capital bounded and insufficient funds:
        if capital_mode == 'f' and bet_amt > capital:
            # bankrupt if cannot cover next bet
            bankruptcies += 1
            if stop_on_bankruptcy:
                # record state and break
                capitals.append(0.0)
                wins.append(0)
                break
            else:
                # bet whatever remains
                bet_amt = capital

        spin = r.spin()
        is_win = evaluate_bet(bet_type, bet_choice, spin)
        wins.append(1 if is_win else 0)

        if is_win:
            ret = payout_multiplier(bet_type) * bet_amt
            # net profit = ret - bet_amt = (multiplier -1)*bet_amt
            net = ret - bet_amt
            if capital_mode == 'f':
                capital += net
        else:
            if capital_mode == 'f':
                capital -= bet_amt
                if capital <= 0:
                    capital = 0.0
                    bankruptcies += 1
                    if stop_on_bankruptcy:
                        capitals.append(capital)
                        break

        strategy.record_result(is_win)
        capitals.append(capital if capital_mode == 'f' else float('inf'))

    return capitals, wins, bankruptcies

# -----------------------------
# Ejecutar multiples corridas
# -----------------------------
def multiple_runs(c: int,
                  n: int,
                  strategy_name: str,
                  bet_type: str,
                  bet_choice,
                  capital_mode: str,
                  initial_capital: Optional[float] = None,
                  base_bet: int = 1,
                  labouchere_seq: Optional[List[int]] = None,
                  rng_seed: Optional[int] = None):
    strategy_map = {
        'm': lambda: Martingale(base_bet),
        'd': lambda: DAlembert(base_bet),
        'f': lambda: Fibonacci(base_bet),
        'o': lambda: Labouchere(labouchere_seq)
    }
    if strategy_name not in strategy_map:
        raise ValueError("Estrategia desconocida")

    all_capitals = []
    all_wins = []
    bankruptcies_total = 0
    for i in range(c):
        strat = strategy_map[strategy_name]()
        capitals, wins, bankruptcies = simular_corrida(
            n=n,
            strategy=strat,
            bet_type=bet_type,
            bet_choice=bet_choice,
            capital_mode=capital_mode,
            initial_capital=initial_capital,
            stop_on_bankruptcy=True,
            rng_seed=(None if rng_seed is None else rng_seed + i)
        )
        # Pad capitals to length n for easier aggregation
        if len(capitals) < n:
            pad_val = capitals[-1] if capitals else (0.0 if capital_mode == 'f' else float('inf'))
            capitals = capitals + [pad_val] * (n - len(capitals))
            wins = wins + [0] * (n - len(wins))
        all_capitals.append(capitals)
        all_wins.append(wins)
        bankruptcies_total += bankruptcies

    return np.array(all_capitals), np.array(all_wins), bankruptcies_total

# -----------------------------
# Graficar resultados
# -----------------------------
def plot_results(all_capitals: np.ndarray, all_wins: np.ndarray, params):
    initial_capital = params['initial_capital']
    capital_mode = params['a']
    prefix = f"corridas{params['c']}_n{params['n']}_estrat_{params['bet_type']}_capital_{params['a']}"
    
    c, n = all_capitals.shape
    # 1) Capital vs tirada (mostrar promedio y algunas corridas)
    avg_capital = np.nanmean(np.where(np.isfinite(all_capitals), all_capitals, np.nan), axis=0)
    plt.figure(figsize=(10,5))
    for i in range(min(10, c)):
        plt.plot(range(1, n+1), all_capitals[i], color='gray', alpha=0.4)
    plt.plot(range(1, n+1), avg_capital, color='red', linewidth=2, label='Promedio')
    plt.xlabel('Número de tirada')
    plt.ylabel('Capital' + ('' if capital_mode == 'i' else f' (inicio {initial_capital})'))
    plt.title('Capital vs Número de tirada')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    #plt.show()
    fcapname = f"{prefix}_GRAF_CAPITAL.png"
    plt.savefig(fcapname, dpi=150, bbox_inches='tight')

    # 2) Histograma de frecuencia relativa de obtener apuesta favorable por tirada (promedio por tirada)
    win_freq_per_spin = np.mean(all_wins, axis=0)  # entre 0 y 1
    plt.figure(figsize=(10,5))
    plt.bar(range(1, n+1), win_freq_per_spin, width=0.8)
    plt.xlabel('Número de tirada')
    plt.ylabel('Frecuencia relativa de apuesta favorable')
    plt.title('Frecuencia relativa de obtener apuesta favorable según tirada')
    plt.tight_layout()
    #plt.show()
    fhistname = f"{prefix}_GRAF_APUESTA.png"
    plt.savefig(fhistname, dpi=150, bbox_inches='tight')

    # 3) Opcional: histograma de resultados finales
    final_capitals = all_capitals[:, -1]
    if capital_mode == 'f':
        plt.figure(figsize=(8,4))
        plt.hist(final_capitals, bins=20, density=True, alpha=0.7)
        plt.xlabel('Capital final')
        plt.ylabel('Densidad / Frecuencia relativa')
        plt.title('Histograma de capital final')
        plt.tight_layout()
        plt.show()
        fhistcapname = f"{prefix}_GRAF_HISTOGRAMA_CAPITAL.png"
        plt.savefig(fhistcapname, dpi=150, bbox_inches='tight')

# -----------------------------
# Interfaz principal (main)
# -----------------------------
def main():
    # a: capital type i (infinito) or f (finito)
    # s: strategy m, d, f, o
    # n: spins per run
    # c: number of runs
    # e: chosen number for 'number' bet (if used)
    params = {
        'a': 'f',         # 'i' or 'f'
        's': 'm',         # 'm','d','f','o'
        'n': 500,
        'c': 200,
        'e': 7,
        'bet_type': 'color',  # 'color','number','column','odd'
        'bet_choice': 'red',  # depends on bet_type; for number use params['e']
        'initial_capital': 1000.0,
        'base_bet': 1,
        'labouchere_seq': [1,2,3,4]
    }

    # map bet_choice if number chosen
    if params['bet_type'] == 'number':
        bet_choice = params['e']
    else:
        bet_choice = params['bet_choice']

    all_capitals, all_wins, bankruptcies_total = multiple_runs(
        c=params['c'],
        n=params['n'],
        strategy_name=params['s'],
        bet_type=params['bet_type'],
        bet_choice=bet_choice,
        capital_mode=params['a'],
        initial_capital=params['initial_capital'],
        base_bet=params['base_bet'],
        labouchere_seq=params['labouchere_seq'],
        rng_seed=42
    )

    print(f"Corridas: {params['c']}, Tiradas por corrida: {params['n']}")
    print(f"Estrategia: {params['s']}, Tipo apuesta: {params['bet_type']}, Modo capital: {params['a']}")
    print(f"Bancarrotas totales: {bankruptcies_total}")

    plot_results(all_capitals, all_wins, params)

if __name__ == "__main__":
    main()
