from sklearn.cross_decomposition import PLSRegression
from hjortevilt import get_hjortevillt_data


df, _ = get_hjortevillt_data()

diff = df.groupby('kommunenr').diff(-1)

filt = df.notna().all(axis=1) & diff.notna().all(axis=1)


X = df.loc[filt].values
Y = diff.loc[filt].values

pls2 = PLSRegression()
pls2.fit(X, Y)
