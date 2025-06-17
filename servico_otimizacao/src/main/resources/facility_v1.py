from matplotlib import pyplot as plt
from pulp import *
import math
import json
import sys

# Obtendo o nome dos arquivos de entrada e saída do terminal
entrada = sys.argv[1]
saida = sys.argv[2]

with open(entrada, encoding='utf-8') as entradas:
    dados = json.load(entradas)

# Função para calcular a distância euclidiana 
def distancia_euclidiana(ponto1, ponto2):
    x1, y1 = ponto1
    x2, y2 = ponto2
    distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distancia 

# Dados de Entrada
# Lendo as variáveis do JSON
# Escrever as variaveis de forma mais literal 

# Número de Localidades
n = dados["n"] 

# Conjunto de Localidades (coordenadas no plano)
L = dados["L"] 

# Conjunto de Facilities que podem ser ativadas (coordenadas no plano)
F = dados["F"]

# Distancia Máxima
D_MAX = dados["D_MAX"]

#K facilities 
k = dados["k"]

# Métricas das Localidades 
M = dados["M"]

# Lambdas das m metricas
lambdas = dados["lambdas"]

# Tamanho dos conjuntos Localidade e Facilities
f = len(F)
l = len(L)

# Quantidade de métricas
m = len(M[0])

# Distancia da Localidade i para a Facility j
d = []

for localidade in L:
    row = []
    for facility in F:
        distancia = distancia_euclidiana(localidade, facility)
        #print(f"distancia {localidade} e {facility} = {distancia}")
        row.append(distancia)
    d.append(row)

# Calcular Wi
w = []

for i in range(n):
    peso_total = 0
    for j in range(len(lambdas)):
        peso_total += lambdas[j] * M[i][j]
    w.append(peso_total)

# Definição das Variáveis de decisão
# Indicar se uma facility j está ativada
y = LpVariable.dicts(f'y_{j}', range(f) ,cat='Binary')

# Indicar se uma localidade i está alocada a uma facility j
x = LpVariable.dicts(f'x_{i}_{j}', (range(l),range(f)),cat='Binary')

# Modelo de Minimização
prob = LpProblem("minimizar", LpMinimize)


# Função Objetivo
objective = lpSum(x[i][j] * d[i][j] * w[i] for i in range(l) for j in range(f))
prob += objective, "Minimizar_Distancia_Ponderada"

# Restrições do problema
# Restrição: Toda localidade deve ser alocada em uma Facility
for i in range(l):
    prob += lpSum(x[i][j] for j in range(f)) == 1, f"Localidade_{i}_alocada"
    
# Restrição: Devemos ter k Facilities 
prob += lpSum(y[j] for j in range(f)) == k, "Numero_de_facilities_ativadas"

# Restrição: Uma Facility só é considerada se uma localidade estiver alocada nela
for j in range(f):
    for i in range(l):
        prob += x[i][j] <= y[j], f"Facility_{j}_considerada_se_Localidade_{i}_alocada"

# Restrição: A localidade só deve ser alocada em uma Facility próxima (menor que Dmax)
for i in range(l):
    for j in range(f):
        prob += d[i][j] * x[i][j] <= D_MAX * y[j], f"Localidade_{i}_alocada_em_Facility_{j}_proxima"

#To cplex
path_to_cplex = "/opt/ibm/ILOG/CPLEX_Studio2211/cplex/bin/x86-64_linux/cplex"
#solver = CPLEX_CMD(msg=1)
solver = CPLEX_CMD(path=path_to_cplex, msg=1)

# Define o tempo limite para o solver
solver.timeLimit = 7200

# Solução 
prob.solve(solver)
#escrever no json de saida

# Status
print("Status:", LpStatus[prob.status])
#escrever no json de saida

# Valor função Objetivo
print("Minimo distancia ponderada = ", value(prob.objective))

#Lista de valores X e Y para printar alocações e facilities alocadas
lista_localidades = []
lista_facilities = []

for i in range(l):
    for j in range(f):
        if abs(x[i][j].varValue - 1) < 0.1:
            #print(f"Localidade {i} alocada na Facility {j}\n")
            lista_localidades.append(f"Localidade {i} alocada na Facility {j}")

for j in range(j):
    if abs(y[j].varValue - 1) < 0.1:
           # print (f"Facility {j} ativada")
            lista_facilities.append(f"Facility {j} ativada")
            
for i in range(len(lista_facilities)):
    print(lista_facilities[i])

# Escrevendo a saída no JSON
# Escrever todas as informações
resultados = {
  "Status": LpStatus[prob.status],
  "Minimo distancia ponderada": value(prob.objective),
  "Distancia_max" : D_MAX,
  "Prioridade metricas(lambda)": lambdas ,
  "Alocacoes" : lista_localidades,
  "Facilities Utilizadas" : lista_facilities
}

with open(saida, 'w', encoding='utf-8') as saidas:
    json.dump(resultados, saidas, indent=4)

def plot():
    # Coordenadas das localidades e facilities
    coord_localidades_x = [coord[0] for coord in L]
    coord_localidades_y = [coord[1] for coord in L]
    coord_facilities_x = [coord[0] for coord in F]
    coord_facilities_y = [coord[1] for coord in F]
    
    # Plotar métricas
    for i in range(l):
        x_localidade, y_localidade = L[i]
        tamanho_metrica_1 = M[i][0] * lambdas[0] * 30
        tamanho_metrica_2 = M[i][1] * lambdas[1] * 30
        
        plt.scatter(x_localidade + 0.5, y_localidade, s=tamanho_metrica_1, color='orange', alpha=0.5)  
        plt.scatter(x_localidade - 0.5, y_localidade, s=tamanho_metrica_2, color='green', alpha=0.5)   
        
    # Plotar localidades
    plt.scatter(coord_localidades_x, coord_localidades_y, color='black', label='Localidades')
    
    # Adicionar rótulos numéricos para localidades
    for i, coord in enumerate(L):
        plt.text(coord[0], coord[1], f'L{i+1}', fontsize=9, ha='right', va='bottom')
    
    # Plotar facilities usadas
    facilities_usadas_x = []
    facilities_usadas_y = []
    for j in range(f):
        if abs(y[j].varValue - 1 ) <= 0.1:
            facilities_usadas_x.append(F[j][0])
            facilities_usadas_y.append(F[j][1])
    plt.scatter(facilities_usadas_x, facilities_usadas_y, color='blue', label='Facilities Usadas')
    
    # Plotar facilities não usadas
    facilities_nao_usadas_x = []
    facilities_nao_usadas_y = []
    for j in range(f):
        if abs(y[j].varValue ) <= 0.1:
            facilities_nao_usadas_x.append(F[j][0])
            facilities_nao_usadas_y.append(F[j][1])
    plt.scatter(facilities_nao_usadas_x, facilities_nao_usadas_y, color='red', label='Facilities Não Usadas')
    
    # Adicionar rótulos numéricos para facilities
    for i, coord in enumerate(F):
        plt.text(coord[0], coord[1], f'F{i+1}', fontsize=9, ha='right', va='bottom')
    
    # Plotar alocação entre localidades e facilities 
    for i in range(l):
        for j in range(f):
            if abs(x[i][j].varValue - 1 ) <= 0.1 and abs(y[j].varValue - 1 ) <= 0.1:
                plt.plot([L[i][0], F[j][0]], [L[i][1], F[j][1]], color='gray')
    
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title('Solução')
    plt.legend()
    plt.grid(True)
    plt.show()
    
#Plotar
#plot()