import requests
import pandas as pd
import datetime
import re
import numpy as np

df1 = pd.read_csv('final_output0.csv')

#df1.set_index('year', 'kommune')
for i in range(23):
    read_string = "final_output"
    read_string += str(i+1)
    read_string += ".csv"
    df2 = pd.read_csv(read_string)
    if not {'Jan'}.issubset(df2.columns):
        df2['Jan'] = np.nan
    if not {'Mar'}.issubset(df2.columns):
        df2['Mar'] = np.nan
    if not {'May'}.issubset(df2.columns):
        df2['May'] = np.nan
    if not {'Jul'}.issubset(df2.columns):
        df2['Jul'] = np.nan
    if not {'Aug'}.issubset(df2.columns):
        df2['Aug'] = np.nan
    if not {'Oct'}.issubset(df2.columns):
        df2['Oct'] = np.nan
    if not {'Sep'}.issubset(df2.columns):
        df2['Sep'] = np.nan
    df1 = pd.concat([df1, df2], ignore_index=True, names=['kommune', 'year'], verify_integrity=True)
    #df1 = df1.combine_first(df2)
    #df1 = pd.merge(df1, df2, on=['kommune', 'year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
print(df1.head())
df1 = df1[['kommune', 'year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]
df1 = df1.sort_values(by=['kommune', 'year'])
df1= df1.drop_duplicates(subset=['kommune','year'])
df1.reset_index(drop=True, inplace=True)
#print(df1.head())
#print(df2.head())
#print(df3.head())


print(df1.head())
#df1.columns = pd.to_datetime(df1.columns, format='%Y_%b')
#df1 = df1[sorted(df1.columns)]
#df1.columns = df1.columns.strftime('%Y_%b')
#df2 = df1.fillna(df1.groupby(['2000_Jan']).mean())
df1.to_csv('merged_weather.csv')