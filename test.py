import requests
import pandas as pd
import itertools
url_root = "http://gammel.hjorteviltregisteret.no"

dyr_liste = [
    'Elg',
    'Hjort']

sett_dyr = {
    'root': 'SettDyr',
    'datatypes': [
        'Bestandsutvikling',
        'SetteDyr',
        'FelteDyr',
        'FeltPrJegerdag',
        'SettPrJegerdag',
        'SettPrJegertime',
        'SettKuPrOkse',
        'SettKalvPrKu',
        'SettSpissbukkPrBukk'
    ]}

jaktmateriale = {
    'root': 'Jaktmateriale',
    'datatypes': [
        'SlaktevekterGjennomsnitt',
        'SlaktevekterKalv',
        'SlaktevekterDyrHalvannetAar',
        'SlaktevekterPrIndivid',
        'FinnInnsendteDyr',
        'Aldersfordeling',
        'Gjennomsnittsalder'
    ]}

jaktstatistikk = {
    'root': 'Jaktstatistikk',
    'datatypes': [
        'TildelteDyr',
        'FelteDyrStatistikk',
        'TildelteOgFelteDyr',
    ]}


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

session = requests.Session()
for dyr in dyr_liste:
    for data_class in [sett_dyr, jaktmateriale, jaktstatistikk]:
        for data_types in data_class['datatypes']:
            for data_type in data_types:

                url = '/'.join([url_root, data_class['root'],
                                data_type])
                resp = session.post(url, headers=None, data=form)
                print(url)
                print(resp)

# output = open('test.xls', 'wb')
# output.write(resp.content)
# output.close()

# xls = pd.ExcelFile(resp.content)
# print(xls.parse().columns)
