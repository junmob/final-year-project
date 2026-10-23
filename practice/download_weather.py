import requests

# Set timeout to 60 seconds, 60 seconds is not too long for a request, but it is long enough to avod timeout errors for slow connections or large responses.
# Timeout too big can cause ...
# Timeout too small can cause ...
# Timeout is not set can cause ...
response = requests.get('https://api.data.gov.my/weather/forecast/', timeout=60)

data = response.json()

# Print HTTP status code
print(f'HTTP Status Code: {response.status_code}')

# Print Record count
print(f'Response: {len(data)} records')

# Print the first record
print(f'First Record: {data[0]}')

