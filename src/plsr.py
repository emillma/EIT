from pandas.core.frame import DataFrame
from sklearn.cross_decomposition import PLSRegression
from hjortevilt import get_hjortevillt_data
from preprocess_data import pre_process
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
df, _ = get_hjortevillt_data()
df = pre_process(df)
df.drop(columns=df.columns[df.columns.str.contains('jaktfelt')], inplace=True)
df.drop(columns=df.columns[~df.columns.str.contains('sett')], inplace=True)

index_frame = df.index.to_frame()
index_frame['neste jaktår'] = index_frame['jaktår'].astype(np.int32) + 1


nextyear = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'neste jaktår']])
index_frame = index_frame.loc[nextyear.isin(df.index)]

X_index = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'jaktår']])
Y_index = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'neste jaktår']])

diff = df.groupby('kommunenr').diff(1)

X = df.loc[X_index].values
Y = df.loc[Y_index, df.columns.str.contains('sett')].values
plsr = PLSRegression(8, scale=False)
plsr.fit(X, Y)

# plt.plot(plsr.coef_[:, 7])
