import logging
from matplotlib import pyplot as plt
from numpy import arccos, cos, sin, pi
from pulp import LpVariable, LpProblem, LpMinimize, lpSum, value, LpStatus, CPLEX_CMD
import math
import json
import time
import sys

def distancia_euclidiana(ponto1, ponto2):
    """
    Calcula a distância euclidiana entre dois pontos (x1, y1) e (x2, y2)
    """
    x1, y1 = ponto1
    x2, y2 = ponto2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) * 1000

def rad2deg(radians):
    """
    Converte radianos para graus.
    """
    return radians * 180 / pi

def deg2rad(degrees):
    """
    Converte graus para radianos.
    """
    return degrees * pi / 180

def clamp(value, min_value, max_value):
    """
    Restringe um valor para que ele esteja dentro do intervalo definido por min_value e max_value.
    """
    return max(min_value, min(value, max_value))

def getDistanceBetweenPointsNew(ponto1, ponto2):
    """
    Calcula a distância entre dois pontos geográficos (latitude, longitude) usando a fórmula de Haversine.
    """
    latitude1, longitude1 = ponto1
    latitude2, longitude2 = ponto2
    theta = longitude1 - longitude2

    try:
        cosine_similarity = (sin(deg2rad(latitude1)) * sin(deg2rad(latitude2))) + \
                            (cos(deg2rad(latitude1)) * cos(deg2rad(latitude2)) * cos(deg2rad(theta)))
        cosine_similarity = clamp(cosine_similarity, -1, 1)
        distance = 60 * 1.1515 * rad2deg(math.acos(cosine_similarity))
        return round(distance * 1.609344, 2)  
    except Exception as e:
        raise ValueError(f"Erro ao calcular a distância entre {ponto1} e {ponto2}: {e}")

def main():
    
    #logging.basicConfig(filename='teste2.txt', level=logging.DEBUG, format='%(asctime)s - %(message)s')

   
    try:
        entrada = sys.argv[1]
        saida = sys.argv[2] # Nome do arquivo de saída
        d_max = 10
        c_max = 100
        lambdas = [0.9, 0.1]  

        try:
            
            with open(entrada, encoding='utf-8') as entradas:
                dados = json.load(entradas)
            print("Dados lidos com sucesso.")
        except Exception as e:
            raise ValueError(f"Erro ao abrir ou ler o arquivo JSON: {e}")

        try:
           #Leitura
            
            #saida = dados.get("arquivo_saida", "saida.json")  # Nome do arquivo de saída
            k = dados.get("num_centros_desejado")  # Número de centros a serem utilizados
            flag_problema = dados.get("tipo_problema")  # Tipo de problema (1: minimizar distância ponderada, 2: minimizar custo)

            if flag_problema not in [1, 2]:
                raise ValueError("Flag invalida. Deve ser 1 ou 2.")
           #Leitura dos daods
            L = [(loc["coordenada"][0], loc["coordenada"][1]) for loc in dados["localidades"]]
            Fn = [(fac["coordenada"][0], fac["coordenada"][1]) for fac in dados["facilities"] if not fac.get("fixed")]
            Ff = [(fac["coordenada"][0], fac["coordenada"][1]) for fac in dados["facilities"] if fac.get("fixed")]
            F = Fn + Ff
            M = [loc["metricas"] for loc in dados["localidades"]]
            nome_metricas = dados.get("nome_metricas", None)
            c = [fac["custo"] for fac in dados["facilities"] if not fac.get("fixed")]
            cap = [12000 for _ in dados["facilities"]]
            p = [loc["total_moradores"] for loc in dados["localidades"]]
            l, f = len(L), len(F)
            m = len(M[0]) if M else 0
            w = [sum(lambdas[j] * M[i][j] for j in range(len(lambdas))) for i in range(l)]
            d = [[getDistanceBetweenPointsNew(L[i], F[j]) for j in range(f)] for i in range(l)]
            #logging.debug(f"Distancias {d}")
            
            if not L or not Fn or not Ff or not M or not c or not cap or not p:
                raise ValueError("Dados insuficientes para a execução do algoritmo.")
            # # Variáveis de depuração
            #logging.debug(f"L (localidades): {L}")
            # logging.debug(f"K: {k}")
            # logging.debug(f"flag: {flag_problema}")
            # logging.debug(f"entrada: {entrada}")

            # logging.debug(f"Fn (facilities novas): {Fn}")
            # logging.debug(f"Ff (facilities fixas): {Ff}")
            # logging.debug(f"Fn tamanho : {len(Fn)}")
            # logging.debug(f"Ff tamanho : {len(Ff)}")
            # logging.debug(f"F (todas as facilities): {F}")
            # # logging.debug(f"nome_metricas: {nome_metricas}")
            # logging.debug(f"c (custos): {c}")
            # logging.debug(f"cap (capacidades): {cap}")
            # logging.debug(f"p (total moradores): {p}")
            # logging.debug(f"l (número de localidades): {l}")
            # logging.debug(f"f (número de facilities): {f}")
            # logging.debug(f"w (pesos): {w}")
            # logging.debug(f"d (distâncias): {d}")

        except Exception as e:
            raise ValueError(f"Erro ao processar os dados: {e}")

        try:
            # Definição das variáveis
            y = LpVariable.dicts('y', range(len(Fn)), cat='Binary')
            x = LpVariable.dicts('x', (range(l), range(f)), cat='Binary')

            prob = LpProblem("minimizar", LpMinimize)

            # Definição da função objetivo
            if flag_problema == 1:
                prob += lpSum(x[i][j] * d[i][j] * w[i] for i in range(l) for j in range(f)), "Minimizar_Distancia_Ponderada"
            else:
                prob += lpSum(y[j] * c[j] for j in range(len(Fn))), "Minimizar_Custo"

            # Definição das restrições
            for i in range(l):
                prob += lpSum(x[i][j] for j in range(f)) == 1, f"Localidade_{i}_alocada"
                

            prob += lpSum(y[j] for j in range(len(Fn))) == k - len(Ff), "Numero_de_facilities_novas_ativadas"
            

            if flag_problema == 1:  
                for j in range(len(Fn)):
                    for i in range(l):
                        prob += x[i][j] <= y[j], f"Facility_{j}_considerada_se_Localidade_{i}_alocada"
                        #logging.debug(f" Facility_{j}_considerada_se_Localidade_{i}_alocada")

            for i in range(l):
                for j in range(f):
                    prob += d[i][j] * x[i][j] <= d_max, f"Localidade_{i}_alocada_em_Facility_{j}_proxima"
                    #logging.debug(f"Localidade_{i}_alocada_em_Facility_{j}_proxima com distância {d[i][j]} e d_max {d_max}")

            prob +=lpSum(y[j] * c[j] for j in range(len(Fn))) <= c_max , f"Facility_Custo_Maximo_{j}"
            #logging.debug(f"Facility_Custo_Maximo_{j} com custo {c[j]}")
            
            
            if flag_problema == 2:    
                    for j in range(f):
                        prob += lpSum(p[i] * x[i][j] for i in range(l)) <= cap[j], f"Capacidade_Facility_{j}"
                    

        
        
        except Exception as e:
            raise ValueError(f"Erro ao definir as variáveis e restrições: {e}")

        try:
           
            inicio = time.time()

            solver = CPLEX_CMD(msg=1)
            solver.timeLimit = 180
            prob.solve(solver)
            
            for j in range(len(Fn)):
                logging.debug(f"facility{j}: {y[j].varValue}")
                
            for i in range(l):
                for j in range(f):
                    logging.debug(f"alocacao({i},{j}): {x[i][j].varValue}")
                    # logging.debug(f"dist({i},{j}): {d[i][j]}")
                    
        
                    

            termino = time.time()
            tempo_execucao = termino - inicio
            status = LpStatus[prob.status]

            resultados = {"status": status}
            if status == "Optimal":
                objective_value = value(prob.objective)
                centros_utilizados = []
                for j in range(len(Fn)):
                    if abs(y[j].varValue - 1) <= 0.1:
                        centros_utilizados.append([j, Fn[j]])
                centros_fixos = []
                for j in range(len(Ff)):
                    centros_fixos.append([j,Ff[j]])

                problema = "min_dist" if flag_problema == 1 else "min_custo"
                resultados.update({
                    "tipo_problema": problema,
                    "tempo_execucao": tempo_execucao,
                    problema: objective_value,
                    "num_centros": k,
                    "orcamento": c_max,
                    "metricas": nome_metricas,
                    "prioridades": lambdas,
                    "alocacoes": [[i, j] for i in range(l) for j in range(f) if abs(x[i][j].varValue - 1) <= 0.1],
                    "centros_adicionados": centros_utilizados,
                    "centros_fixos": centros_fixos
                })
            
        except Exception as e:
            raise ValueError(f"Erro ao resolver o problema de otimizacao: {e}")
        
        with open(saida, 'w', encoding='utf-8') as saidas:
                json.dump(resultados, saidas, indent=4)

    except Exception as e:
        resultados = {"status": "Erro", "mensagem": str(e)}
        with open(saida, 'w', encoding='utf-8') as saidas:
            json.dump(resultados, saidas, indent=4)

    
    
