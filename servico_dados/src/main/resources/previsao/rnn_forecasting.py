from typing import Dict
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class DataProcessor:
    def __init__(self):
        self.scaler = MinMaxScaler()

    def fit_scaler(self, data):
        """Treina o scaler com os dados fornecidos."""
        self.scaler.fit(data.reshape(-1, 1))

    def normalize(self, data):
        """Normaliza os dados com o scaler treinado."""
        return self.scaler.transform(data.reshape(-1, 1))

    def inverse_transform(self, data):
        """Reverte a normalização para os valores originais."""
        return self.scaler.inverse_transform(data)

    @staticmethod
    def create_sequences(data, seq_length):
        """Cria sequências de entrada e saída para o modelo."""
        xs, ys = [], []
        for i in range(len(data) - seq_length):
            x = data[i:i + seq_length]
            y = data[i + seq_length]
            xs.append(x)
            ys.append(y)
        return np.array(xs), np.array(ys)


class RNNForecasting:
    model = None
    metrics = None

    def __init__(self, unit_id: int, model_type="LSTM", train_percentage=0.8, seq_length=12):
        """
        Inicializa a classe com o tipo de modelo desejado (LSTM ou GRU).

        Args:
            model_type (str): Tipo de modelo, "LSTM" ou "GRU". Default é "LSTM".
            train_percentage (float): Percentual de dados de treino.
            seq_length (int): Número de pontos em uma sequência.
        """
        if model_type not in ["LSTM", "GRU"]:
            raise ValueError("O tipo de modelo deve ser 'LSTM' ou 'GRU'.")
        
        self.logger = logging.getLogger(f"RNN_FORECASTING:{model_type}:{unit_id}")
        self.model_type = model_type
        self.train_percentage = train_percentage
        self.seq_length = seq_length
        self.data_processor = DataProcessor()

    def _build_model(self):
        """Constrói o modelo com base no tipo (LSTM ou GRU)."""
        model = Sequential()

        # Seleciona a camada correta (LSTM ou GRU)
        if self.model_type == "LSTM":
            model.add(LSTM(64, return_sequences=True, input_shape=(self.seq_length, 1)))
        elif self.model_type == "GRU":
            model.add(GRU(64, return_sequences=True, input_shape=(self.seq_length, 1)))
        
        model.add(Dropout(0.3))

        if self.model_type == "LSTM":
            model.add(LSTM(32, return_sequences=False))
        elif self.model_type == "GRU":
            model.add(GRU(32, return_sequences=False))
        
        model.add(Dropout(0.2))
        model.add(Dense(25, activation='relu'))
        model.add(Dense(1))
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def _split_data_by_percentage(self, data, train_percentage):
        """Divide os dados em treino e teste."""
        train_size = int(len(data) * train_percentage)
        train_data = data[:train_size]
        test_data = data[train_size:]
        self.logger.info(f"Tamanho do treino: {len(train_data)}, Tamanho do teste: {len(test_data)}")
        return train_data, test_data

    def train(self, input_json: Dict[str, int]):
        """Treina o modelo com base nos dados fornecidos."""
        self.logger.info("Início do treinamento")
        try:
            df = self._prepare_data(input_json)
            data_scaled = self._process_data(df)
            
            train_data, test_data = self._split_data_by_percentage(data_scaled, self.train_percentage)
            X_train, y_train, X_test, y_test = self._prepare_train_test_sets(train_data, test_data)
            
            model = self._train_model(X_train, y_train)
            self.model = model

            if X_test.size > 0:
                self._evaluate_model(model, X_test, y_test)
            else:
                self.logger.warning("Modelo treinado, mas o conjunto de teste é vazio. Métricas não calculadas.")
                self.metrics = None

        except Exception as e:
            self.logger.error(f"Erro ao realizar o treinamento: {e}")
            raise

    def _prepare_data(self, input_json: Dict[str, int]) -> pd.DataFrame:
        """Converte os dados JSON para um DataFrame e realiza validações."""
        df = pd.DataFrame(list(input_json.items()), columns=['data', 'quantidade'])
        df['data'] = pd.to_datetime(df['data'])
        df.set_index('data', inplace=True)
        df = df.sort_index()
        
        if df['quantidade'].isnull().any() or not np.issubdtype(df['quantidade'].dtype, np.number):
            raise ValueError("Os dados contêm valores inválidos ou não numéricos.")

        return df

    def _process_data(self, df: pd.DataFrame) -> np.ndarray:
        """Normaliza os dados para preparação de treinamento."""
        data = df['quantidade'].values
        self.data_processor.fit_scaler(data)
        return self.data_processor.normalize(data)

    def _prepare_train_test_sets(self, train_data: np.ndarray, test_data: np.ndarray):
        """Prepara os conjuntos de treino e teste, incluindo a criação de sequências."""
        X_train, y_train = self.data_processor.create_sequences(train_data, self.seq_length)
        X_test, y_test = self.data_processor.create_sequences(test_data, self.seq_length)

        self.logger.info(f"Dimensões X_train: {X_train.shape}, y_train: {y_train.shape}")
        self.logger.info(f"Dimensões X_test: {X_test.shape}, y_test: {y_test.shape}")

        if X_test.size == 0 or y_test.size == 0:
            self.logger.warning(
                "Conjunto de teste insuficiente para avaliação. Considere aumentar os dados ou ajustar o seq_length."
            )
            X_test, y_test = np.array([]), np.array([])

        X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        if X_test.size > 0:
            X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
        
        return X_train, y_train, X_test, y_test

    def _train_model(self, X_train: np.ndarray, y_train: np.ndarray):
        """Treina o modelo usando os dados fornecidos."""
        model = self._build_model()
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        model.fit(
            X_train, y_train,
            epochs=100, batch_size=64,
            validation_split=0.2, callbacks=[early_stop], verbose=1
        )
        return model

    def _evaluate_model(self, model, X_test: np.ndarray, y_test: np.ndarray):
        """Avalia o modelo e calcula métricas de desempenho."""
        y_pred = model.predict(X_test)
        y_test_inverse = self.data_processor.inverse_transform(y_test.reshape(-1, 1))
        y_pred_inverse = self.data_processor.inverse_transform(y_pred)

        mae = mean_absolute_error(y_test_inverse, y_pred_inverse)
        rmse = np.sqrt(mean_squared_error(y_test_inverse, y_pred_inverse))
        mape = mean_absolute_percentage_error(y_test_inverse, y_pred_inverse) * 100

        self.metrics = {"mae": mae, "rmse": rmse, "mape": mape}
        self.logger.info(f"Treinamento realizado com sucesso!\nMAE: {mae:.2f}, RMSE: {rmse:.2f}, MAPE: {mape:.2f}%")

    def predict(self, input_array):
        """Realiza predições com base em um array de entrada."""
        self.logger.info("Início da predição")
        try:
            if self.model is None:
                raise ValueError("O modelo não foi treinado ainda. Execute o método 'train' antes de prever.")

            if len(input_array) < self.seq_length:
                raise ValueError(f"Os dados de entrada devem ter pelo menos {self.seq_length} pontos para criar uma sequência.")

            data_scaled = self.data_processor.normalize(np.array(input_array).reshape(-1, 1))
            sequence = data_scaled[-self.seq_length:].reshape(1, self.seq_length, 1)

            prediction_scaled = self.model.predict(sequence)
            prediction = self.data_processor.inverse_transform(prediction_scaled)[0][0]
            prediction = np.round(prediction).astype(int)

            self.logger.info(f"Predição realizada com sucesso! Resultado: {prediction}")
            return prediction
        except Exception as e:
            self.logger.error(f"Erro durante a predição: {e}")
            return None
