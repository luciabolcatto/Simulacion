import random
import heapq
import numpy as np
import matplotlib.pyplot as plt

def simular_mm1(lam, mu, tiempo_max, capacidad_cola=None):
    t = 0.0
    en_sistema = 0
    aef = []
    heapq.heappush(aef, (random.expovariate(lam), 'ARR'))
    
    ultimo_evento_t = 0.0
    area_sistema = 0.0
    area_cola = 0.0
    tiempo_servidor_ocupado = 0.0
    
    clientes_arribados = 0
    clientes_atendidos = 0
    
    tiempos_arribo = {}
    tiempos_inicio_servicio = {}
    esperas_sistema = []
    esperas_cola = []

    while aef:
        t_evento, tipo = heapq.heappop(aef)
        if t_evento > tiempo_max:
            break
            
        delta_t = t_evento - ultimo_evento_t
        area_sistema += en_sistema * delta_t
        if en_sistema > 1:
            area_cola += (en_sistema - 1) * delta_t
            tiempo_servidor_ocupado += delta_t
        elif en_sistema == 1:
            tiempo_servidor_ocupado += delta_t
            
        t = t_evento
        ultimo_evento_t = t
        
        if tipo == 'ARR':
            clientes_arribados += 1
            capacidad_max_sistema = capacidad_cola + 1 if capacidad_cola is not None else float('inf')
            
            if en_sistema < capacidad_max_sistema:
                en_sistema += 1
                tiempos_arribo[clientes_arribados] = t
                if en_sistema == 1:
                    tiempos_inicio_servicio[clientes_arribados] = t
                    heapq.heappush(aef, (t + random.expovariate(mu), 'DEP'))
            
            heapq.heappush(aef, (t + random.expovariate(lam), 'ARR'))
            
        elif tipo == 'DEP':
            clientes_atendidos += 1
            id_cliente = clientes_atendidos
            if id_cliente in tiempos_arribo:
                t_arr = tiempos_arribo[id_cliente]
                t_ini = tiempos_inicio_servicio.get(id_cliente, t)
                esperas_cola.append(t_ini - t_arr)
                esperas_sistema.append(t - t_arr)
            
            en_sistema -= 1
            if en_sistema > 0:
                siguiente_cliente_id = clientes_atendidos + 1
                tiempos_inicio_servicio[siguiente_cliente_id] = t
                heapq.heappush(aef, (t + random.expovariate(mu), 'DEP'))

    L = area_sistema / t if t > 0 else 0
    Lq = area_cola / t if t > 0 else 0
    W = np.mean(esperas_sistema) if esperas_sistema else 0
    Wq = np.mean(esperas_cola) if esperas_cola else 0
    U = tiempo_servidor_ocupado / t if t > 0 else 0
    
    return L, Lq, W, Wq, U

if __name__ == "__main__":
    mu_fijo = 10.0      # Capacidad del servidor: 10 clientes por hora
    tiempo_sim = 2000.0 # Duración de cada simulación
    corridas = 10       # 10 corridas por experimento exige la UTN
    porcentajes = [0.25, 0.50, 0.75, 1.00, 1.25]
    
    # Listas para guardar las medias globales para graficar
    cargas_label = ['25%', '50%', '75%', '100%', '125%']
    medios_L = []
    medios_Lq = []
    medios_W = []
    medios_Wq = []
    medios_U = []
    
    print("=" * 70)
    print(" INICIANDO EXPERIMENTOS M/M/1 - PROCESANDO 10 CORRIDAS POR CASO")
    print("=" * 70)
    
    for pct in porcentajes:
        lam_exp = mu_fijo * pct
        list_L, list_Lq, list_W, list_Wq, list_U = [], [], [], [], []
        
        for _ in range(corridas):
            L, Lq, W, Wq, U = simular_mm1(lam_exp, mu_fijo, tiempo_sim)
            list_L.append(L)
            list_Lq.append(Lq)
            list_W.append(W)
            list_Wq.append(Wq)
            list_U.append(U)
            
        # Guardar promedios de este experimento
        medios_L.append(np.mean(list_L))
        medios_Lq.append(np.mean(list_Lq))
        medios_W.append(np.mean(list_W))
        medios_Wq.append(np.mean(list_Wq))
        medios_U.append(np.mean(list_U))
        
        print(f"Carga {int(pct*100)}% (λ={lam_exp}) -> L={np.mean(list_L):.2f}, Lq={np.mean(list_Lq):.2f}, W={np.mean(list_W):.2f}, U={np.mean(list_U):.2f}")
    
    print("\n[INFO] Guardando y abriendo las ventanas de gráficos...")
    
    # --- GRÁFICO 1: Clientes y Tiempos promedio ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.plot(cargas_label, medios_L, marker='o', color='blue', label='En Sistema (L)')
    ax1.plot(cargas_label, medios_Lq, marker='s', color='orange', label='En Cola (Lq)')
    ax1.set_title('Número Promedio de Clientes')
    ax1.set_xlabel('Tasa de Arribo / Carga respecto al Servidor')
    ax1.set_ylabel('Clientes')
    ax1.grid(True)
    ax1.legend()
    
    ax2.plot(cargas_label, medios_W, marker='o', color='green', label='En Sistema (W)')
    ax2.plot(cargas_label, medios_Wq, marker='s', color='red', label='En Cola (Wq)')
    ax2.set_title('Tiempo Promedio de Espera')
    ax2.set_xlabel('Tasa de Arribo / Carga respecto al Servidor')
    ax2.set_ylabel('Tiempo (Horas)')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('grafico_rendimiento.png', dpi=300) # <- Esto lo guarda solo en alta calidad
    plt.show() 
    
    # --- GRÁFICO 2: Utilización del Servidor ---
    plt.figure(figsize=(6, 4))
    plt.bar(cargas_label, medios_U, color='purple', alpha=0.7)
    plt.axhline(y=1.0, color='r', linestyle='--', label='Saturación Límite (100%)')
    plt.title('Utilización del Servidor (U) vs Carga')
    plt.xlabel('Experimento')
    plt.ylabel('Fracción de Tiempo Ocupado')
    plt.ylim(0, 1.2)
    plt.grid(axis='y')
    plt.legend()
    plt.tight_layout()
    plt.savefig('grafico_utilizacion.png', dpi=300) # <- Esto lo guarda solo en alta calidad
    plt.show()
    
    print("[OK] Imágenes guardadas como 'grafico_rendimiento.png' y 'grafico_utilizacion.png'.")