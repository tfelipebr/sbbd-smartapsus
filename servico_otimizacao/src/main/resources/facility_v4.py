import logging
from matplotlib import pyplot as plt
from numpy import arccos, cos, sin, pi
import numpy as np
from pulp import LpVariable, LpProblem, LpMinimize, lpSum, value, LpStatus, CPLEX_CMD
import math
import json
import time
import sys
import cplex

def distancia_euclidiana(ponto1, ponto2):
    """
    Calcula a distância euclidiana entre dois pontos (x1, y1) e (x2, y2)
    """
    x1, y1 = ponto1
    x2, y2 = ponto2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) * 1000

def extrair_coord(cf):
    """
    Converte qualquer formato em (lat, lon, idx)
    aceita:
      • (lat, lon)
      • [(lat, lon)]
      • [idx, (lat, lon)]
      • {"centro": [lat, lon], ...}
      • {"centro": [[lat, lon]], ...}
    """
    if isinstance(cf, dict) and "centro" in cf:
        val = cf["centro"]
        if isinstance(val, (list, tuple)) and len(val) == 1 and isinstance(val[0], (list, tuple)):
            val = val[0]                    # desfaz colchete duplo
        lat, lon = val                      # agora são dois números
        idx = cf.get("codigo_cnes") or cf.get("idx")

    elif isinstance(cf, (list, tuple)):
        if len(cf) == 2 and all(isinstance(v, (int, float)) for v in cf):
            lat, lon = cf; idx = None
        elif len(cf) == 1:
            lat, lon = cf[0]; idx = None
        else:
            idx, (lat, lon) = cf

    else:
        raise ValueError(f"Formato inesperado: {cf}")

    return lat, lon, idx


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
    
    #logging.basicConfig(filename='teste.txt', level=logging.DEBUG, format='%(asctime)s - %(message)s')

   
    try:
        entrada = sys.argv[1]
        saida = sys.argv[2]
        d_max = 10
        c_max = 100000  
        

        try:
            
            with open(entrada, encoding='utf-8') as entradas:
                dados = json.load(entradas)
            print("Dados lidos com sucesso.")
        except Exception as e:
            raise ValueError(f"Erro ao abrir ou ler o arquivo JSON: {e}")

        try:
            
            
            k = dados.get("num_centros_desejado")  # Número de centros que deseja criar/alocar na cidade (já existentes incluso)

            codigo_cnes = [fac['codigo_cnes'] for fac in dados["facilities"] if fac.get("fixed") is True]

            flag_problema = dados.get("tipo_problema")  # Tipo de problema (1: minimizar distância ponderada, 2: minimizar custo)
            if flag_problema not in [1, 2]:
                raise ValueError("Flag invalida. Deve ser 1 ou 2.")
            
          # Leitura dos dados
            L = [(loc["coordenada"][0], loc["coordenada"][1]) for loc in dados["localidades"] if "fixed" not in loc]  
            Ff = [(fac["coordenada"][0], fac["coordenada"][1]) for fac in dados["facilities"] if fac.get("fixed") is True]  
            Fn = [(loc["coordenada"][0], loc["coordenada"][1]) for loc in dados["facilities"] if loc.get("fixed") is False]  


            print(f"ff: {len(Ff)}")
            print(f"fn: {len(Fn)}")

            # Combinação de facilities fixas
            F = Ff  + Fn
            # Extração de métricas
            M = [loc["metricas"] for loc in dados["localidades"]]  # Métricas para localidades 

            nome_metricas = dados.get("nome_metricas", None)
            
            # Extração de pesos
            lambdas = dados.get("pesos", None)
            if lambdas is None:
                raise ValueError("Pesos não fornecidos.")
            if len(lambdas) != len(M[0]):
                raise ValueError("Número de pesos não corresponde ao número de métricas.")
            
            flag_proporcao_inversa = dados.get("proporcao_inversa", None)

            if flag_proporcao_inversa is None:
                raise ValueError("Flag de proporção inversa não fornecida.")

            
            if len(flag_proporcao_inversa) != len(M[0]):
                raise ValueError("O tamanho de flag_proporcao_inversa deve ser igual ao número de métricas.")

            if any(f not in [0, 1] for f in flag_proporcao_inversa):
                raise ValueError("Flag de proporção inversa deve conter apenas 0 ou 1.")

            # Aplica a inversão para cada localidade e para cada métrica conforme a flag
            for i in range(len(M)):
                for j in range(len(M[i])):
                    if flag_proporcao_inversa[j] == 1 and M[i][j] != 0:
                        M[i][j] = 1 / M[i][j]



            #Verificação K
            if k < len(Ff):
                raise ValueError("Número de centros desejados não pode ser menor que o número de centros que já existem.")

            if k > len(F):
                raise ValueError("Número de centros disponíveis é menor que o número de centros desejados.")


            # Custos e capacidades para localidades com fixed = false
            c = [loc["custo"] for loc in dados["facilities"]]  

            cap = [12000 for loc in dados["facilities"]]  

            # Total de moradores nas localidades sem o campo "fixed"
            p = [loc["total_moradores"] for loc in dados["localidades"]]

            # Cálculos e distâncias
            l, f = len(L), len(F)


            # Calcule w usando a lista atualizada de métricas M
            w = [sum(lambdas[j] * M[i][j] for j in range(len(lambdas))) for i in range(len(M))]


            # Calcule d se houver localidades e facilities
            d = [[getDistanceBetweenPointsNew(L[i], F[j]) for j in range(f)] for i in range(l)] if l > 0 and f > 0 else []
            d_max = max([min(d[i]) for i in range(l)]) 
            # Log para distâncias e w
            #logging.debug(f"Distancias: {d}")
            #logging.debug(f"Pesos: {w}")
            print(f"Tamanho de L (localidades): {len(L)}")
            print(f"Tamanho de F (facilities): {len(F)}")
            print(f"Tamanho de Fn (facilities novas): {len(Fn)}")
            print(f"Tamanho de Ff (facilities fixas): {len(Ff)}")
            print(f"Tamanho de M (métricas): {len(M)}")
            if len(M) > 0:
                print(f"Tamanho das métricas (elementos em M[0]): {len(M[0])}")




            
            # # Variáveis de depuração
            # logging.debug(f"L (localidades): {L}")
            # logging.debug(f"K: {k}")
            # logging.debug(f"flag: {flag_problema}")
            # logging.debug(f"entrada: {entrada}")

            logging.debug(f"Fn (facilities novas): {Fn}")
            logging.debug(f"Ff (facilities fixas): {Ff}")
            # logging.debug(f"Fn tamanho : {len(Fn)}")
            # logging.debug(f"Ff tamanho : {len(Ff)}")
            # logging.debug(f"F (todas as facilities): {F}")
            # logging.debug(f"nome_metricas: {nome_metricas}")
            # logging.debug(f"c (custos): {c}")
            # logging.debug(f"cap (capacidades): {cap}")
            # logging.debug(f"p (total moradores): {p}")
            # logging.debug(f"l (número de localidades): {l}")
            # logging.debug(f"f (número de facilities): {f}")
            # logging.debug(f"w (pesos): {w}")
            logging.debug(f"Valor de k: {k}, len(Ff): {len(Ff)}, l (localidades): {l}, f (facilities): {f}")


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

            # Definição das restriçõe
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

            for j in range(len(Fn)):
                        prob += lpSum(p[i] * x[i][j] for i in range(l)) <= cap[j], f"Capacidade_Facility_{j}"
            
            
            
            if flag_problema == 2:    
                        
                    prob +=lpSum(y[j] * c[j] for j in range(len(Fn))) <= c_max , f"Facility_Custo_Maximo_{j}"
                    #logging.debug(f"Facility_Custo_Maximo_{j} com custo {c[j]}")
                    

        
        
        except Exception as e:
            raise ValueError(f"Erro ao definir as variáveis e restrições: {e}")

        try:
           
            inicio = time.time()

            solver = CPLEX_CMD(msg=1)
            solver.timeLimit = 1000
            prob.solve(solver)
            
            #for j in range(len(Fn)):
                #logging.debug(f"facility{j}: {y[j].varValue}")
                
            for i in range(l):
                for j in range(f):
                    logging.debug(f"alocacao({i},{j}): {x[i][j].varValue}")
                    #logging.debug(f"dist({i},{j}): {d[i][j]}")
                    
       

            termino = time.time()
            tempo_execucao = termino - inicio
            status = LpStatus[prob.status]

            resultados = {"status": status}
            if status == "Optimal":
                objective_value = value(prob.objective)
                

                centros_utilizados = []
                centros_fixos = []


                for j in range(len(Ff)):
                        centros_fixos.append([Ff[j]])
                
                offset = len(Ff)
                for j in range(len(Fn)):
                    if abs(y[j].varValue - 1) <= 0.1:
                        centros_utilizados.append([j + offset, Fn[j]])


                # Verificação para evitar duplicação de índices
                print("Centros não fixos:", centros_utilizados)
                print("Centros fixos com índices ajustados:", centros_fixos)
                alocacoes_utilizadas = []
                for i in range(l):
                    for j in range(f):
                        if abs(x[i][j].varValue - 1) <= 0.1:
                            if j < len(Ff): 
                                alocacoes_utilizadas.append({
                                    "localidade": dados["localidades"][i]["codigo"],
                                    "centro": codigo_cnes[j]
                                })
                            else:  
                                alocacoes_utilizadas.append({
                                    "localidade": dados["localidades"][i]["codigo"],
                                    "centro": dados["facilities"][j - len(Ff)]["coordenada"]
                                })
              
                          


                problema = "min_dist" if flag_problema == 1 else "min_custo"
                resultados.update({
                    "tipo_problema": problema,
                    "tempo_execucao": tempo_execucao,
                    problema: objective_value,
                    "num_centros": k,
                    "orcamento": c_max,
                    "metricas": nome_metricas,
                    "prioridades": lambdas,
                    "alocacoes": alocacoes_utilizadas,
                    "centros_adicionados": centros_utilizados,
                    "centros_fixos": [{"centro": coord, "codigo_cnes": codigo_cnes} for coord, codigo_cnes in zip(centros_fixos, codigo_cnes)],
                })
            
        except Exception as e:
            raise ValueError(f"Erro ao resolver o problema de otimizacao: {e}")
        
        with open(saida, 'w', encoding='utf-8') as saidas:
                json.dump(resultados, saidas, indent=4)

    except Exception as e:
        resultados = {"status": "Erro", "mensagem": str(e)}
        with open(saida, 'w', encoding='utf-8') as saidas:
            json.dump(resultados, saidas, indent=4)

    
    
    if resultados.get("status") == "Optimal":
        alocacoes_utilizadas = resultados["alocacoes"]
        centros_utilizados = resultados["centros_adicionados"]
        centros_fixos = resultados["centros_fixos"]

        plt.figure(figsize=(12, 10))

        # Plotagem das localidades
        for idx, (lat, lon) in enumerate(L):
            plt.scatter(lon, lat, color='blue', s=50, edgecolors='black', label='Localidades' if idx == 0 else "")
            plt.text(lon, lat, f'L{idx}', fontsize=12, ha='right')

        # Plotagem de facilities novas
        if centros_utilizados:
            for cf in centros_utilizados:
                lat, lon, idx = extrair_coord(cf)
                plt.scatter(lon, lat, color='green', marker='^', s=100, edgecolors='black',
                            label='Facilities Novas' if cf == centros_utilizados[0] else "")
                if idx is not None:
                    plt.text(lon, lat, f'F{idx}', fontsize=12, ha='right')

        # Plotagem de facilities fixas
        if centros_fixos:
            for cf in centros_fixos:
                lat, lon, idx = extrair_coord(cf)
                plt.scatter(lon, lat, color='red', marker='s', s=100, edgecolors='black',
                            label='Facilities Fixas' if cf == centros_fixos[0] else "")
                if idx is not None:
                    plt.text(lon, lat, f'F{idx}', fontsize=12, ha='right')

        # Remover duplicatas das legendas
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        # Conectar alocações com linhas
        for localidade_idx, facility_idx in alocacoes_utilizadas:
            # ───── normaliza índices de localidade ─────
            try:
                localidade_idx = int(localidade_idx)
            except ValueError:
                continue            # pula se não for um inteiro (IBGE em string)

            # idem para facility; pode não estar na lista F
            try:
                facility_idx = int(facility_idx)
            except ValueError:
                continue            # pula se for CNES/coord fora de F

            localidade_coord = L[localidade_idx]
            facility_coord   = F[facility_idx]
            plt.plot([localidade_coord[1], facility_coord[1]],
                    [localidade_coord[0], facility_coord[0]],
                    linestyle='-', color='gray', alpha=0.5)

        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Alocações de Facilities')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{saida}.png')
        plt.show()
    else:
        print("Nenhuma alocação encontrada ou status não é Ótimo. Nenhum gráfico será gerado.")



    if resultados.get("status") == "Optimal":
        centros_utilizados = resultados["centros_adicionados"]
        centros_fixos = resultados["centros_fixos"]

        plt.figure(figsize=(12, 10))

        # Plotagem de facilities novas
        if centros_utilizados:
            for cf in centros_utilizados:
                lat, lon, idx = extrair_coord(cf)
                plt.scatter(lon, lat, color='green', marker='^', s=100, edgecolors='black',
                            label='Facilities Novas' if cf == centros_utilizados[0] else "")
                if idx is not None:
                    plt.text(lon, lat, f'F{idx}', fontsize=12, ha='right')

        # Plotagem de facilities fixas
        if centros_fixos:
            for cf in centros_fixos:
                lat, lon, idx = extrair_coord(cf)
                plt.scatter(lon, lat, color='red', marker='s', s=100, edgecolors='black',
                            label='Facilities Fixas' if cf == centros_fixos[0] else "")
                if idx is not None:
                    plt.text(lon, lat, f'F{idx}', fontsize=12, ha='right')

        # Remover duplicatas das legendas
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Posição das Facilities')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{saida}_facilities.png')
    else:
        print("Nenhuma alocação encontrada ou status não é Ótimo. Nenhum gráfico será gerado.")



if __name__ == "__main__":
    main()