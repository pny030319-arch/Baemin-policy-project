"""
Example script for collecting order history data.
Note:
- Actual shop identifiers, authentication cookies, and platform-specific endpoints are excluded for privacy and security reasons.
- This script demonstrates the data collection workflow used in the project.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import requests


PLATFORM_LOGIN_URL= 'https://example-platform-login-url.com'

options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

# Launch Chrome with predefined browser option
driver = webdriver.Chrome(options = options)
driver.get(PLATFORM_LOGIN_URL)

# Login
input('Press Enter after logging in...')

# Extract authenticated browser cookies after login
cookies = {c['name']: c['value'] for c in driver.get_cookies()}

# Create request headers for authenticated data requests
# based on values observed in the browser Network tab

headers = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'ko-KR, ko;q=0.9',
  'user-agent': driver.execute_script('return navigator.userAgent'),
  'origin': PLATFORM_LOGIN_URL,
  'referer': PLATFORM_LOGIN_URL + '/',
  'service-channel': 'SELF_SERVICE_PC',
  'x-pathname-trace-key': '/orders/history',
  'x-web-version': 'WEB_VERSION_PLACEHOLDER'
  }

# Iterate over defined date ranges to bypass API data limits
# and retrieve paginated order data using offset-based pagination

periods = [
    ('2024-01-01', '2024-06-30'),
    ('2024-07-01', '2024-12-31'),
    ('2025-01-01', '2025-06-30'),
    ('2025-07-01', '2025-12-31')
]

SHOP_OWNER = 'SHOP_ID_PLACEHOLDER'
API_URL = 'https://api.example.com/orders'
all_orders = []

for start, end in periods:
    offset = 0
    limit = 100
    while True:
        params = {
            'offset': offset, 
            'limit': limit,
            'startDate': start, 
            'endDate': end,
            'shopOwnerNumber': SHOP_OWNER,
            'shopNumbers': '',
            'orderStatus': 'CLOSED',
            }
        res = requests.get(
            API_URL,
            params=params,
            headers=headers,
            cookies=cookies
        )
        if res.status_code != 200:
            print(f'error: {res.status_code} - {res.text}')
            break

        data = res.json()
        orders = data.get('data', {}).get('orders', [])
        
        if not orders:
            print(f'  {start}~{end} complete!  n:{offset}')
            break

        all_orders.extend(orders)
        print(f'  collected {offset + len(orders)}')
        offset += limit
        
driver.quit()

df = pd.DataFrame(all_orders)
df.to_csv('baemin_orders_2024_2025.csv', index=False, encoding='utf-8-sig')