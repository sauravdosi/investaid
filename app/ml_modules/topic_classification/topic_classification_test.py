import requests

headers = {"Content-Type": "application/json"}

url = 'http://127.0.0.1:5000/get_response'
data = {"query": {"text": "However, Tesla’s share of the EV segment continues to plunge, hitting 50% in Q3, the lowest level on record and down from 62% in Q1.",
                  "classifier": "all", "custom_classes": ["business","other"], "custom_multiclass": False}}  # Your data to be sent

response = requests.post(url, json=data, headers=headers)

print(response.json()["output"])