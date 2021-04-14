from hjortevilt import get_hjortevillt_data
from preprocess_data import pre_process
import pandas as pd
import numpy as np


hjortedata, _ = get_hjortevillt_data()
hjortedata = pre_process(hjortedata)
hjortedata.drop(
    columns=hjortedata.columns[hjortedata.columns.str.contains('jaktfelt')],
    inplace=True)

værdata = pd.read_csv(
    r'C:\Users\emilm\Documents\NTNU\4.klasse\EIT\data\merged_weather.csv')
værdata.drop(columns='Unnamed: 0', inplace=True)
værdata.rename(columns={'kommune': 'kommunenr',
                        'year': 'jaktår'}, inplace=True)
værdata.set_index(['kommunenr', 'jaktår'], inplace=True)
værdata.sort_index(0, ['kommunenr', 'jaktår'])
værdata = værdata[~værdata.isna().any(axis=1)]

index_frame = hjortedata.index.to_frame()
index_frame['neste jaktår'] = index_frame['jaktår'].astype(np.int32) + 1


nextyear = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'neste jaktår']])
index_frame = index_frame.loc[nextyear.isin(hjortedata.index)]
index_frame = index_frame.loc[index_frame.index.isin(værdata.index)]


X_index = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'jaktår']])
Y_index = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'neste jaktår']])

data = pd.concat([hjortedata.loc[X_index], værdata.loc[X_index]], axis=1)
data.loc[:, 'elg sett sum sette elg pr dag neste aar'] = (
    hjortedata.loc[Y_index, 'elg sett sum sette elg pr dag'].values
)
data.to_csv('test_data.csv')
