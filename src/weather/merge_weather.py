import requests
import pandas as pd
import openpyxl
import datetime
import re

df1 = pd.read_excel('final_output.xlsx', engine='openpyxl')
df2 = pd.read_excel('final_output2.xlsx', engine='openpyxl')
df3 = pd.read_excel('final_output3.xlsx', engine='openpyxl')
print(df1.head())
print(df2.head())
print(df3.head())

df1.update(df2)
df1.update(df3)
df1.columns = pd.to_datetime(df1.columns, format='%Y_%b')
df1 = df1[sorted(df1.columns)]
df1.columns = df1.columns.strftime('%Y_%b')
df1.to_excel('test_merge.xlsx')
print(df1.head())
