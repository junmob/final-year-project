import requests

# Timeout = seconds of silence from the server before giving up (not the total download time).
# - Not set: if the server never answers, the script hangs forever, nothing is logged, the code
#   below never runs, and the next scheduled run cannot start.
# - Too small: a slow but working server is treated as a failure, and that forecast version is
#   lost for good.
# - Too big: only a longer wait when the server is really down; nobody waits on this background
#   job, so 60 s is safe as long as it stays far below the run interval (3 h).
response = requests.get('https://api.data.gov.my/weather/forecast/', timeout=60)

data = response.json()

# Print HTTP status code
print(f'HTTP Status Code: {response.status_code}')

# Print Record count
print(f'Response: {len(data)} records')

# Print the first record
print(f'First Record: {data[0]}')

