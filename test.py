import requests
import pandas as pd
import itertools
url_root = "http://hjorteviltregisteret.no"

dyr = ['Elg',
       'Hjort']

sett_dyr_root = 'SettDyr'
sett_dyr = [
    'Bestandsutvikling',
    'SetteDyr',
    'FelteDyr',
    'FeltPrJegerdag',
    'SettPrJegerdag',
    'SettPrJegertime',
    'SettKuPrOkse',
    'SettKalvPrKu',
    'SettSpissbukkPrBukk'
]

jaktmateriale_root = 'Jaktmateriale'
jaktmateriale = [
    'SlaktevekterGjennomsnitt',
    'SlaktevekterKalv',
    'SlaktevekterDyrHalvannetAar',
    'SlaktevekterPrIndivid',
    'FinnInnsendteDyr',
    'Aldersfordeling',
    'Gjennomsnittsalder'
]

jaktstatistikk_root = 'Jaktstatistikk'
jaktstatistikk = [
    'TildelteDyr',
    'FelteDyrStatistikk',
    'TildelteOgFelteDyr',
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

session = requests.Session()
for i in dyr:
    for j in sett_dyr:
        url = '/'.join([url_root, i, sett_dyr_root, j])
        resp = session.post(url, headers=None, data=form)
        print(url)
        print(resp)

# output = open('test.xls', 'wb')
# output.write(resp.content)
# output.close()

# xls = pd.ExcelFile(resp.content)
# print(xls.parse().columns)