# PLOT
    if resultados.get("status") == "Optimal":
        alocacoes_utilizadas = resultados["alocacoes"]
        centros_utilizados = resultados["centros_adicionados"]
        centros_fixos = resultados["centros_fixos"]

        coordenadas_localidades = L
        coordenadas_facilities = F

        plt.figure(figsize=(12, 10))

        # Plotando localidades
        for idx, coord in enumerate(coordenadas_localidades):
            plt.scatter(coord[1], coord[0], color='blue', label='Localidades' if idx == 0 else "", s=50, edgecolors='black')
            plt.text(coord[1], coord[0], f'L{idx}', fontsize=12, ha='right')

        # Plotando facilities novas
        if centros_utilizados:
            for idx, coord in centros_utilizados:
                plt.scatter(coord[1], coord[0], color='green', marker='^', s=100, label='Facilities Novas' if idx == centros_utilizados[0][0] else "", edgecolors='black')
                plt.text(coord[1], coord[0], f'F{idx}', fontsize=12, ha='right')

        # Plotando facilities fixas
        if centros_fixos:
            for idx, coord in centros_fixos:
                plt.scatter(coord[1], coord[0], color='red', marker='s', s=100, label='Facilities Fixas' if idx == centros_fixos[0][0] else "", edgecolors='black')
                plt.text(coord[1], coord[0], f'F{idx}', fontsize=12, ha='right')

        # Remover duplicatas das legendas
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        # Conectando as alocações com linhas
        for alo in alocacoes_utilizadas:
            localidade_idx, facility_idx = alo
            localidade_coord = coordenadas_localidades[localidade_idx]
            facility_coord = coordenadas_facilities[facility_idx]
            plt.plot([localidade_coord[1], facility_coord[1]], [localidade_coord[0], facility_coord[0]], linestyle='-', color='gray', alpha=0.5)

        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Alocações de Facilities')
        plt.grid(True)
        plt.tight_layout()

        plt.savefig(f'{saida}.png')
        plt.show()
    else:
        print("Nenhuma alocação encontrada ou status não é Ótimo. Nenhum gráfico será gerado.")
        sys.exit(1)


if __name__ == "__main__":
    main()
