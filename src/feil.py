
df = get_hjortevilt_dataframe()

a = df[['elg sett antall jegerdager', 'elg felt antall jegerdager',
        'elg sett sum sette elg', 'elg felt sum felte']]

b = a.loc[a.iloc[:, 0] != a.iloc[:, 1]]
