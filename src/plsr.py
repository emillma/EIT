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
from matplotlib.lines import Line2D
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
Y = df.loc[Y_index, df.columns.str.contains(
    'sett')].values
# Y = Y - X[:, :8]
# Y = df.loc[Y_index].values - X
plsr = PLSRegression(n_components=6, scale=True)
plsr.fit(X, Y)


x_scores = plsr.x_scores_
y_scores = plsr.y_scores_
x_load = plsr.x_loadings_
y_load = plsr.y_loadings_

colors = X_index.get_level_values(0).values
val, indices = np.unique(colors, return_inverse=True)

loadings = plsr.x_loadings_
dirs = [0, 1]
L1 = loadings.T[dirs[0]]
L2 = loadings.T[dirs[1]]
x_load = plsr.x_loadings_.T[dirs]
y_load = plsr.y_loadings_.T[dirs]

plt.close('all')
fig, ax = plt.subplots(1, 1)
# ax.set_xlim([-1, 1])
# ax.set_ylim([-1, 1])
fig.set_size_inches(12, 8)
plt.tight_layout()

labels = [re.sub('elg ', '', label) for label in df.columns]
colors = [0 if 'sett' in label else 0.5 for label in labels]
colors += [1] * y_load.shape[1]
labels += labels[:8]

for remove in ['sett ', 'felt ', 'pr dag']:
    labels = [re.sub(remove, '', label) for label in labels]
# labels = [re.sub('felt ', '', label) for label in labels]
data = np.hstack([x_load, y_load])

colormap = plt.get_cmap()
scatter = ax.scatter(*data, c=colors, cmap=colormap)
# scatter_ny = ax.scatter(*plsr.y_loadings_.T[:2])
# legend_elem = scatter_ny.legend_elements()[0] + scatter.legend_elements()[0]
legend_elem = scatter.legend_elements()[0]


legend_elements = [Line2D([0], [0], marker='o', color='w', label=name,
                          markerfacecolor=color, markersize=10)
                   for color, name in [
                       [colormap(0), 'sett per jaktdøgn'],
                       [colormap(0.5), 'felt'],
                       [colormap(1.), 'utvikling'],

]]

ax.legend(handles=legend_elements,
          loc="lower left", title="")
other_objects = []
other_objects.append(ax.axvline(x=0))
other_objects.append(ax.axhline(y=0))
other_objects = []

texts = [plt.text(data[0, i], data[1, i], labels[i],
                  ha='center', va='center')
         for i in range(data.shape[1])]

adjust_text(texts, add_objects=other_objects,
            arrowprops=dict(arrowstyle='-', color='black'),
            force_points=(3, 0.3),
            force_text=(0.1, 0.3),
            # force_objects=(0.2, 0.4)
            )
