import argparse
import os
import yaml

from nn import PGNN_train_test


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
    PGNN_train_test(config)
