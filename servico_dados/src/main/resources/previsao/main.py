from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import sys
import logging
from typing import Optional, Tuple, Dict, List, Any
from rnn_forecasting import RNNForecasting

MAX_WORKERS = os.cpu_count()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()


def load_json(filepath: str) -> Dict[str, Any]:
    """
    Carrega dados de um arquivo JSON.

    Args:
        filepath (str): Caminho para o arquivo JSON.

    Returns:
        Dict[str, Any]: Dados carregados do JSON.

    Raises:
        ValueError: Se ocorrer um erro ao ler o arquivo.
    """
    try:
        with open(filepath, encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"Arquivo JSON '{filepath}' carregado com sucesso.")
        return data
    except Exception as e:
        logger.error(f"Erro ao abrir ou ler o arquivo JSON '{filepath}': {e}")
        raise ValueError(f"Erro ao abrir ou ler o arquivo JSON '{filepath}': {e}")

def extract_parameters(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, Dict[str, Any]]:
    """
    Extrai parâmetros necessários do JSON de entrada.

    Args:
        data (Dict[str, Any]): Dados carregados do JSON de entrada.

    Returns:
        Tuple[Dict[str, Any], int, Dict[str, Any]]:
            - historical_data: Dados de atendimentos por unidade.
            - prediction_window: Número de meses para previsão.
            - training_data: Dados de treinamento por unidade.
    """
    historical_data = data.get('dados_atendimentos', {})
    prediction_window = data.get('janela_de_predicao', 1)
    training_data = data.get('dados_treinamento', {})
    logger.info("Parâmetros extraídos com sucesso.")
    return historical_data, prediction_window, training_data

def prepare_data_for_forecasting(
    historical_data: Dict[str, Any], 
    training_data: Dict[str, Dict[str, int]], 
    prediction_window: int
) -> List[Dict[str, Any]]:
    """
    Prepara os dados históricos para fazer previsões.

    Args:
        historical_data (Dict[str, Any]): Dados históricos de atendimentos por unidade.
        training_data (Dict[str, Dict[str, int]]): Dados de treinamento por unidade.
        prediction_window (int): Número de meses para previsão.

    Returns:
        List[Dict[str, Any]]: Lista de dados preparados para previsão.
    """
    logger.info("Preparando dados para previsão...")
    prepared_data = [
        {
            'unit_id': unit_id,
            'data': data.get('dados', []),
            'training_data': training_data.get(unit_id, {}),
            'current_month': data.get('mes'),
            'current_year': data.get('ano'),
            'prediction_window': prediction_window
        }
        for unit_id, data in historical_data.items()
    ]
    logger.info("Dados preparados com sucesso.")
    return prepared_data

def train_models(data: Dict[str, Any], model_types: List[str]) -> Dict[str, Tuple[Any, Optional[Dict[str, float]]]]:
    """
    Treina os modelos especificados e retorna um dicionário com os modelos e suas métricas.

    Args:
        data (Dict[str, Any]): Dados para treinamento.
        model_types (List[str]): Lista dos tipos de modelos a serem treinados.

    Returns:
        Dict[str, Tuple[Any, Optional[Dict[str, float]]]]: Dicionário com os modelos e suas métricas.
    """
    models = {}
    for model_type in model_types:
        model = RNNForecasting(unit_id=data.get("unit_id"), model_type=model_type)
        model.train(data.get("training_data"))
        models[model_type] = (model, model.metrics)
    return models


def select_best_model(models: Dict[str, Tuple[Any, Optional[Dict[str, float]]]]) -> Any:
    """
    Seleciona o melhor modelo com base no menor MAE.

    Args:
        models (Dict[str, Tuple[Any, Optional[Dict[str, float]]]]): Dicionário com modelos e suas métricas.

    Returns:
        Any: Instância do modelo com melhor desempenho.
    """
    best_model_type = None
    best_model = None
    best_mae = float('inf')
    
    for model_type, (model, metrics) in models.items():
        if metrics and metrics['mae'] < best_mae:
            best_model_type = model_type
            best_model = model
            best_mae = metrics['mae']

    if best_model_type:
        logger.info(f"Melhor modelo selecionado: {best_model_type} com MAE de {best_mae}")
    else:
        logger.warning("Nenhum modelo válido encontrado. Retornando o primeiro modelo.")

    # Retorna o primeiro modelo válido caso nenhum tenha métricas
    return best_model if best_model else next(iter(models.values()))[0]


