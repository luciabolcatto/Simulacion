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
# --- Reemplazar/actualizar estas funciones en tu código ---

def simular_corrida(n: int,
                 strategy: Strategy,
                 bet_type: str,
                 bet_choice,
                 capital_mode: str,
                 initial_capital: Optional[float] = None,
                 stop_on_bankruptcy: bool = True,
                 rng_seed: Optional[int] = None) -> Tuple[List[float], List[float], List[float], int]:
    """
    Returns:
      capitals: cantidad de capital después de cada iteración de ruleta
      wins: 1.0 si gana, 0.0 si pierde, np.nan si la corrida terminó antes de esa tirada
      bet_amounts: monto apostado en cada tirada (np.nan para tiradas inexistentes)
      bankruptcies: cantidad de bancarrotas en la corrida
    """
    if rng_seed is not None:
        random.seed(rng_seed)
    r = Roulette()
    capitals: List[float] = []
    wins: List[float] = []
    bet_amounts: List[float] = []
    bankruptcies = 0

    capital = float('inf') if capital_mode == 'i' else float(initial_capital)
    strategy.reset()

    for spin_idx in range(n):
        bet_amt = strategy.bet_amount()
        # record the intended bet amount (may be adjusted later if insufficient capital)
        bet_amounts.append(float(bet_amt) if bet_amt is not None else np.nan)

        # If bet 0 (Labouchere finished), stop — mark remaining wins as NaN
        if bet_amt <= 0:
            capitals.append(capital)
            wins.append(np.nan)
            break

        # if capital bounded and insufficient funds:
        if capital_mode == 'f' and bet_amt > capital:
            # bankrupt if cannot cover next bet
            bankruptcies += 1
            if stop_on_bankruptcy:
                # record state and break; mark this spin's win as NaN (no spin occurred)
                capitals.append(0.0)
                wins.append(np.nan)
                break
            else:
                # bet whatever remains
                bet_amt = capital

        spin = r.spin()
        is_win = evaluate_bet(bet_type, bet_choice, spin)
        wins.append(1.0 if is_win else 0.0)

        if is_win:
            ret = payout_multiplier(bet_type) * bet_amt
            # net profit = ret - bet_amt
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
                        # corrida terminó tras perder y quedar en 0; no hay resultado para siguiente tirada
                        break

        strategy.record_result(is_win)
        capitals.append(capital if capital_mode == 'f' else float('inf'))

    # pad bet_amounts and wins to length n if stopped early using np.nan
    if len(bet_amounts) < n:
        pad_val_bet = np.nan
        bet_amounts = bet_amounts + [pad_val_bet] * (n - len(bet_amounts))

    if len(wins) < n:
        wins = wins + [np.nan] * (n - len(wins))

    # pad capitals to length n using last known capital (keeps last state)
    if len(capitals) < n:
        pad_val_cap = capitals[-1] if capitals else (0.0 if capital_mode == 'f' else float('inf'))
        capitals = capitals + [pad_val_cap] * (n - len(capitals))

    return capitals, wins, bet_amounts, bankruptcies


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
    all_bets = []
    bankruptcies_total = 0
    for i in range(c):
        strat = strategy_map[strategy_name]()
        capitals, wins, bet_amounts, bankruptcies = simular_corrida(
            n=n,
            strategy=strat,
            bet_type=bet_type,
            bet_choice=bet_choice,
            capital_mode=capital_mode,
            initial_capital=initial_capital,
            stop_on_bankruptcy=True,
            rng_seed=(None if rng_seed is None else rng_seed + i)
        )

        # Ensure lengths are exactly n (simular_corrida already pads, but por seguridad)
        if len(capitals) < n:
            pad_val_cap = capitals[-1] if capitals else (0.0 if capital_mode == 'f' else float('inf'))
            capitals = capitals + [pad_val_cap] * (n - len(capitals))
        if len(wins) < n:
            wins = wins + [np.nan] * (n - len(wins))
        if len(bet_amounts) < n:
            bet_amounts = bet_amounts + [np.nan] * (n - len(bet_amounts))

        all_capitals.append(capitals)
        all_wins.append(wins)
        all_bets.append(bet_amounts)
        bankruptcies_total += bankruptcies

    # Convert to numpy arrays (float dtype to hold np.nan)
    return np.array(all_capitals, dtype=float), np.array(all_wins, dtype=float), np.array(all_bets, dtype=float), bankruptcies_total



