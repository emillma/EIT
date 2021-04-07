import requests
import pandas as pd
import openpyxl
import datetime
import re

# Insert your own client ID here
client_id = '0cc29786-04f6-4dac-b6ad-3ac0565ee799'

# Define endpoint and parameters
endpoint = 'https://frost.met.no/sources/v0.jsonld?types=SensorSystem'
parameters = {
    #'validtime': '2020-01-01/2020-01-02',
    'country': 'NO',
    #'name': 'O*'
}

# Issue an HTTP GET request
r = requests.get(endpoint, parameters, auth=(client_id,''))
# Extract JSON data
json = r.json()

# Check if the request worked, print out any errors
if r.status_code == 200:
    data = json['data']
    print('Data retrieved from frost.met.no!')
else:
    print('Error! Returned status code %s' % r.status_code)
    print('Message: %s' % json['error']['message'])
    print('Reason: %s' % json['error']['reason'])

df = pd.DataFrame()

station_list = []
municipality_list = []
municipality_dict = {}
municipality_dict2 = {}
måned_dict = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
for i in range(len(data)):
    #if (data[i]['validFrom'] < min_validFrom):
    if('municipalityId' not in data[i]):
        print('no id available!')
    else: 
        station_list.append(data[i]['id'])
        municipality_list.append(data[i]['municipalityId'])
        string_help = data[i]['id']
        string_help += ':0'
        if(data[i]['municipality'] not in municipality_dict): 
            municipality_dict[string_help] = data[i]['municipality']
            municipality_dict2[data[i]['id']] = data[i]['municipalityId']
        new_row = data[i]
        df = df.append(new_row, ignore_index=True)
print(len(station_list))
print(municipality_dict)


endpoint2 = 'https://frost.met.no/observations/availableTimeSeries/v0.jsonld?referencetime=2000-01-01/2021-01-01&elements=mean(air_temperature%20P1M)'
df2 = pd.DataFrame()

# Issue an HTTP GET request
r2 = requests.get(endpoint2, auth=(client_id,''))
# Extract JSON data
json2 = r2.json()

# Check if the request worked, print out any errors
if r2.status_code == 200:
    data2 = json2['data']
    print('Data2 retrieved from frost.met.no!')
else:
    print('Error! Returned status code %s' % r2.status_code)
    print('Message: %s' % json['error']['message'])
    print('Reason: %s' % json['error']['reason'])

final_list = []
for i in range(len(station_list)):
    for j in range(len(data2)):
        if station_list[i] in data2[j]['sourceId']:
            if station_list[i] not in final_list:
                final_list.append(station_list[i])
print(len(final_list))

output_number = 0
while(len(final_list) > 0):
    supp_stations = []
    municipality_help = []
    for i in range(len(final_list)):
        for j in range(len(data)):
            if('municipalityId' not in data[j]):
                err = 'no municipality id!'
                #print('err')
            else:
                if(data[j]['municipalityId'] not in municipality_help):
                    if(data[j]['id']==final_list[i]):
                        supp_stations.append(final_list[i])
                        municipality_help.append(data[j]['municipalityId'])
    #for å hente enda mer suplerende data til df3
    df_supp = pd.DataFrame()
    for i in range(len(supp_stations)):
        target_station = supp_stations[i]
        final_list.remove(supp_stations[i])
        print('target station: ',target_station)
        endpoint0 = 'https://frost.met.no/observations/v0.jsonld?referencetime=2000-01-01/2021-01-01&elements=mean(air_temperature%20P1M)'
        parameters0 = {
            'sources': target_station,
            'timeoffsets': 'PT0H'
        }
        # Issue an HTTP GET request
        r0 = requests.get(endpoint0, parameters0, auth=(client_id,''))
        # Extract JSON data
        json0 = r0.json()

        # Check if the request worked, print out any errors
        if r0.status_code == 200:
            data0 = json0['data']
        else:
            print('Error! Returned status code %s' % r0.status_code)
            print('Message: %s' % json0['error']['message'])
            print('Reason: %s' % json0['error']['reason'])

        for j in range(len(data0)):
            row = pd.DataFrame(data0[j])
            date_time_str1 = data0[j]['referenceTime']
            date_time_obj1 = datetime.datetime.strptime(date_time_str1, '%Y-%m-%dT%H:%M:%S.%fZ')
            time_string = ''
            time_string += str(date_time_obj1.year)
            time_string += '_'
            time_string += måned_dict[date_time_obj1.month]
            row['year'] = date_time_obj1.year
            row['kommune'] = municipality_dict2[supp_stations[i]]
            row['month'] = måned_dict[date_time_obj1.month]
            row['value'] = data0[j]['observations'][0]['value']
            df_supp = df_supp.append(row, ignore_index=True)
            
        print('progress: ' , i+1, '/', len(supp_stations))

    del df_supp['observations']
    del df_supp['sourceId']
    del df_supp['referenceTime']
    df_supp.set_index('year', 'kommune', append=True)
    df_supp = df_supp.pivot(index=['kommune', 'year'], columns='month', values='value') 
    output_string = "final_output"
    output_string += str(output_number)
    output_string += ".csv"
    df_supp.to_csv(output_string)
    output_number += 1