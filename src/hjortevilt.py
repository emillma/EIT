import requests
import pandas as pd
from multiprocessing.pool import ThreadPool
from itertools import product as iterprod
import os
import numpy as np
import re

SAVE_EXCEL = False

dir_path = os.path.dirname(os.path.realpath(__file__))
DATA_FOLDER_PATH = os.path.join(dir_path, '..', 'data')
DATAFRAME_FILENAME = os.path.join(DATA_FOLDER_PATH,
                                  'hjorteviltregisteret.csv')

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


def get_frames(input):
    animal, data_set = input

    url = '/'.join((url_root, animal, 'Jaktmateriale', data_set)) + 'Excel'
    rep = requests.get(url, params=form)

    frame = pd.read_excel(rep.content)
    frame = frame.add_prefix(f'{animal} {data_set} ')

    if any(['unnamed' in i.lower() for i in frame.columns]):  # second row is also name
        columns = list(frame.columns)
        columns = [columns[i] if 'unnamed' not in columns[i].lower()
                   else columns[i-1]
                   for i in range(len(columns))]

        columns = [i + ' ' + str(j) if not pd.isnull(j)
                   else i
                   for i, j in zip(columns, frame.values[0])]

        frame.columns = columns
        frame = frame.iloc[1:]
    return frame


def get_hjortevilt_dataframe(reload=False, redownload=False):

    if os.path.isfile(DATAFRAME_FILENAME) and not redownload:
        dataframe = pd.read_csv(DATAFRAME_FILENAME)
        if not reload:
            return dataframe

    else:
        with ThreadPool(6) as pool:
            frames = pool.map(get_frames, iterprod(animals, data_sets))

        dataframe = pd.concat([frames[0].iloc[:, :3]]
                              + [i.iloc[:, 3:] for i in frames],
                              axis=1)

    dataframe.rename(columns={dataframe.columns[0]: "jaktår",
                              dataframe.columns[1]: "kommunenr",
                              dataframe.columns[2]: "kommune"}, inplace=True)
    dataframe.dropna(subset=dataframe.columns[:3], inplace=True)

    columns = list(dataframe.columns)
    for i, text in enumerate(columns):
        text = text.lower()
        text = re.sub(' ½', '.5', text)
        text = re.sub(r'([0-9]*\.[0-9]*) år og eldre', r'>=\1 år', text)
        text = re.sub('gjennomsnittsvekt', 'snittvekt', text)
        # text = re.sub(' ?kalv(er)?', ' 0.5 år', text)
        columns[i] = text

    dataframe.columns = columns
    dataframe.iloc[:, :2] = dataframe.iloc[:, :2].astype(np.int32)
    dataframe.loc[dataframe.loc[:, 'kommune'] == 'Våler', 'kommunenr'] = 3018
    dataframe.loc[dataframe.loc[:, 'kommune'] == 'Herøy', 'kommunenr'] = 1515

    dataframe.to_csv(DATAFRAME_FILENAME, index=False)
    return dataframe
