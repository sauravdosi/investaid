import requests

url = 'http://127.0.0.1:5000/get_response'
data = {'prompt': 'Tell me about electric vehicles'}  # Your data to be sent

response = requests.post(url, data=data)

print(response.json()["output"])