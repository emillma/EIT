
from typing import List
from joblib import dump, load
import os
import numpy as np

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Input, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam, Adadelta, Adagrad, SGD, RMSprop
from tensorflow.keras.callbacks import EarlyStopping, TerminateOnNaN
from tensorflow.keras.losses import mean_squared_error
from sklearn.cross_decomposition import PLSRegression
import pandas as pd

from model import LogisticModel

optimizers = {
    'adam': Adam,
    'adadelta': Adadelta,
    'adagrad': Adagrad,
    'sgd': SGD,
    'rmsprop': RMSprop,
}


class MGNN:

    def __init__(self, config: dict) -> None:
        if config["load"]:
            self.load_model_from_file(config["source_dir"])
        else:
            layers = config["layers"]
            self.l3_model = Sequential()
            self.l3_model.add(Input(layers[0]['width']))
            for i in range(1, len(layers)):
                self.l3_model.add(Dense(layers[i]["width"],
                                        activation=layers[i]["activation"]))
            self.l3_model.add(Dropout(config["dropout"]))
            self.l3_model.add(Dense(1, activation='sigmoid'))

            self.l2_model = PLSRegression(
                n_components=config["plsr_components"])

            self.l1_model = LogisticModel(config["num_weather_params"])

    def dump_model_to_file(self, destination: str):
        dirname = os.path.dirname(__file__)
        dirname = os.path.join(dirname, destination)
        os.makedirs("src/model/"+destination, exist_ok=True)
        l1_path = os.path.join(dirname, "l1_model.joblib")
        l2_path = os.path.join(dirname, "l2_model.joblib")
        l3_path = os.path.join(dirname, "l3_model.h5")

        with open(l1_path, "wb") as file:
            dump(self.l1_model, file)
        with open(l2_path, "wb") as file:
            dump(self.l2_model, l2_path)
        self.l3_model.save(l3_path)

    def load_model_from_file(self, source: str):
        dirname = os.path.dirname(__file__)
        dirname = os.path.join(dirname, source)
        l1_path = os.path.join(dirname, "l1_model.joblib")
        l2_path = os.path.join(dirname, "l2_model.joblib")
        l3_path = os.path.join(dirname, "l3_model.h5")

        self.l1_model = load(l1_path)
        self.l2_model = load(l2_path)
        self.l3_model = load_model(l3_path)

    def train(self, config: dict, train_X: pd.DataFrame, train_Y: pd.DataFrame, last_year_key: str, weather_keys: List[str]):

        self.l1_model.fit(train_X, train_Y, last_year_key, weather_keys)

        l1_prediction = self.l1_model.predict(
            train_X[last_year_key].to_numpy(), train_X[weather_keys].to_numpy())
        l1_error = l1_prediction - train_Y
        train_X["l1_prediction"] = l1_prediction

        self.l2_model.fit(train_X, l1_error)

        l2_prediction = self.l2_model.predict(train_X).reshape(l1_error.shape)

        for i, loading in enumerate(self.l2_model.x_scores_.T):
            train_X[f"l2_loading_{i}"] = loading
        train_X["l2_prediction"] = l2_prediction

        l2_error = (l1_prediction + l2_prediction) - train_Y
        self.l3_error_scaling = np.std(l2_error) * 3 * 2
        self.l3_error_mean = np.mean(l2_error)

        l2_error = ((l2_error - self.l3_error_mean)
                    / self.l3_error_scaling + 0.5)

        # Hyper-parameters of the training process
        num_epochs = config["epochs"]
        batch_size = config["batch_size"]
        val_frac = config["val_frac"]
        patience_val = config["patience_val"]

        self.l3_model.compile(loss=mean_squared_error,
                              optimizer=optimizers[config["optimizer"]](
                                  config["learning_rate"]),
                              metrics=[mean_squared_error])

        self.l3_model.summary()

        early_stopping = EarlyStopping(
            monitor='val_loss', patience=patience_val, verbose=1)

        print(f'Running... {config["optimizer"]}')
        return self.l3_model.fit(train_X, l2_error,
                                 batch_size=batch_size,
                                 epochs=num_epochs,
                                 verbose=1,
                                 validation_split=val_frac, callbacks=[TerminateOnNaN(), early_stopping])

    def predict(self, inputs: pd.DataFrame, last_year_key: str, weather_keys: List[str]):
        l1_prediction = self.l1_model.predict(
            inputs[last_year_key].to_numpy(), inputs[weather_keys].to_numpy())
        inputs["l1_prediction"] = l1_prediction

        l2_prediction = self.l2_model.predict(
            inputs).reshape(l1_prediction.shape)

        for i, loading in enumerate(self.l2_model.transform(inputs).T):
            inputs[f"l2_loading_{i}"] = loading

        inputs["l2_prediction"] = l2_prediction
        nn_prediction = self.l3_model.predict(inputs)

        nn_prediction = ((nn_prediction - 0.5) * self.l3_error_scaling
                         + self.l3_error_mean)

        return l1_prediction + l2_prediction + np.squeeze(nn_prediction)

    def test(self, inputs: pd.DataFrame, targets: pd.DataFrame, last_year_key: str, weather_keys: List[str]):
        inputs_copy = inputs.copy()
        l1_test_error, l1_error, l1_predictions = self.l1_model.test(
            inputs_copy, targets, last_year_key, weather_keys)
        inputs_copy["l1_prediction"] = l1_predictions

        l2_predictions = self.l2_model.predict(
            inputs_copy).reshape(l1_error.shape)
        for i, loading in enumerate(self.l2_model.transform(inputs_copy).T):
            inputs_copy[f"l2_loading_{i}"] = loading
        inputs_copy["l2_prediction"] = l2_predictions

        l2_error = (l1_predictions + l2_predictions) - targets

        upto_l2_error = np.mean(
            ((l1_predictions + l2_predictions) - targets)**2)

        l2_error_adj = ((l2_error - self.l3_error_mean)
                        / self.l3_error_scaling + 0.5)

        l2_test_error = np.mean((l1_error - l2_predictions)**2)

        l3_test_error = self.l3_model.evaluate(inputs_copy, l2_error_adj)[0]

        predictions = self.predict(inputs, last_year_key, weather_keys)
        l3_error = targets - predictions
        test_score = np.mean((targets - predictions)**2)

        return test_score, l3_test_error, l2_test_error, l1_test_error, upto_l2_error, l1_error.to_numpy(), l2_error.to_numpy(), l3_error.to_numpy()
