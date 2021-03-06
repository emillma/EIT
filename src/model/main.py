import argparse
import os
import yaml
import pandas as pd
from sklearn.model_selection import train_test_split

from nn import MGNN


def setup_args() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="./configs/base.yaml")
    args = parser.parse_args()

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, args.config)

    if not os.path.isfile(filename):
        raise ValueError(f"{args.config} is not a valid file path")

    with open(filename) as file:
        print(f"Loading config from {args.config}")
        config = yaml.full_load(file)

    return config


if __name__ == "__main__":
    config = setup_args()
    data_config, model_config = config["data"], config["model"]

    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, data_config["path"])
    data = pd.read_csv(path, delimiter=",")

    train, test = train_test_split(data, test_size=0.2)

    data_keys = [i for i in train.columns[2:]
                 if i != data_config["this_year_key"]]

    model = MGNN(config["model"])
    if not config["model"]["load"]:
        model.train(model_config, train[data_keys], train[data_config["this_year_key"]],
                    data_config["last_year_key"], data_config["weather_keys"])

    test_results = model.test(test[data_keys], test[data_config["this_year_key"]],
                              data_config["last_year_key"], data_config["weather_keys"])
    print(
        f'Test result: Overall error: {test_results[0]}, l3 error: {test_results[1]}, l2 error: {test_results[2]}, l1 error: {test_results[3]}')
    print(f'Up to l2 error: {test_results[4]}')
    if config["model"]["save"]:
        model.dump_model_to_file(config["model"]["save_dir"])
