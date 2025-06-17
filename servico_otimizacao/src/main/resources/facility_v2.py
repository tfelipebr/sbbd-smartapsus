from matplotlib import pyplot as plt
from pulp import *
import math
import json
import time
import sys

def distancia_euclidiana(ponto1, ponto2):
    x1, y1 = ponto1
    x2, y2 = ponto2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) * 1000

try:
    # Obtendo o nome dos arquivos e dados do terminal 
    entrada = sys.argv[1]
    saida = sys.argv[2]
    k = int(sys.argv[3])  
    d_max = 100 #padrao
    lambdas = [0.9, 0.1]

    try:
        with open(entrada, encoding='utf-8') as entradas:
            dados = json.load(entradas)
    except Exception as e:
        raise ValueError(f"Erro ao abrir ou ler o arquivo JSON: {e}")

    try:
        # Conjunto de Localidades (coordenadas no plano)
        L = [(localidade["coordenada"].get('latitude', 0), localidade["coordenada"].get('longitude', 0)) 
             for localidade in dados["setores"] if not localidade["facility"]]

        # Conjunto de Facilities que podem ser ativadas (coordenadas no plano)
        F = [(localidade["coordenada"].get('latitude', 0), localidade["coordenada"].get('longitude', 0)) 
             for localidade in dados["setores"] if localidade["facility"]]

        # Métricas das Localidades
        M = [localidade["metricas"] for localidade in dados["setores"] if "metricas" in localidade and not localidade["facility"]]

        K_max= dados.get("num_facilities",None)
        
        # Nome métricas
        nome_metricas = dados.get("nome_metricas", None)

        if not L or not F or not M :
            raise ValueError("Dados insuficientes para a execucao do algoritmo.")

        l, f = len(L), len(F)
        m = len(M[0]) if M else 0  

        # Calcular Wi
        w = [sum(lambdas[j] * M[i][j] for j in range(len(lambdas))) for i in range(l)]

        # Distancia da Localidade i para a Facility j
        d = [[distancia_euclidiana(L[i], F[j]) for j in range(f)] for i in range(l)]
    except Exception as e:
        raise ValueError(f"Erro ao processar os dados: {e}")

    try:
        # Definição das Variáveis de decisão
        y = LpVariable.dicts('y', range(f), cat='Binary')
        x = LpVariable.dicts('x', (range(l), range(f)), cat='Binary')

        # Modelo de Minimização
        prob = LpProblem("minimizar", LpMinimize)

        # Função Objetivo
        prob += lpSum(x[i][j] * d[i][j] * w[i] for i in range(l) for j in range(f)), "Minimizar_Distancia_Ponderada"

        # Restrições do problema
        for i in range(l):
            prob += lpSum(x[i][j] for j in range(f)) == 1, f"Localidade_{i}_alocada"

        prob += lpSum(y[j] for j in range(f)) == k, "Numero_de_facilities_ativadas"

        for j in range(f):
            for i in range(l):
                prob += x[i][j] <= y[j], f"Facility_{j}_considerada_se_Localidade_{i}_alocada"

        for i in range(l):
            for j in range(f):
                prob += d[i][j] * x[i][j] <= d_max * y[j], f"Localidade_{i}_alocada_em_Facility_{j}_proxima"
                
    except Exception as e:
        raise ValueError(f"Erro ao definir as variáveis e restrições: {e}")

    try:
        # Tempo
        inicio = time.time()

        # Resolvendo 
        prob.solve(CPLEX(msg=1))

        # Finalizando tempo
        termino = time.time()
        tempo_execucao = termino - inicio

        # Status
        status = LpStatus[prob.status]

        resultados = {"status": status}

        if status == "Optimal":
            objective_value = value(prob.objective)
            centros_utilizados= [[i, j] for i in range(l) for j in range(f) if abs(x[i][j].varValue - 1) <= 0.1]

            resultados.update({
                "tempo_execucao": tempo_execucao,
                "min_dist_ponderada": objective_value,
                "num_localidades": l,
                "num_facilities": f,
                "num_centros": k,
                "dist_max": d_max,
                "metricas": nome_metricas,
                "prioridades": lambdas,
                "alocacoes": centros_utilizados,
                "centros_utilizados": [j for j in range(f) if abs(y[j].varValue - 1) <= 0.1]
            })

    except Exception as e:
        raise ValueError(f"Erro ao resolver o problema de otimização: {e}")

    
    with open(saida, 'w', encoding='utf-8') as saidas:
        json.dump(resultados, saidas, indent=4)

except Exception as e:
    resultados = {"status": "Erro", "mensagem": str(e)}
    with open(saida, 'w', encoding='utf-8') as saidas:
        json.dump(resultados, saidas, indent=4)