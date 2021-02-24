from pandas.core.frame import DataFrame
from sklearn.cross_decomposition import PLSRegression
from hjortevilt import get_hjortevillt_data
import pandas as pd

df, _ = get_hjortevillt_data()

index_frame = df.index.to_frame()
index_frame['neste jaktår'] = index_frame['jaktår'] + 1


Y_index = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'neste jaktår']])
# index_frame[df.index.names] = df.reset_index()[df.index.names]
diff = df.groupby('kommunenr').diff(-1)

# filt = df.notna().all(axis=1) & diff.notna().all(axis=1)


# X = df.loc[filt].values
# Y = diff.loc[filt].values

# pls2 = PLSRegression()
# pls2.fit(X, Y)
