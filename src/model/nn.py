
from __future__ import print_function
from typing import List

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, TerminateOnNaN
from tensorflow.keras.losses import mean_squared_error
import pandas as pd

from model.model import LogisticModel


class MGNN:

    def __init__(self, config: dict) -> None:
        layers = config["layers"]
        self.l3_model = Sequential()
        for i in range(len(layers)):
            if i == 0:
                self.l3_model.add(Input(layers[i]['nodes']))
            else:
                self.l3_model.add(Dense(layers[i]["nodes"],
                                        activation=layers[i]["activation"]))
            self.l3_model.add(Dropout(config["dropout_frac"]))
        self.l3_model.add(Dense(1, activation='linear'))

        self.l1_model = LogisticModel(config["num_weather_params"])

    def train(self, config: dict, train_X: pd.DataFrame, train_Y: pd.DataFrame, last_year_key: str, weather_keys: List[str]):

        self.l1_model.fit(train_X, train_Y)

        model_prediction = self.l1_model.predict(
            train_X[last_year_key], train_X[weather_keys])
        
        model_error = train_Y - model_prediction

        train_X["model_prediction"] = model_prediction

        # Hyper-parameters of the training process
        num_epochs = config["epochs"]
        batch_size = config["batch_size"]
        val_frac = config["val_frac"]
        patience_val = config["patience_val"]

        self.l3_model.compile(loss=mean_squared_error,
                              optimizer=config["optimizer"],
                              metrics=[mean_squared_error])

        early_stopping = EarlyStopping(
            monitor='val_loss_1', patience=patience_val, verbose=1)

        print(f'Running... {config["optimizer"]}')
        self.l3_model.fit(train_X, model_error,
                          batch_size=batch_size,
                          epochs=num_epochs,
                          verbose=1,
                          validation_split=val_frac, callbacks=[early_stopping, TerminateOnNaN()])

    def save_models(self, model_name):
        self.new_method(model_name)

    def predict(self, inputs: pd.DataFrame, last_year_key: str, weather_keys: List[str]):
        model_prediction = self.l1_model.predict(
            inputs[last_year_key], inputs[weather_keys])
        inputs["model_prediction"] = model_prediction
        nn_prediction = self.l3_model.predict(inputs)

        return model_prediction + nn_prediction

    def test(self, testX: pd.DataFrame, testY: pd.DataFrame, last_year_key: str, weather_keys: List[str]):
        model_prediction = self.l1_model.predict(
            testX[last_year_key], testX[weather_keys])
        testX["model_prediction"] = model_prediction
        model_error = model_prediction - testY
        test_score = self.l3_model.evaluate(testX, model_error)
        return test_score
