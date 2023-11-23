import requests

headers = {"Content-Type": "application/json"}

url = 'http://127.0.0.1:5000/get_response'
data = {"query": {"company_name": "GOOGL", "parameter": "price", "start_date": "DATE(2023,10,1)",
                  "end_date": "DATE(2023,11,1)", "interval": "DAILY"}}  # Your data to be sent

response = requests.post(url, data=data, headers=headers)

print(response.json()["output"])