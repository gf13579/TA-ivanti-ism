import os
import sys
import time
import datetime
import requests
import json
from urllib import unquote
import logging

def authenticate(tenant, username, password, role):    
    base_url = 'https://' + tenant
    payload = {
        'tenant': tenant,
        'username':username,
        'password':password,
        'role':role
    }

    headers = {
        "Content-Type" : "application/json"
    }
    
    response = requests.post(base_url + '/api/rest/authentication/login',data=json.dumps(payload),headers=headers,verify=False)

    if response.status_code != 200:
        logging.warning("Failed to connect or authenticate")
        logging.info(response.content)
        exit()

    auth_token = (response.content).decode('UTF-8').replace('"','')
    logging.info("auth_token is " + str(auth_token))

    return auth_token

def get_incidents_simple(auth_token, base_url, parameters):
    path = '/api/odata/businessobject/incidents' 
    return get_busobjects(auth_token, base_url, path, parameters, 100)

def get_incidents(auth_token, base_url, parameters):
    path = '/api/odata/businessobject/incidents' 
    incs = get_busobjects(auth_token, base_url, path, parameters, 100)

    breaches = get_busobjects(auth_token, base_url, '/api/odata/businessobject/Frs_data_escalation_watchs', "$filter=ClockState eq 'Run' and ParentLink_Category eq 'Incident'&$select=L3Passed, BreachPassed, BreachDateTime, RecId",100) 
        
    breach_times = {}
    for b in breaches:
        #if b['BreachPassed'] == False:
        #    if datetime.datetime.strptime(b['BreachDateTime'], '%Y-%m-%dT%H:%M:%SZ') < (datetime.datetime.now() + datetime.timedelta(hours=24)):
        #        #print(b['BreachDateTime'])
        #        breach_times[b['RecId']] = b['BreachDateTime']
        if b['BreachPassed'] == False:
            breach_times[b['RecId']] = b['BreachDateTime']
    for i in incs:
        if i['ResolutionEscLink_RecID'] in breach_times:
            i['BreachDateTime'] = breach_times[i['ResolutionEscLink_RecID']]

    return incs    

def get_servicereqs(auth_token, base_url, parameters):
    path = '/api/odata/businessobject/servicereqs' 
    return get_busobjects(auth_token, base_url, path, parameters, 100)
    
def get_busobjects(auth_token, base_url, path, parameters, page_size):
    headers = {
        "Content-Type" : "application/json",
        "Authorization" : auth_token
    }
    url = base_url + path + '?$top=' + str(page_size) + '&$skip=0&' + parameters
    
    response = requests.get(url, headers=headers,verify=False)

    r_json = response.json()
    values = response.json()['value']
    logging.info("count returned by initial query: " + str(int(r_json['@odata.count'])))

    if r_json['@odata.count'] > page_size:
        count = int(r_json['@odata.count'])
        for i in range(page_size,count,page_size):
            logging.info("iterating with skip set to " + str(count))
            request_str = base_url + path + "?$top=" + str(page_size) + "&$skip=" + str(i) + '&' + parameters
            response = requests.get(request_str, headers=headers,verify=False)
            j2 = response.json()
            values.extend(j2['value'])

    return values


