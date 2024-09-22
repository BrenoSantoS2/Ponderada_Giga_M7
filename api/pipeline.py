import yfinance as yf
import pandas as pd

import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import numpy as np

from sklearn.metrics import mean_squared_error, mean_absolute_error


def explorar_dados(ativo):
    df = yf.download(ativo, start="2014-01-01", end="2024-01-01")
    df.to_csv(f'./data/raw/{ativo}.csv')
    return df

def treinar_modelo(ativo, memory_days=60):
    # Carregar dados
    df = pd.read_csv(f'./data/raw/{ativo}.csv')
    data = df.filter(['Close']).values

    # Escalar dados
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(data)
    
    # Dividir em treino/teste
    training_data_len = int(len(scaled_data) * 0.8)
    train_data = scaled_data[:training_data_len]

    # Criar sequências para o modelo LSTM
    X_train, y_train = [], []
    for i in range(memory_days, len(train_data)):
        X_train.append(train_data[i-memory_days:i])
        y_train.append(train_data[i])

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Definir e treinar o modelo LSTM
    model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(units=50, return_sequences=False, input_shape=(X_train.shape[1], 1)),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=10, batch_size=32)
    
    # Salvar o modelo treinado
    model.save(f'./models/{ativo}_model.h5')
    return model

def testar_modelo(ativo, memory_days=60):
    # Carregar modelo e dados
    model = tf.keras.models.load_model(f'../models/{ativo}_model.h5')
    df = pd.read_csv(f'./data/raw/{ativo}.csv')

    data = df.filter(['Close']).values
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(data)

    # Separar dados de teste
    training_data_len = int(len(scaled_data) * 0.8)
    test_data = scaled_data[training_data_len - memory_days:]
    X_test, y_test = [], scaled_data[training_data_len:]

    for i in range(memory_days, len(test_data)):
        X_test.append(test_data[i-memory_days:i])

    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    # Fazer previsões
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)

    # Calcular métricas
    mae = mean_absolute_error(y_test[:len(predictions)], predictions)
    mse = mean_squared_error(y_test[:len(predictions)], predictions)
    rmse = np.sqrt(mse)

    return mae, mse, rmse

def prever_valores(ativo, memory_days=60, prevision_days=7):
    model = tf.keras.models.load_model(f'../models/{ativo}_model.h5')
    df = pd.read_csv(f'../data/raw/{ativo}.csv')

    data = df.filter(['Close']).values
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(data)

    # Prever para os próximos 7 dias
    last_days = scaled_data[-memory_days:]
    predictions = []

    for _ in range(prevision_days):
        last_days = np.reshape(last_days, (1, memory_days, 1))
        next_price = model.predict(last_days)
        next_price = scaler.inverse_transform(next_price)
        predictions.append(next_price[0][0])
        last_days = np.append(last_days[:, 1:, :], next_price.reshape(1, 1, 1), axis=1)

    return np.array(predictions)

def retreinar_modelo(ativo, memory_days=60):
    df = yf.download(ativo, start="2014-01-01", end="2024-01-01")
    df.to_csv(f'./data/raw/{ativo}.csv')

    # Carregar dados
    df = pd.read_csv(f'../data/raw/{ativo}.csv')
    data = df.filter(['Close']).values

    # Escalar dados
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(data)
    
    # Dividir em treino/teste
    training_data_len = int(len(scaled_data) * 0.8)
    train_data = scaled_data[:training_data_len]

    # Criar sequências para o modelo LSTM
    X_train, y_train = [], []
    for i in range(memory_days, len(train_data)):
        X_train.append(train_data[i-memory_days:i])
        y_train.append(train_data[i])

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Definir e treinar o modelo LSTM
    model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(units=50, return_sequences=False, input_shape=(X_train.shape[1], 1)),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=10, batch_size=32)
    
    # Salvar o modelo treinado
    model.save(f'./models/{ativo}_model.h5')
    return model

def pipeline(ativo):
    print(f"Explorando dados do ativo {ativo}")
    explorar_dados(ativo)
    
    print(f"Treinando modelo para o ativo {ativo}")
    treinar_modelo(ativo)
    
    print(f"Testando modelo para o ativo {ativo}")
    mae, mse, rmse = testar_modelo(ativo)
    print(f"Métricas: MAE={mae}, MSE={mse}, RMSE={rmse}")
    
    print(f"Fazendo previsões para os próximos 7 dias para o ativo {ativo}")
    previsoes = prever_valores(ativo)
    print(f"Previsões: {previsoes}")

# Executar pipeline
if __name__ == "__main__":
    pipeline('ETH-USD')