def theoretical_params_for_bet(bet_type: str):
    #Devuelve (p_win, multiplier) según bet_type asumiendo ruleta europea (37 casillas: 0 + 1-36).
    #Multipliers: total returned including la apuesta original.
  
    if bet_type == 'color' or bet_type == 'odd':
        p_win = 18.0 / 37.0
        multiplier = 2.0   #recibes 2 veces la apuesta (apuesta + ganancia)
    elif bet_type == 'number':
        p_win = 1.0 / 37.0
        multiplier = 36.0  #recibes 36 veces la apuesta
    elif bet_type == 'column':
        p_win = 12.0 / 37.0
        multiplier = 3.0   #recibes 3 veces la apuesta
    else:
        # fallback: asumir even-money
        p_win = 18.0 / 37.0
        multiplier = 2.0
    return p_win, multiplier


def plot_results(all_capitals: np.ndarray, all_wins: np.ndarray, all_bets: np.ndarray, params):
    initial_capital = params['initial_capital']
    capital_mode = params['a']
    prefix = f"corridas{params['c']}_n{params['n']}_estrat_{params['s']}_bet_{params['bet_type']}_capital_{params['a']}"
    
    c, n = all_capitals.shape
    # 1) Capital vs tirada (mostrar promedio y algunas corridas)
    avg_capital = np.nanmean(np.where(np.isfinite(all_capitals), all_capitals, np.nan), axis=0)
    plt.figure(figsize=(10,5))
    for i in range(min(10, c)):
        plt.plot(range(1, n+1), all_capitals[i], color='gray', alpha=0.4)
    plt.plot(range(1, n+1), avg_capital, color='red', linewidth=2, label='Promedio')

    """# Calcular línea de capital esperado final (horizontal) usando parámetros teóricos y promedio de apuestas por tirada
    p_win, multiplier = theoretical_params_for_bet(params['bet_type'])
    expected_net_per_unit = p_win * multiplier - 1.0  # neto esperado por unidad apostada
    # promedio de apuesta por tirada (promedio entre corridas)
    avg_bet_per_spin = np.mean(all_bets, axis=0)  # shape (n,)
    # capital esperado por tirada (acumulado)
    expected_capital_traj = np.array(initial_capital) + np.cumsum(avg_bet_per_spin * expected_net_per_unit)
    expected_final_capital = expected_capital_traj[-1]
    # Dibujar línea horizontal en el valor esperado final
    plt.axhline(expected_final_capital, color='blue', linestyle='--', linewidth=2,
                label=f'Capital esperado final (teórico): {expected_final_capital:.2f}')
                """
    
    # Dibujar línea horizontal capital inicial
    capital_inicial = np.array(initial_capital)
    plt.axhline(initial_capital, color='red', linestyle='--', linewidth=2,
                label=f'Capital inicial: {initial_capital:.2f}')
    plt.xlabel('Número de tirada')
    plt.ylabel('Capital' + ('' if capital_mode == 'i' else f' (inicio {initial_capital})'))
    plt.title('Capital vs Número de tirada')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    fcapname = f"{prefix}_GRAF_CAPITAL.png"
    plt.savefig(fcapname, dpi=150, bbox_inches='tight')
    plt.close()

    # 2) Histograma de frecuencia relativa de obtener apuesta favorable por tirada (promedio por tirada)
    win_freq_per_spin = np.nanmean(all_wins, axis=0)  # entre 0 y 1
    plt.figure(figsize=(10,5))
    plt.bar(range(1, n+1), win_freq_per_spin, width=0.8)
    
    # Línea horizontal con probabilidad teórica de ganar
    p_win, _ = theoretical_params_for_bet(params['bet_type'])
    plt.axhline(p_win, color='blue', linestyle='--', linewidth=2,
                label=f'Probabilidad teórica de ganar: {p_win:.4f}')

    plt.xlabel('Número de tirada')
    plt.ylabel('Frecuencia relativa de apuesta favorable')
    plt.title('Frecuencia relativa de obtener apuesta favorable según tirada')
    plt.legend()
    plt.tight_layout()
    fhistname = f"{prefix}_GRAF_APUESTA.png"
    plt.savefig(fhistname, dpi=150, bbox_inches='tight')
    plt.close()

    # 3) Histograma de resultados finales
    final_capitals = all_capitals[:, -1]
    if capital_mode == 'f':
        plt.figure(figsize=(8,4))
        plt.hist(final_capitals, bins=20, density=True, alpha=0.7)
        plt.xlabel('Capital final')
        plt.ylabel('Densidad / Frecuencia relativa')
        plt.title('Histograma de capital final')
        plt.legend()
        plt.tight_layout()
        fhistcapname = f"{prefix}_GRAF_HISTOGRAMA_CAPITAL.png"
        plt.savefig(fhistcapname, dpi=150, bbox_inches='tight')
        plt.close()
    
    # 4) Curva de supervivencia simple (Kaplan Meier estilo)
    
    alive = (all_capitals > 0)  # True si capital > 0 en esa tirada
    survival = np.sum(alive, axis=0) / alive.shape[0]

    plt.figure(figsize=(10,5))
    plt.step(range(1, survival.size+1), survival, where='post', label='Supervivencia empírica')
    plt.xlabel('Número de tirada')
    plt.ylabel('Fracción de corridas activas')
    plt.title('Curva de supervivencia hasta bancarrota')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    fsurvname = f"{prefix}_GRAF_SUPERVIVENCIA.png"
    plt.savefig(fsurvname, dpi=150, bbox_inches='tight')
    #plt.show()
    plt.close()

    # 5)
    percentiles = [10, 25, 50, 75, 90]
    qs = np.nanpercentile(all_capitals, percentiles, axis=0)  # shape (len(percentiles), n)

    plt.figure(figsize=(10,6))
    x = np.arange(1, qs.shape[1]+1)
    plt.fill_between(x, qs[0], qs[-1], color='lightgreen', label='10-90 percentile')
    plt.fill_between(x, qs[1], qs[-2], color='pink', label='25-75 percentile')
    plt.plot(x, qs[2], color='red', linewidth=2, label='Mediana')
    plt.xlabel('Número de tirada')
    plt.ylabel('Capital')
    plt.title('Trayectorias percentiles de capital')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    fpercname = f"{prefix}_GRAF_PERCENTIL_CAPITAL.png"
    plt.savefig(fpercname, dpi=150, bbox_inches='tight')
    plt.close()

    # 6) histograma tiempo hasta bancarrota

    times_to_bankrupt = []
    for row in all_capitals:
        zeros = np.where(row == 0)[0]
        times_to_bankrupt.append(zeros[0]+1 if zeros.size>0 else np.nan)
    times_to_bankrupt = np.array(times_to_bankrupt)

    plt.figure(figsize=(8,4))
    plt.hist(times_to_bankrupt[~np.isnan(times_to_bankrupt)], bins=30, density=False, alpha=0.7)
    plt.xlabel('Tiradas hasta bancarrota')
    plt.ylabel('Frecuencia')
    plt.title('Distribución del tiempo hasta bancarrota')
    plt.tight_layout()
    fhisthastaquebrarname = f"{prefix}_GRAF_TIEMPO_HASTA_BANCARROTA.png"
    plt.savefig(fhisthastaquebrarname, dpi=150, bbox_inches='tight')
    plt.close()

    # 7) Boxplots en hitos (cada 50, 100, 250 o la ultima antes de quebrar)
    hitos = [50, 100, 250, all_capitals.shape[1]-1]
    data = [all_capitals[:, h-1][~np.isnan(all_capitals[:, h-1])] for h in hitos]
    plt.figure(figsize=(8,5))
    plt.boxplot(data, tick_labels=[str(h) for h in hitos], showfliers=True)
    plt.xlabel('Tirada')
    plt.ylabel('Capital')
    plt.title('Boxplot de capital en tiradas clave')
    plt.grid(True)
    plt.tight_layout()
    fboxplothitosname = f"{prefix}_GRAF_BOXPLOT_HITOS.png"
    plt.savefig(fboxplothitosname, dpi=150, bbox_inches='tight')
    plt.close()



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
        'initial_capital': 100.0,
        'base_bet': 1,
        'labouchere_seq': [1,2,3,4]
    }

    # map bet_choice if number chosen
    if params['bet_type'] == 'number':
        bet_choice = params['e']
    else:
        bet_choice = params['bet_choice']

        all_capitals, all_wins, all_bets, bankruptcies_total = multiple_runs(
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

    plot_results(all_capitals, all_wins, all_bets, params)

if __name__ == "__main__":
    main()
