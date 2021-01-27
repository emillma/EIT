import requests
url = "http://gammel.hjorteviltregisteret.no/Elg/SettDyr/SettPrJegertime"

form = {
    'Fylke':
    'Kommune':
    'Vald':
    'Jaktfelt':
    'FromYear': 1985
    'ToYear': 2020
    'VisningsType': 0
    'ExcelKnapp': 'Excel'
}

session = requests.Session()

resp = session.post(url, headers=None, data=form)

output = open('test.xls', 'wb')
output.write(resp.content)
output.close()
