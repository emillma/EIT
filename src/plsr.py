from os import supports_dir_fd
from sys import int_info
from pandas.core.frame import DataFrame
from sklearn.cross_decomposition import PLSRegression
from hjortevilt import get_hjortevillt_data
from preprocess_data import pre_process
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from adjustText import adjust_text
import re
# <--- This is important for 3d plotting
from mpl_toolkits.mplot3d import Axes3D

df, _ = get_hjortevillt_data()
df = pre_process(df)
df.drop(columns=df.columns[df.columns.str.contains('jaktfelt')], inplace=True)
# df.drop(columns=df.columns[~df.columns.str.contains('sett')], inplace=True)

index_frame = df.index.to_frame()
index_frame['neste jaktår'] = index_frame['jaktår'].astype(np.int32) + 1


nextyear = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'neste jaktår']])
index_frame = index_frame.loc[nextyear.isin(df.index)]

X_index = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'jaktår']])
Y_index = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'neste jaktår']])

diff = df.groupby('kommunenr').diff(1)

X = df.loc[X_index].values
Y = df.loc[Y_index, df.columns.str.contains(
    'sett')]['elg sett sum sette elg pr dag'].values[:, None]
plsr = PLSRegression(n_components=4, scale=True)
plsr.fit(X, Y)

# plt.plot(plsr.coef_[:, :])
# plt.plot(plsr.coef_[:, :])

x_scores = plsr.x_scores_
y_scores = plsr.y_scores_
x_load = plsr.x_loadings_
y_load = plsr.y_loadings_

colors = X_index.get_level_values(0).values
val, indices = np.unique(colors, return_inverse=True)
# np.random.shuffle
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter(x_scores[:, 0], x_scores[:, 1], x_scores[:, 2], c=indices,
#            s=30, cmap='jet')
loadings = plsr.x_loadings_
L1 = loadings.T[0]
L2 = loadings.T[1]


fig, ax = plt.subplots(1, 1)
fig.set_size_inches(12, 8)
plt.tight_layout()
labels = [re.sub('elg ', '', label) for label in df.columns]
colors = [0 if 'sett' in label else 1 for label in labels]

for remove in ['sett ', 'felt ', 'pr dag']:
    labels = [re.sub(remove, '', label) for label in labels]
# labels = [re.sub('felt ', '', label) for label in labels]

scatter = ax.scatter(L1, L2, c=colors)
ax.legend(scatter.legend_elements()[0], ['Sett per jaktdøgn', 'Felt totalt'],
          loc="lower left", title="")
ax.scatter(*plsr.y_loadings_.ravel()[:2])


ax.xaxis.zoom(-2)
texts = [plt.text(L1[i], L2[i], labels[i], ha='left', va='center')
         for i in range(len(df.columns))]
adjust_text(texts, arrowprops=dict(arrowstyle='-', color='black'))

# for i, txt in enumerate(df.columns):
#     ax.annotate(txt, (L1[i], L2[i]))
# plt.show()
# plsr.transform
