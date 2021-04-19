from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize
import sklearn.metrics as sm

# Based on https://www.researchgate.net/publication/238106949_Impacts_of_Climate_Changes_on_Elk_Population_Dynamics_in_Rocky_Mountain_National_Park_Colorado_USA


class LogisticModel:

    def __init__(self, num_weather_vars: int):
        self.num_weather_vars = num_weather_vars
        self.a = np.zeros(num_weather_vars)
        self.K = 0.5
        self.R0 = 0.5

    def predict(self, last_year: np.ndarray, weather: np.ndarray) -> float:
        return last_year + last_year * self.get_R(weather) * (1 - last_year/self.K)

    def get_R(self, weather: np.ndarray) -> float:
        return self.R0 + np.sum(self.a * weather)

    def objective_function(self, inputs: np.ndarray, *args):
        self.K = inputs[0]
        self.R0 = inputs[1]
        self.a = inputs[2:]
        predictions = self.predict(args[1], args[2])
        return np.sum((args[0] - predictions)**2)

    def fit(self, inputs: pd.DataFrame, targets: pd.DataFrame, last_year_key: str, weather_keys: List[str]):
        """
        input: time x params
        targets: time x targets
        """
        x0 = np.random.random(2 + self.num_weather_vars)
        final_params = minimize(
            self.objective_function, x0, args=(targets, inputs[last_year_key].to_numpy(), inputs[weather_keys].to_numpy()), method="nelder-mead")

        self.K = final_params.x[0]
        self.R0 = final_params.x[1]
        self.a = final_params.x[2:]

    def test(self, inputs: pd.DataFrame, targets: pd.DataFrame, last_year_key: str, weather_keys: List[str]) -> Tuple[float]:
        predictions = self.predict(
            inputs[last_year_key].to_numpy(), inputs[weather_keys].to_numpy())

        return sm.mean_squared_error(targets, predictions), targets - predictions, predictions


if __name__ == "__main__":
    inputs_dict = {
        "last_year": [100, 101, 105, 120, 130],
        "w0": [0.1, 0.4, 0.2, 0.4, 0.1],
        "w1": [0.2, 0.5, 0.4, 0.7, 0.6],
        "w2": [0.1, 0.6, 0.6, 0.2, 1]
    }

    inputs = pd.DataFrame.from_dict(inputs_dict)
    outputs = [101, 105, 120, 130, 120]

    model = LogisticModel(3)
    model.test(inputs, outputs, "last_year", ["w0", 'w1', 'w2'])
    model.fit(inputs, outputs, "last_year", ["w0", 'w1', 'w2'])
    model.test(inputs, outputs, "last_year", ["w0", 'w1', 'w2'])
