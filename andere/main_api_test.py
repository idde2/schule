import requests
def apiget(path,args=None,args2=None):
    if args and not args2:
        API_URL = f"http://localhost:5000/api/{path}/{args}"
    elif args2:
        API_URL = f"http://localhost:5000/api/{path}/{args}/{args2}"
    else:
        API_URL = f"http://localhost:5000/api/{path}"

    headers = { "X-API-KEY": "2026!", "Content-Type": "application/json"}

    response = requests.get( API_URL,headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return f"Fehler: {response.status_code}"



def apipost(path,args=None,args2=None,data=None):
    if args and not args2:
        API_URL = f"http://localhost:5000/api/{path}/{args}"
    elif args2:
        API_URL = f"http://localhost:5000/api/{path}/{args}/{args2}"
    else:
        API_URL = f"http://localhost:5000/api/{path}"

    headers = { "X-API-KEY": "2026!"}

    response = requests.post( API_URL,headers=headers,json=data)

    if response:
        return response.json()
    else:
        return f"Fehler: {response.status_code}"


data = {
    "name": "test",
    "wert": 1000
}
print(apipost(path="daten",data=data))
