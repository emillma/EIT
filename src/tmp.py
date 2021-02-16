from hjortevilt import get_hjortevillt_data


df, _ = get_hjortevillt_data()

feil_rapportering = df.loc[
    df.loc[:, 'elg sett antall jegerdager']
    != df.loc[:, 'elg felt antall jegerdager']].index
