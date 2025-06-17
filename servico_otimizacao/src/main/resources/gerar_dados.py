import json
import folium
import numpy as np
import pandas as pd
from shapely.geometry import Polygon
import random

# Selecionar a cidade
cidade = 'Garanhuns'

# Dados das cidades
dados_cidades = {
    'Garanhuns': {
        'setores_csv': 'planilhas/setores_pe.csv',
        'localidades_csv': 'planilhas/localidades_garanhuns.csv',
        'coordenadas_centro': [-8.89106439321296, -36.49339283297139],
        #o numero de facilities foi extraido do site das prefeituras
        'numero_facilities': 39,
        'poligonos': 'planilhas/malha_garanhuns.json',
        'centros_fixos': 'planilhas/fixados_Garanhuns.json'
    },
    'Recife': {
        'setores_csv': 'planilhas/setores_pe.csv',
        'localidades_csv': 'planilhas/localidades_recife.csv',
        'coordenadas_centro': [-8.058260309612239, -34.88203670720981],
        'numero_facilities': 290,
        'poligonos': 'planilhas/malha_recife.json',
        'centros_fixos': 'planilhas/fixados_Recife.json'
    },
    'Maceió': {
        'setores_csv': 'planilhas/setores_al.csv',
        'localidades_csv': 'planilhas/localidades_maceio.csv',
        'coordenadas_centro': [-9.665517080399974, -35.730751728241714],
        'numero_facilities': 76,
        'poligonos': 'planilhas/malha_maceio.json',
        'centros_fixos': 'planilhas/fixados_Maceió.json'
    }
}

# Carregar arquivos CSV
setores_csv = dados_cidades[cidade]['setores_csv']
localidades_csv = dados_cidades[cidade]['localidades_csv']
coordenadas_centro = dados_cidades[cidade]['coordenadas_centro']

numero_facilities = dados_cidades[cidade]['numero_facilities']

setores_da_cidade = pd.read_csv(setores_csv, delimiter=',', low_memory=False, encoding='utf-8')
localidades = pd.read_csv(localidades_csv, delimiter=';', low_memory=False, encoding='utf-8')

    
# Carregar e filtrar polígonos
with open(dados_cidades[cidade]['poligonos'], 'r', encoding='utf-8') as f:
    dados_poligonos = json.load(f)

# Filtrar os polígonos pela cidade específica
dados_poligonos['features'] = [feature for feature in dados_poligonos['features'] if feature['properties']['NM_MUN'] == cidade]

# Função para corrigir o formato da latitude e longitude
def corrigir_coordenadas(coordenada):
    if isinstance(coordenada, float):
        return coordenada
    partes = coordenada.split('.')
    if len(partes) > 2:
        return float(partes[0] + '.' + ''.join(partes[1:]))
    return float(coordenada)

# Corrigir e converter as coordenadas para floats
localidades['LATITUDE'] = localidades['LATITUDE'].apply(lambda x: corrigir_coordenadas(str(x)))
localidades['LONGITUDE'] = localidades['LONGITUDE'].apply(lambda x: corrigir_coordenadas(str(x)))
setores_da_cidade['AREA_KM2'] = setores_da_cidade['AREA_KM2'].apply(lambda x: float(str(x).replace('.', '', str(x).count('.') - 1).replace(',', '.')))
setores_da_cidade['Total de pessoas'] = setores_da_cidade['v0001'].apply(lambda x: int(x))

# Filtrar setores pela cidade específica
setores_da_cidade = setores_da_cidade[setores_da_cidade['NM_MUN'] == cidade]
numero_setores = setores_da_cidade.shape[0]

# Atualizar o número de setores no dicionário de dados da cidade
dados_cidades[cidade]['numero_setores'] = numero_setores
dados_setores = []

facilities = []

# Agrupar as localidades por COD_SETOR
localidades_por_setor = localidades.groupby('COD_SETOR')[['LATITUDE', 'LONGITUDE']].apply(lambda x: x.values.tolist()).to_dict()
localidades_por_cep = localidades.groupby('COD_SETOR')['CEP'].apply(set).to_dict()

# Criar um mapa centrado na cidade
mapa = folium.Map(location=coordenadas_centro, zoom_start=12)

# Número máximo de setores a serem considerados
l = numero_setores

# Iterar sobre os setores e calcular informações
contador_setores = 0
poligonos_setores = []

centros_de_massa = pd.DataFrame(columns=['COD_SETOR', 'LATITUDE', 'LONGITUDE'])

