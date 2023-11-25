import requests

headers = {"Content-Type": "application/json"}

url = 'http://127.0.0.1:5000/get_response'
data = {"query": "Tesla"}  # Your data to be sent

response = requests.post(url, json=data, headers=headers)

print(response.json()["output"])
