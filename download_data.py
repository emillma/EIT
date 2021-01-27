import requests
import pandas as pd
from multiprocessing.pool import ThreadPool
from itertools import product as iterprod
import os
import numpy as np
import re

url_root = "https://hjorteviltregisteret.no/Statistikk"

animals = [
    'Elg',
    'Hjort']


data_sets = [
    'Sett',
    'Felt',
    'Slaktevekt',
]

form = {
    'fraår': 1985,
    'granularitet': 1,
    'gruppering': 2,
    'tilår': 2020,
}


def req(input):
    animal, data_set = input
    filename = f'data/{animal}_{data_set}.xls'
    if os.path.isfile(filename):
        return

    url = '/'.join((url_root, animal, 'Jaktmateriale', data_set)) + 'Excel'
    rep = requests.get(url, params=form)

    with open(filename, 'wb') as file:
        file.write(rep.content)


if not os.path.exists('data'):
    os.makedirs('data')

with ThreadPool(128) as pool:
    pool.map(req, iterprod(animals, data_sets))


frames = []
for animal, data_set in list(iterprod(animals, data_sets)):
    filename = f'data/{animal}_{data_set}.xls'
    frame = pd.read_excel(filename)
    frame = frame.add_prefix(f'{animal} {data_set} ')

    columns = list(frame.columns)

    double_names = any(['unnamed' in i.lower() for i in columns])
    if double_names:
        columns = [columns[i] if 'unnamed' not in columns[i].lower()
                   else columns[i-1]
                   for i in range(len(columns))]

        columns = [i + ' ' + str(j) if not pd.isnull(j)
                   else i
                   for i, j in zip(columns, frame.values[0])]

        frame.columns = columns
        frame = frame.iloc[1:]
    frames.append(frame)

dataframe = pd.concat([frames[0].iloc[:, :3]]+[i.iloc[:, 3:] for i in frames],
                      axis=1)
dataframe.rename(columns={dataframe.columns[0]: "jaktår",
                          dataframe.columns[0]: "kommunenr",
                          dataframe.columns[0]: "kommune"}, inplace=True)
columns = list(dataframe.columns)
for i, text in enumerate(columns):
    text = text.lower()
    text = re.sub(' ½', '.5', text)
    text = re.sub(r'([0-9]*\.[0-9]*) år og eldre', r'>=\1 år', text)
    text = re.sub('gjennomsnittsvekt', 'snittvekt', text)
    text = re.sub('kalv', ' 0.5 år', text)
    columns[i] = text


dataframe.columns = columns

dataframe.iloc[:, :2] = dataframe.iloc[:, :2].astype(np.int32)
'Våler', 3018
'Herøy', 1515
