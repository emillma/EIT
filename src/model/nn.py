
from typing import List

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, TerminateOnNaN
from tensorflow.keras.losses import mean_squared_error
from sklearn.cross_decomposition import PLSRegression
import pandas as pd

from model import LogisticModel


class MGNN:

    def __init__(self, config: dict) -> None:
        layers = config["layers"]
        self.l3_model = Sequential()
        self.l3_model.add(BatchNormalization())
        for i in range(len(layers)):
            if i == 0:
                self.l3_model.add(Input(layers[i]['width']))
            else:
                self.l3_model.add(Dense(layers[i]["width"],
                                        activation=layers[i]["activation"]))
            self.l3_model.add(Dropout(config["dropout"]))
        self.l3_model.add(Dense(1, activation='linear'))

        self.l2_model = PLSRegression(n_components=1)

        self.l1_model = LogisticModel(config["num_weather_params"])

    def train(self, config: dict, train_X: pd.DataFrame, train_Y: pd.DataFrame, last_year_key: str, weather_keys: List[str]):

        self.l1_model.fit(train_X, train_Y, last_year_key, weather_keys)

        l1_prediction = self.l1_model.predict(
            train_X[last_year_key].to_numpy(), train_X[weather_keys].to_numpy())
        l1_error = train_Y - l1_prediction
        train_X["l1_prediction"] = l1_prediction

        self.l2_model.fit(train_X, l1_error)

        l2_prediction = self.l2_model.predict(train_X).reshape(l1_error.shape)
        train_X["l2_prediction"] = l2_prediction

        remaining_error = l1_error - l2_prediction

        # Hyper-parameters of the training process
        num_epochs = config["epochs"]
        batch_size = config["batch_size"]
        val_frac = config["val_frac"]
        patience_val = config["patience_val"]

        self.l3_model.compile(loss=mean_squared_error,
                              optimizer=config["optimizer"],
                              metrics=[mean_squared_error])

        early_stopping = EarlyStopping(
            monitor='val_loss', patience=patience_val, verbose=1)

        print(f'Running... {config["optimizer"]}')
        self.l3_model.fit(train_X, remaining_error,
                          batch_size=batch_size,
                          epochs=num_epochs,
                          verbose=1,
                          validation_split=val_frac, callbacks=[early_stopping, TerminateOnNaN()])

    def predict(self, inputs: pd.DataFrame, last_year_key: str, weather_keys: List[str]):
        l1_prediction = self.l1_model.predict(
            inputs[last_year_key].to_numpy(), inputs[weather_keys].to_numpy())
        inputs["l1_prediction"] = l1_prediction

        l2_prediction = self.l2_model.predict(
            inputs).reshape(l1_prediction.shape)
        inputs["l2_prediction"] = l2_prediction

        nn_prediction = self.l3_model.predict(inputs)

        return l1_prediction + l2_prediction + nn_prediction

    def test(self, inputs: pd.DataFrame, targets: pd.DataFrame, last_year_key: str, weather_keys: List[str]):
        l1_prediction = self.l1_model.predict(
            inputs[last_year_key].to_numpy(), inputs[weather_keys].to_numpy())
        inputs["l1_prediction"] = l1_prediction

        l2_prediction = self.l2_model.predict(
            inputs).reshape(l1_prediction.shape)
        inputs["l2_prediction"] = l2_prediction

        remaining_error = targets - l1_prediction - l2_prediction

        test_score = self.l3_model.evaluate(inputs, remaining_error)
        return test_score