for codigo, group in setores_da_cidade.groupby('COD_SETOR'):
    if contador_setores >= l:
        break

    area = group['AREA_KM2'].iloc[0]
    total_pessoas = int(group['Total de pessoas'].iloc[0])
    densidade = total_pessoas / area
    
    coordenadas = localidades_por_setor.get(codigo, [])
    ceps = list(localidades_por_cep.get(codigo, set()))
    
    # Encontrar o polígono correspondente ao setor
    polygon = None
    for feature in dados_poligonos['features']:
        if feature['properties']['CD_SETOR'] == codigo:
            coordinates = feature['geometry']['coordinates'][0]
            # Verificar se coordinates contém sublistas adicionais
            if isinstance(coordinates[0][0], list):
                coordinates = coordinates[0]  
            polygon = Polygon(coordinates)
            poligonos_setores.append((polygon, codigo))
            folium.GeoJson(feature).add_to(mapa)
            break

    if not polygon:
        continue  # Pular setores sem polígonos válidos

    # Calcular o centro de massa do polígono
    if polygon.is_valid:
        centro_de_massa = polygon.centroid
        centro_de_massa_lat = centro_de_massa.y
        centro_de_massa_lon = centro_de_massa.x
    else:
        print(f"Polígono inválido para o setor {codigo}. Usando coordenadas das localidades.")
        if coordenadas:
            coordenadas_array = np.array(coordenadas)
            centro_de_massa = np.mean(coordenadas_array, axis=0)
            centro_de_massa_lat = centro_de_massa[0]
            centro_de_massa_lon = centro_de_massa[1]
        else:
            print(f"Nenhuma coordenada disponível para o setor {codigo}.")
            continue

    # Adicionar centro de massa ao DataFrame
    novo_centro = pd.DataFrame({'COD_SETOR': [codigo], 'LATITUDE': [centro_de_massa_lat], 'LONGITUDE': [centro_de_massa_lon]})
    centros_de_massa = pd.concat([centros_de_massa, novo_centro], ignore_index=True)

    dados_setor = {
        "codigo": codigo,
        "total_moradores": total_pessoas,
        "coordenada": [centro_de_massa_lat, centro_de_massa_lon]
    }
    
    dados_setores.append(dados_setor)
    
    contador_setores += 1

# Facilities

with open(dados_cidades[cidade]['centros_fixos'], 'r', encoding='utf-8') as f:
    fixados_json = json.load(f)

# Criar um dicionário para mapear os centros fixados por código de setor
fixados_map = {}
for fixado in fixados_json['centros_fixados']:
    cod_setor = fixado['cod_setor']
    latitude = fixado['coordenadas']['latitude']
    longitude = fixado['coordenadas']['longitude']
    fixados_map[cod_setor] = (latitude, longitude)

# Marcar setores fixados e definir facilities aleatórias para outros setores
num_fixados = 0
num_facilities = numero_facilities
facilities_fixas = []

for setor in dados_setores:
    cod_setor = setor['codigo']
    if cod_setor in fixados_map:
        facility = {
            "coordenada": [fixados_map[cod_setor][0], fixados_map[cod_setor][1]],
            "fixed": True,
            
        }
        facilities_fixas.append(facility)
        facilities.append(facility)
        num_fixados += 1

num_a_adicionar = num_facilities - num_fixados

indices_nao_fixados = [i for i, setor in enumerate(dados_setores) if not any(setor['codigo'] == fixado['cod_setor'] for fixado in fixados_json['centros_fixados'])]

random.seed(42)
indices_aleatorios = random.sample(indices_nao_fixados, min(num_a_adicionar, len(indices_nao_fixados)))

# Adicionar os setores selecionados aleatoriamente como facilities no JSON
for i in indices_aleatorios:
    facilities.append({
        "coordenada": dados_setores[i]['coordenada'],
        "fixed": False,
    })

    
    
def gerar_metricas(n, m):
    return [[random.uniform(0, 15) for _ in range(m)] for _ in range(n)]

# Gerar métricas
metricas = gerar_metricas(len(dados_setores), 2)

# Adicionar métricas aos setores
for i, setor in enumerate(dados_setores):
    setor["metricas"] = metricas[i]


# Custos
def gerar_custos(n):
    return [random.uniform(10, 100) for _ in range(n)]

# Filtrar as facilities para as quais adicionar custos
facilities_para_custo = [f for f in facilities if not f.get('fixed', True)]

# Gerar custos apenas para as facilities filtradas
custos = gerar_custos(len(facilities_para_custo))

# Associar os custos às facilities corretas
for i, facility in enumerate(facilities_para_custo):
    facility["custo"] = custos[i]


# Capacidade de alocação
def gerar_cap(n):
    return [random.randint(0, (numero_setores - numero_facilities)) for _ in range(n)]

cap = gerar_cap(num_facilities)

for i, setor in enumerate(facilities):
    setor["capacidade"] = cap.pop(0)

k = 23
arquivoSaida = f"output_{cidade}.json"
# Estrutura final do JSON
json_data = {
    "localidades": dados_setores,
    "facilities": facilities,
    "tipo_problema": 1,
    "arquivo_saida": arquivoSaida,
    "num_centros_desejado": k,
    "nome_metricas": ["Dengue", "IDH"],
    "coordenada": ["Latitude", "Longitude"]
}

saida = f'dados_{cidade}.json'
with open(saida, 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

# Adicionar marcadores para localidades
for localidade in dados_setores:
    folium.Marker(
        location=localidade["coordenada"],
        popup=f"Localidade: {localidade['codigo']}",
        icon=folium.Icon(color='blue')
    ).add_to(mapa)

# Adicionar marcadores para facilities
for facility in facilities:
    color = 'pink' if facility['fixed'] else 'green'
    folium.Marker(
        location=facility["coordenada"],
        popup=f"Facility: {facility['coordenada']}, Custo: {facility.get('custo', 0.0)}",
        icon=folium.Icon(color=color)
    ).add_to(mapa)

mapa.save(f'mapa_{cidade}.html')

print("Processo concluído. Arquivos JSON e HTML gerados com sucesso.")
