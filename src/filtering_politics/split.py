import pandas as pd
from sklearn.model_selection import train_test_split
import random
import numpy as np


def split_random_sklearn(df):
    """
    Input: dataframe
    output: train and test set with sizes respectively
    80% and 20% of the original dataframe. The data 
    is randomly split and shuffled with sklearn
    """
    train_df, test_df = train_test_split(df, test_size=0.2)
    return train_df, test_df


def split_random(df):
    """
    Input: dataframe
    output: train and test set with sizes respectively
    80% and 20% of the original dataframe. The data 
    is randomly split and shuffled.
    """
    df.sample(frac=1)
    train = df.sample(frac=0.8)
    test = df.drop(train.index)

    return test, train


def split_municipality(df):
    """
    Input: dataframe
    output: train and test set with sizes respectively
    80% and 20% of the original dataframe. The function
    splits based upon municipalities, i.e. no overlap between
    the two sets.
    """

    kommuner = df.Kommunenr.unique().tolist()

    random.shuffle(kommuner)

    cutoff = round(len(kommuner)*0.8)
    train_kommuner = kommuner[:cutoff]
    test_kommuner = kommuner[cutoff:]

    test_df = df.loc[df['Kommunenr'].isin(test_kommuner)]
    train_df = df.loc[df['Kommunenr'].isin(train_kommuner)]
    return train_df, test_df


def split_year(df):
    """
    Input: dataframe
    output: train and test set with sizes respectively
    80% and 20% of the original dataframe. The function
    splits based upon years, i.e. no overlap between
    the two sets.
    """
    years = df.År.unique()
    cutoff = round(len(years)*0.8)

    train_years = years[:cutoff]
    test_years = years[cutoff:]

    test_df = df.loc[df['År'].isin(test_years)]
    train_df = df.loc[df['År'].isin(train_years)]
    return train_df, test_df


df = pd.read_csv('politikk-ferdig.csv', sep=';')

split_random_sklearn(df)
