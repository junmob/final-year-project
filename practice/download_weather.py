import requests

r = requests.get('https://api.data.gov.my/weather/forecast/', timeout=5)

# Print HTTP status code
print(f'HTTP Status Code: {r.status_code}')

# Print Record count
print(f'Response: {len(r.json())} records')

# Print the first record
print(f'First Record: {r.json()[0]}')

