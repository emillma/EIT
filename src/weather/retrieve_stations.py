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
            municipality_dict2[data[i]['id']] = data[i]['municipality']
        new_row = data[i]
        df = df.append(new_row, ignore_index=True)
print(len(station_list))
#df.to_excel("output.xlsx") 
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

final_final_list = []
municipality_help_list = []
for i in range(len(final_list)):
    for j in range(len(data)):
        if('municipalityId' not in data[j]):
            err = 'no municipality id!'
            #print('err')
        else:
            if(data[j]['municipalityId'] not in municipality_help_list):
                 if(data[j]['id']==final_list[i]):
                    final_final_list.append(final_list[i])
                    municipality_help_list.append(data[j]['municipalityId'])

df3 = pd.DataFrame()
target_station = ''
# Define endpoint and parameters
for i in range(len(final_final_list)):
    print(municipality_dict2[final_final_list[i]])
test_list = []
any_stations_remaining = True
for i in range(len(final_final_list)):
    target_station = final_final_list[i]
    final_list.remove(final_final_list[i])
    print('target station: ',target_station)
    endpoint3 = 'https://frost.met.no/observations/v0.jsonld?referencetime=2000-01-01/2021-01-01&elements=mean(air_temperature%20P1M)'
    parameters3 = {
        'sources': target_station,
        'timeoffsets': 'PT0H'
    }
    # Issue an HTTP GET request
    r3 = requests.get(endpoint3, parameters3, auth=(client_id,''))
    # Extract JSON data
    json3 = r3.json()

    # Check if the request worked, print out any errors
    if r3.status_code == 200:
        data3 = json3['data']
    else:
        print('Error! Returned status code %s' % r3.status_code)
        print('Message: %s' % json3['error']['message'])
        print('Reason: %s' % json3['error']['reason'])
    
    #if(municipality_dict[data3[0]['sourceId']] not in test_list):
        #print(municipality_dict[data3[0]['sourceId']])
        #test_list.append(municipality_dict[data3[0]['sourceId']])
    #else:
        #print('-----------------------------------------------------')
        #print('duplikat av: ', municipality_dict[data3[j]['sourceId']])
        #print('-----------------------------------------------------')

    for j in range(len(data3)):
        row = pd.DataFrame(data3[j])
        row['kommune'] = municipality_dict2[final_final_list[i]]
        date_time_str1 = data3[j]['referenceTime']
        date_time_obj1 = datetime.datetime.strptime(date_time_str1, '%Y-%m-%dT%H:%M:%S.%fZ')
        time_string = ''
        time_string += str(date_time_obj1.year)
        time_string += '_'
        time_string += måned_dict[date_time_obj1.month]
        row['tid'] = time_string
        row['value'] = data3[j]['observations'][0]['value']
        df3 = df3.append(row, ignore_index=True)
        
    print('progress: ' , i+1, '/', len(final_final_list))

del df3['observations']
del df3['sourceId']
del df3['referenceTime']

df3.set_index('kommune', append=True)

df3 = df3.pivot(index='kommune', columns='tid', values='value') 
print(df3.head())
df3.to_excel("final_output.xlsx")

supplementary_stations = []
municipality_help_list2 = []
for i in range(len(final_list)):
    for j in range(len(data)):
        if('municipalityId' not in data[j]):
            err = 'no municipality id!'
            #print('err')
        else:
            if(data[j]['municipalityId'] not in municipality_help_list2):
                 if(data[j]['id']==final_list[i]):
                    supplementary_stations.append(final_list[i])
                    municipality_help_list2.append(data[j]['municipalityId'])

