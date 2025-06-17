import fiona
from shapely.geometry import shape, mapping
import json

# Caminho do arquivo GPKG
gpkg_path = 'AL_setores_CD2022.gpkg'

# Abrir o arquivo GPKG usando fiona
with fiona.open(gpkg_path, layer='AL_setores_CD2022') as src:
    # Converter as geometrias e propriedades para o formato GeoJSON
    features = [
        {
            "type": "Feature",
            "geometry": mapping(shape(feature['geometry'])),
            "properties": dict(feature['properties'])
        }
        for feature in src
    ]
    
    # Criar a estrutura GeoJSON
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

# Salvar como GeoJSON
geojson_path = 'AL_setores_CD2022.geojson'
with open(geojson_path, 'w') as f:
    json.dump(geojson, f)

geojson_path
