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

RAW_FILENAME = os.path.join(DATA_FOLDER_PATH,
                            'hjorteviltregisteret_raw.csv')
HJORTEDATA_FILENAME = os.path.join(DATA_FOLDER_PATH,
                                   'hjortedata.csv')


def download_from_hjortevilltregisteret(input):
    """Used to download the data and translate it into a dataframe"""

    url_root = "https://hjorteviltregisteret.no/Statistikk"
    animal, data_set = input
    form = {
        'fraår': 1985,
        'granularitet': 1,
        'gruppering': 2,
        'tilår': 2020,
    }

    url = '/'.join((url_root, animal, 'Jaktmateriale', data_set)) + 'Excel'
    rep = requests.get(url, params=form)

    df = pd.read_excel(rep.content)
    df = df.add_prefix(f'{animal} {data_set} ')

    # In some of the tables, the first and second row are labels, this solve it
    if any(['unnamed' in i.lower() for i in df.columns]):  # second row is also name
        columns = list(df.columns)
        columns = [columns[i] if 'unnamed' not in columns[i].lower()
                   else columns[i-1]
                   for i in range(len(columns))]

        columns = [i + ' ' + str(j) if not pd.isnull(j)
                   else i
                   for i, j in zip(columns, df.values[0])]

        df.columns = columns
        df = df.iloc[1:]
    return df


def get_raw_hjortevillt_df():
    """Get the data from hjorteviltregisteret
    """
    animals = [
        'Elg',
        'Hjort']

    data_sets = [
        'Sett',
        'Felt',
        'Slaktevekt',
    ]
    # download the data and turn each table into an individual frame
    with ThreadPool(6) as pool:
        frames = pool.map(download_from_hjortevilltregisteret,
                          iterprod(animals, data_sets))
    # join the frames into one single large frame
    df = pd.concat([frames[0].iloc[:, :3]]
                   + [i.iloc[:, 3:] for i in frames],
                   axis=1)
    df.to_csv(RAW_FILENAME, index=False)
    return df


def preprocess(df):
    df.rename(columns={df.columns[0]: "jaktår",
                       df.columns[1]: "kommunenr",
                       df.columns[2]: "kommune"}, inplace=True)

    # this only removes the last row, which is garbage
    df.dropna(subset=df.columns[:3], inplace=True)

    columns = list(df.columns)
    for i, text in enumerate(columns):
        text = text.lower()
        text = re.sub(' ½', '.5', text)
        text = re.sub(r'([0-9]*\.[0-9]*) år og eldre', r'>=\1 år', text)
        text = re.sub('gjennomsnittsvekt', 'snittvekt', text)
        # text = re.sub(' ?kalv(er)?', ' 0.5 år', text)
        columns[i] = text

    df.columns = columns
    df.iloc[:, :2] = df.iloc[:, :2].astype(np.int32)

    # multiple municipals sharing name
    df.loc[(df['kommune'] == 'Våler') & (df['kommunenr'] == 3018),
           'kommune'] = 'Våler (Østfold)'
    df.loc[(df['kommune'] == 'Våler') & (df['kommunenr'] == 3419),
           'kommune'] = 'Våler (Hedmark)'
    df.loc[(df['kommune'] == 'Herøy') & (df['kommunenr'] == 1818),
           'kommune'] = 'Herøy (Nordland)'
    df.loc[(df['kommune'] == 'Herøy') & (df['kommunenr'] == 1515),
           'kommune'] = 'Herøy (Møre og Romsdal)'

    df.set_index(['kommunenr', 'jaktår'], inplace=True)
    df.sort_index(0, ['kommunenr', 'jaktår'])

    return df


def clean_incomplete_data(df):
    feil_rapportering = df.loc[
        df.loc[:, 'elg sett antall jegerdager']
        != df.loc[:, 'elg felt antall jegerdager']]
    

def get_hjortevillt_data(reprocess=False, redownload=False, animal='elg'):

    if os.path.isfile(HJORTEDATA_FILENAME) and not reprocess:
        df = pd.read_csv(HJORTEDATA_FILENAME)
        return df

    if os.path.isfile(RAW_FILENAME) and not redownload:
        df_raw = pd.read_csv(RAW_FILENAME)
    else:
        df_raw = get_raw_hjortevillt_df()
        df_raw.to_csv(RAW_FILENAME, index=False)

    df = preprocess(df_raw)

    kommune_nr_name_relations = dict(
        df.reset_index().groupby(['kommunenr', 'kommune']).
        size().reset_index().iloc[:, :-1].values)

    extra_data = {'kommune_names': kommune_nr_name_relations}
    df.drop('kommune', axis=1, inplace=True)

    if animal in ['elg', 'hjort']:
        drop_animal = 'hjort' if animal == 'elg' else 'elg'
        df.drop(df.columns[df.columns.str.contains(drop_animal)],
                axis=1, inplace=True)

    return df, extra_data
