import requests
import pandas as pd
from multiprocessing.pool import ThreadPool
from itertools import product as iterprod
import os

url_root = "https://hjorteviltregisteret.no/Statistikk"

animals = [
    'Elg',
    'Hjort']


data_set = [
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
    pool.map(req, iterprod(animals, data_set))


data_tables = []
for animal, data_set in iterprod(animals, data_set):
    filename = f'data/{animal}_{data_set}.xls'
    data_tables.append(pd.read_excel(filename))