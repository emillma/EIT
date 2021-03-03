import pandas as pd
from sklearn.model_selection import train_test_split
import random
import numpy as np

df = pd.read_csv('politikk-ny.csv', delimiter=';')
gg = df.Kommune.str.split().str[0]
gg = gg.str.split('-').str[1:].str.get(0)
gg2 = df.Kommune.str.split().str[1:].str.get(0)
df['Kommunenr'] = gg
df['Kommunenavn'] = gg2
df.drop('Kommune', inplace=True, axis=1)
# bytte plass på kolonnene
columns = df.columns.tolist()
partiliste = df.columns.tolist()[1:len(columns)-2]
columns = partiliste.copy()
columns.insert(0, 'År')
columns.insert(1, 'Kommunenr')
columns.insert(2, 'Kommunenavn')

df = df[columns]
partiliste = df.columns.tolist()[3:]
df['stemmer totalt'] = df[partiliste].sum(axis=1)


for parti in partiliste:
    df[''.join([parti, '-prosent'])] = round(df[parti]/df['stemmer totalt'], 3)
df.fillna(0, inplace=True)
df.to_csv('politikk-ferdig.csv', sep=";")
