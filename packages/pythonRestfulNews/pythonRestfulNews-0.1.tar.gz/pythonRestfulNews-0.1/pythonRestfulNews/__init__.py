import requests
import json


def create_user(email, password, name='unknown', picture=''):
    url = 'http://api.restfulnews.com/users'
    headers = {'content-type': 'application/json'}    
    data = dict(
        email=email,
        password=password,
        name=name,
        picture=picture
    )
    json_data = json.dumps(data)
    
    resp = requests.post(url=url, data=json_data, headers=headers)
    data = resp.json()
    
    return data

def search_news(token, topics, companyids, start_date, end_date):
    
    url =  'http://api.restfulnews.com/search'
    auth = 'Bearer ' + token
    
    headers = {'content-type': 'application/json', 'authorization': auth}  
    
    params = dict(
        topics=topics,
        companyids=companyids,
        start_date=start_date,
        end_date=end_date
    )
    print(headers)
    json_params = json.dumps(params)
    
    resp = requests.get(url=url, params=json_params, headers=headers)
    print(resp)
    data = resp.json()
    
    return data