def build_prediction_result(unit_id: int, prediction: List[float], current_month: int, current_year: int, prediction_window: int) -> Dict[str, Any]:
    """
    Monta o resultado da previsão com os dados fornecidos.

    Args:
        unit_id (int): Identificador da unidade.
        prediction (List[float]): Dados previstos.
        current_month (int): Mês atual.
        current_year (int): Ano atual.
        prediction_window (int): Janela de previsão.

    Returns:
        Dict[str, Any]: Resultado da previsão formatado.
    """
    prediction_month, prediction_year = get_prediction_date(current_month, current_year, prediction_window)
    
    return {
        "unit_id": unit_id,
        "mes": prediction_month,
        "ano": prediction_year,
        "dados": prediction
    }


def process_single_prediction(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa uma única previsão de unidade, treinando os modelos, selecionando o de menor erro e gerando o resultado.
    Args:
        data (Dict[str, Any]): Dados para uma unidade específica.

    Returns:
        Dict[str, Any]: Previsões e informações sobre o modelo escolhido.
    """
    model_types = ["LSTM", "GRU"]  # Pode ser expandido no futuro
    models = train_models(data, model_types)

    best_model = select_best_model(models)

    best_prediction = best_model.predict(data.get('data'))

    return build_prediction_result(
        unit_id=data.get('unit_id'),
        prediction=best_prediction,
        current_month=data.get('current_month'),
        current_year=data.get('current_year'),
        prediction_window=data.get('prediction_window')
    )

def process_predictions_and_save(prepared_data: List[Dict[str, Any]], output_file: str):
    """
    Processa as previsões em paralelo e salva diretamente em um arquivo.
    """
    logger.info("Iniciando o processamento das previsões...")

    predictions_by_unit = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_unit = {executor.submit(process_single_prediction, data): data for data in prepared_data}
        
        for future in as_completed(future_to_unit):
            try:
                result = future.result()
                predictions_by_unit[result['unit_id']] = {
                    "mes": result["mes"],
                    "ano": result["ano"],
                    "dados": [result["dados"].tolist()],
                }
            except Exception as e:
                logger.error(f"Erro ao processar a previsão para uma unidade: {e}")

    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump({ "dados": predictions_by_unit}, file, indent=4, ensure_ascii=False)
        logger.info(f"Previsões salvas com sucesso no arquivo {output_file}")
    except Exception as e:
        logger.error(f"Erro ao salvar as previsões no arquivo '{output_file}': {e}")
        raise ValueError(f"Erro ao salvar as previsões no arquivo '{output_file}': {e}")

def get_prediction_date(current_month: int, current_year: int, prediction_window: int) -> Tuple[int, int]:
    """
    Retorna o mês e o ano de acordo com a janela de previsão.

    Args:
        current_month (int): Mês atual da previsão (1-12).
        current_year (int): Ano atual da previsão.
        prediction_window (int): Número de meses para previsão.

    Returns:
        Tuple[int, int]: Novo mês e ano para a previsão.
    """
    total_months = current_month + prediction_window - 1
    prediction_year = current_year + total_months // 12
    prediction_month = (total_months % 12) + 1
    return prediction_month, prediction_year

def main():
    """
    Função principal que orquestra o fluxo de execução do script.
    """
    if len(sys.argv) != 3:
        logger.error("Uso incorreto. Use: python3 <nome_do_arquivo>.py <entrada.json> <saida.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        data = load_json(input_file)
        historical_data, prediction_window, training_data = extract_parameters(data)
        prepared_data = prepare_data_for_forecasting(historical_data, training_data, prediction_window)
        process_predictions_and_save(prepared_data, output_file)
    except Exception as e:
        logger.error(f"Erro durante a execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
