from hjortevilt import get_hjortevillt_data
from preprocess_data import pre_process
from geoplotter import plot_kommuner
import pandas as pd
from matplotlib import pyplot as plt


def valid_years():
    """
    Vise antall gyldige datapungter for hver kommune. Altså hvor mange unike
    konsekkutive år det er hvor antall jegerdager er større enn minimumet satt 
    i pre_process
    """
    df, _ = get_hjortevillt_data()
    df_processed = pre_process(df)

    index_frame = df_processed.index.to_frame()
    index_frame['neste jaktår'] = index_frame['jaktår'].astype(np.int32) + 1

    nextyear = pd.MultiIndex.from_frame(
        index_frame[['kommunenr', 'neste jaktår']])
    index_frame = index_frame.loc[nextyear.isin(df_processed.index)]

    X_index = pd.MultiIndex.from_frame(index_frame[['kommunenr', 'jaktår']])

    valid_years = df_processed.loc[X_index].reset_index().groupby('kommunenr')[
        'jaktår'].nunique()

    keys = valid_years.index.values
    items = valid_years.values
    plot_dict = dict(zip(keys, items))
    all_numbers = df.index.get_level_values(0).unique()
    for n in all_numbers:
        if n not in plot_dict:
            plot_dict[n] = 0
    plot_kommuner(plot_dict)
    plt.tight_layout()