#for å hente suplerende data til df3
df4 = pd.DataFrame()
for i in range(len(supplementary_stations)):
    target_station = supplementary_stations[i]
    final_list.remove(supplementary_stations[i])
    print('target station: ',target_station)
    endpoint4 = 'https://frost.met.no/observations/v0.jsonld?referencetime=2000-01-01/2021-01-01&elements=mean(air_temperature%20P1M)'
    parameters4 = {
        'sources': target_station,
        'timeoffsets': 'PT0H'
    }
    # Issue an HTTP GET request
    r4 = requests.get(endpoint4, parameters4, auth=(client_id,''))
    # Extract JSON data
    json4 = r4.json()

    # Check if the request worked, print out any errors
    if r4.status_code == 200:
        data4 = json4['data']
    else:
        print('Error! Returned status code %s' % r4.status_code)
        print('Message: %s' % json4['error']['message'])
        print('Reason: %s' % json4['error']['reason'])

    for j in range(len(data4)):
        row = pd.DataFrame(data4[j])
        row['kommune'] = municipality_dict2[supplementary_stations[i]]
        date_time_str1 = data4[j]['referenceTime']
        date_time_obj1 = datetime.datetime.strptime(date_time_str1, '%Y-%m-%dT%H:%M:%S.%fZ')
        time_string = ''
        time_string += str(date_time_obj1.year)
        time_string += '_'
        time_string += måned_dict[date_time_obj1.month]
        row['tid'] = time_string
        row['value'] = data4[j]['observations'][0]['value']
        df4 = df4.append(row, ignore_index=True)
        
    print('progress: ' , i+1, '/', len(supplementary_stations))

del df4['observations']
del df4['sourceId']
del df4['referenceTime']

df4.set_index('kommune', append=True)

df4 = df4.pivot(index='kommune', columns='tid', values='value') 
print(df4.head())
df4.to_excel("final_output2.xlsx")


supplementary_stations2 = []
municipality_help_list3 = []
for i in range(len(final_list)):
    for j in range(len(data)):
        if('municipalityId' not in data[j]):
            err = 'no municipality id!'
            #print('err')
        else:
            if(data[j]['municipalityId'] not in municipality_help_list3):
                 if(data[j]['id']==final_list[i]):
                    supplementary_stations2.append(final_list[i])
                    municipality_help_list3.append(data[j]['municipalityId'])
#for å hente enda mer suplerende data til df3
df5 = pd.DataFrame()
for i in range(len(supplementary_stations2)):
    target_station = supplementary_stations2[i]
    final_list.remove(supplementary_stations2[i])
    print('target station: ',target_station)
    endpoint5 = 'https://frost.met.no/observations/v0.jsonld?referencetime=2000-01-01/2021-01-01&elements=mean(air_temperature%20P1M)'
    parameters5 = {
        'sources': target_station,
        'timeoffsets': 'PT0H'
    }
    # Issue an HTTP GET request
    r5 = requests.get(endpoint5, parameters5, auth=(client_id,''))
    # Extract JSON data
    json5 = r5.json()

    # Check if the request worked, print out any errors
    if r5.status_code == 200:
        data5 = json5['data']
    else:
        print('Error! Returned status code %s' % r5.status_code)
        print('Message: %s' % json5['error']['message'])
        print('Reason: %s' % json5['error']['reason'])

    for j in range(len(data5)):
        row = pd.DataFrame(data5[j])
        row['kommune'] = municipality_dict2[supplementary_stations[i]]
        date_time_str1 = data5[j]['referenceTime']
        date_time_obj1 = datetime.datetime.strptime(date_time_str1, '%Y-%m-%dT%H:%M:%S.%fZ')
        time_string = ''
        time_string += str(date_time_obj1.year)
        time_string += '_'
        time_string += måned_dict[date_time_obj1.month]
        row['tid'] = time_string
        row['value'] = data5[j]['observations'][0]['value']
        df5 = df5.append(row, ignore_index=True)
        
    print('progress: ' , i+1, '/', len(supplementary_stations2))

del df5['observations']
del df5['sourceId']
del df5['referenceTime']

df5.set_index('kommune', append=True)

df5 = df5.pivot(index='kommune', columns='tid', values='value') 
print(df5.head())
df5.to_excel("final_output3.xlsx")