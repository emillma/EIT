import requests
import pandas as pd
import itertools
from multiprocessing.pool import ThreadPool

url_root = "http://gammel.hjorteviltregisteret.no"
# url_root = "http://hjorteviltregisteret.no/Statistikk"

dyr_liste = [
    'Elg',
    'Hjort']


data_types = [
    'SettDyr/SetteDyr',
    'SettDyr/FelteDyr',
    'Jaktmateriale/SlaktevekterGjennomsnitt',
    'Jaktstatistikk/TildelteDyr'
]


form = {
    'Fylke': None,
    'Kommune': None,
    'Vald': None,
    'Jaktfelt': None,
    'FromYear': 1985,
    'ToYear': 2020,
    'VisningsType': 0,
    'ExcelKnapp': 'Excel',
}

request_list = []
session = requests.Session()
for dyr in dyr_liste:
    for data_type in data_types:
        url = '/'.join([url_root, dyr, data_type])
        request_list.append((url, form))
        resp = session.post(url, headers=None, data=form)
        print(url)
        print(resp)


# def get_data():
#     '''Locates all sonars in an IP range and returns a list of namedtuples'''

#     def req(ip):
#         return

#     with ThreadPool(128) as pool:
#         res = filter(lambda x: x != None, pool.map(req, ))
#     return list(res)


# output = open('test.xls', 'wb')
# output.write(resp.content)
# output.close()

# xls = pd.ExcelFile(resp.content)
# print(xls.parse().columns)
