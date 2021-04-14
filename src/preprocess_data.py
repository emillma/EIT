from pandas.core.frame import DataFrame
import pandas as pd
from hjortevilt import get_hjortevillt_data


def pre_process(df):
    df = df.copy()
    df = df[df.columns[~df.columns.str.contains('slaktevekt')]]

    df.dropna(axis=0, inplace=True)
    rap_feil = (df.loc[:, 'elg sett antall jegerdager']
                != df.loc[:, 'elg felt antall jegerdager'])
    rap_feil_index = rap_feil[rap_feil].index
    df.drop(index=rap_feil_index, inplace=True)

    JEGERDAGER_MIN = 500
    df = df.loc[df['elg sett antall jegerdager'] >= JEGERDAGER_MIN]

    jegerdager = df['elg sett antall jegerdager']
    df = df[df.columns[~df.columns.str.contains('jegerdager')]]

    names = df.columns[df.columns.str.contains('sett')]
    df[names] = df[names].div(jegerdager, axis=0)

    df.rename(columns=dict(zip(
        names,
        [name + ' pr dag' for name in names])), inplace=True)
    return df


if __name__ == '__main__':
    df, _ = get_hjortevillt_data()
    df = pre_process(df)
