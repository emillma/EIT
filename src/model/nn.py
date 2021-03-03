
from __future__ import print_function
import os
import math
from typing import Dict

import scipy.io as spio
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, TerminateOnNaN
from tensorflow.keras import backend as K
from tensorflow.keras.losses import mean_squared_error


def elk_model(inputs):
    # TODO: Replace this with a sensible model for next year elk observation
    return inputs


def phy_loss_mean(params):
    # useful for cross-checking training
    udendiff, lam = params

    def loss(y_true, y_pred):
        return K.mean(K.relu(udendiff))
    return loss


def combined_loss(params):
    # function to calculate the combined loss = sum of mse and model based loss
    udendiff, lam = params

    def loss(y_true, y_pred):
        return mean_squared_error(y_true, y_pred) + lam * K.mean(K.relu(udendiff))
    return loss


def PGNN_train_test(config: Dict):

    # Hyper-parameters of the training process
    num_epochs = config["epochs"]
    batch_size = config["batch_size"]
    val_frac = config["val_frac"]
    test_frac = config["test_frac"]
    traing_frac = 1 - test_frac - val_frac
    dropout_frac = config["dropout"]
    patience_val = config["patience_val"]

    # Initializing results filename
    exp_name = config["optimizer"] + '_drop' + str(config["dropout"]) + '_nL' + str(
        len(config["layers"]))
    results_dir = './results/'
    model_name = results_dir + exp_name + '_model.h5'  # storing the trained model
    results_name = results_dir + exp_name + \
        '_results.mat'  # storing the results of the model

    # Load features (Xc) and target values (Y)
    # This will need to change when we know the final format of our data
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, config["data_path"])
    data = pd.read_csv(filename)
    X = data['Xc_doy']
    Y = data['Y']

    training_size = math.floor(traing_frac * len(X))

    trainX, trainY = X[:training_size, :], Y[:training_size]
    testX, testY = X[training_size:, :], Y[training_size:]

    # Creating the model
    layers = config["layers"]
    model = Sequential()
    for i in range(len(layers)):
        if i == 0:
            model.add(Input(trainX[1].shape))
        else:
            model.add(Dense(layers[i]["nodes"],
                            activation=layers[i]["activation"]))
        model.add(Dropout(dropout_frac))
    model.add(Dense(1, activation='linear'))

    # physics-based regularization
    # TODO: Replace this with a sensible model based regularization for
    # our elk problem
    # uin1 = K.constant(value=uX1)  # input at depth i
    # uin2 = K.constant(value=uX2)  # input at depth i + 1
    # uout1 = model(uin1)  # model output at depth i
    # uout2 = model(uin2)  # model output at depth i + 1
    # difference in density estimates at every pair of depth values
    #udendiff = (elk_model(uout1) - elk_model(uout2))

    totloss = combined_loss([udendiff, lam])
    phyloss = phy_loss_mean([udendiff, lam])

    model.compile(loss=totloss,
                  optimizer=config["optimizer"],
                  metrics=[phyloss, mean_squared_error])

    early_stopping = EarlyStopping(
        monitor='val_loss_1', patience=patience_val, verbose=1)

    print(f'Running... {config["optimizer"]}')
    history = model.fit(trainX, trainY,
                        batch_size=batch_size,
                        epochs=num_epochs,
                        verbose=1,
                        validation_split=val_frac, callbacks=[early_stopping, TerminateOnNaN()])

    test_score = model.evaluate(testX, testY, verbose=0)
    model.save(model_name)
    spio.savemat(results_name, {'train_loss_1': history.history['loss_1'], 'val_loss_1': history.history['val_loss_1'],
                                'train_rmse': history.history['root_mean_squared_error'], 'val_rmse': history.history['val_root_mean_squared_error'], 'test_rmse': test_score[2]})
