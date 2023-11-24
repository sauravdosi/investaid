import requests

url = 'http://127.0.0.1:5000/get_response'
data = {'prompt': ['Tell me about football', 'Tell me about cricket', 'Tell me about hockey',
        'Tell me about kabbaddi', 'Tell me about marathon', 'Tell me about swimming', 'Tell me about volleyball',
        'Tell me about table tennis', 'Tell me about tennis', 'Tell me about chess', 'Tell me about basketball',
        'Tell me about dodgeball', 'Tell me about beachball', 'Tell me about golf']}  # Your data to be sent

response = requests.post(url, data=data)

print(response.json())