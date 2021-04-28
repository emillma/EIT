
import argparse
import os

import yaml
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt

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


def plot_data_and_dev(title, labels, x_pos, means, std):
    fix, ax = plt.subplots()
    ax.bar(x_pos, means, yerr=std, align="center",
           alpha=0.5, ecolor="black", capsize=10)
    ax.set_ylabel("Error")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_title(title)
    ax.yaxis.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    config = setup_args()
    data_config, model_config = config["data"], config["model"]

    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, data_config["path"])
    data = pd.read_csv(path, delimiter=",")

    l1_errors = []
    l1_pred_errors = []
    percentage_l1_pred_errors = []
    l2_errors = []
    up_to_l2_pred_errors = []
    percentage_l2_pred_errors = []
    l3_errors = []
    total_pred_error = []
    percentage_total_pred_error = []
    nn_training_history = []

    for i in range(100):

        train, test = train_test_split(data, test_size=0.2)

        data_keys = [i for i in train.columns[2:]
                     if i != data_config["this_year_key"]]

        model = MGNN(config["model"])

        training_history = model.train(model_config, train[data_keys], train[data_config["this_year_key"]],
                                       data_config["last_year_key"], data_config["weather_keys"])

        nn_training_history.append(training_history)

        test_results = model.test(test[data_keys], test[data_config["this_year_key"]],
                                  data_config["last_year_key"], data_config["weather_keys"])

        l1_pred_errors.append(test_results[3])
        percentage_l1_pred_errors.append(
            100 * abs(test_results[3]) / test[data_config["last_year_key"]])
        up_to_l2_pred_errors.append(test_results[4])
        percentage_l2_pred_errors.append(
            100 * abs(test_results[4]) / test[data_config["last_year_key"]])
        total_pred_error.append(test_results[0])
        percentage_total_pred_error.append(
            100 * abs(test_results[0]) / test[data_config["last_year_key"]])

        print(
            f'Test result: Overall error: {test_results[0]}, l3 error: {test_results[1]}, l2 error: {test_results[2]}, l1 error: {test_results[3]}')
        print(f'Up to l2 error: {test_results[4]}')

        l1_errors.append(test_results[3])
        l2_errors.append(test_results[2])
        l3_errors.append(test_results[1])

    l1_pred_mean = np.mean(l1_pred_errors)
    l2_pred_mean = np.mean(up_to_l2_pred_errors)
    model_pred_mean = np.mean(total_pred_error)

    l1_pred_std = np.std(l1_pred_errors)
    l2_pred_std = np.std(up_to_l2_pred_errors)
    model_pred_std = np.std(total_pred_error)

    l1_percentage_mean = np.mean(percentage_l1_pred_errors)
    l2_percentage_mean = np.mean(percentage_l2_pred_errors)
    percentage_total_mean = np.mean(percentage_total_pred_error)

    relative_l1_std = np.std(percentage_l1_pred_errors)
    relative_l2_std = np.std(percentage_l2_pred_errors)
    relative_model_std = np.std(percentage_total_pred_error)

    l1_mean = np.mean(l1_errors)
    l2_mean = np.mean(l2_errors)
    l3_mean = np.mean(l3_errors)

    l1_std = np.std(l1_errors)
    l2_std = np.std(l2_errors)
    l3_std = np.std(l3_errors)

    labels = ["Layer 1", "Up to layer 2", "Full model"]
    x_pos = np.arange(len(labels))
    means = [l1_pred_mean, l2_pred_mean, model_pred_mean]
    std = [l1_pred_std, l2_pred_std, model_pred_std]

    relative_means = [l1_percentage_mean,
                      l2_percentage_mean, percentage_total_mean]
    relative_std = [relative_l1_std, relative_l2_std, relative_model_std]

    print(
        f"l1_mean: {l1_pred_mean}, l2_mean: {l2_pred_mean}, model_mean: {model_pred_mean}")
    print(
        f"l1_std: {l1_pred_std}, l2_std: {l2_pred_std}, model_std: {model_pred_std}")

    plot_data_and_dev("Prediction error: MSE", labels, x_pos, means, std)

    print(
        f"Percentage: l1_mean: {l1_percentage_mean}, l2_mean: {l2_percentage_mean}, model_mean: {percentage_total_mean}")
    print(
        f"l1_std: {relative_l1_std}, l2_std: {relative_l2_std}, model_std: {relative_model_std}")

    plot_data_and_dev("Perdiction error: Mean percentage error",
                      labels, x_pos, relative_means, relative_std)

    labels = ["Layer 1", "Layer 2", "Layer 3"]
    x_pos = np.arange(len(labels))
    means = [l1_mean, l2_mean, l3_mean]
    std = [l1_std, l2_std, l3_std]

    plot_data_and_dev("Layer error: MSE", labels, x_pos, means, std)
