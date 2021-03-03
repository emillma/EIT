import pandas as pd
from sklearn.model_selection import train_test_split
import random
import numpy as np
import time
df = pd.read_csv("Areal2.csv", delimiter=";")

gg = df.Kommune.str.split().str[0]

gg2 = df.Kommune.str.split().str[1:].str.get(0)
df['Kommunenr'] = gg
df['Kommunenavn'] = gg2
df.drop('Kommune', inplace=True, axis=1)

columns = df.columns.tolist()
parametere = df.columns.tolist()[1:len(columns)-2]
columns = parametere.copy()

columns.insert(0, 'År')
columns.insert(1, 'Kommunenr')
columns.insert(2, 'Kommunenavn')

df = df[columns]


for parameter in parametere:
    df[parameter] = pd.to_numeric(
        df[parameter], downcast="float")


df[parametere] = df[parametere].div(
    df[parametere].sum(axis=1), axis=0).round(4)


#nan_value = float("NaN")
#df.replace("", nan_value, inplace=True)
#df.dropna(subset=["Boligbebyggelse"], inplace=True)

df.to_csv('geografi-med-alle-år.csv', sep=";")
