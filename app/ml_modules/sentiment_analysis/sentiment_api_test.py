import requests

url = 'http://127.0.0.1:5000/get_sentiment'
data = {'text': "Tesla launches it's own car insurance,  these drivers say it's lemons", 'model': 'all'}  # Your data to be sent

response = requests.post(url, data=data)

print(response.json()["output"])
