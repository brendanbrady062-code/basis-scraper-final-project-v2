import requests
import json
import re

url = 'https://cargillus.websol.barchart.com/?jsonpFunction=jQuery37007274726507964236_1782160231242&module=cashbids&location=62677&output=json&commOverviewByLocation=1&commRoots=%2CZS%2CZS&_=1782160231243'

response = requests.get(url, verify=False, timeout=10)
match = re.match(r'^[^(]+\((.*)\)\s*;?\s*$', response.text, re.S)
data = json.loads(match.group(1))

print('Group names in API response:')
for group in data.get('bigGroups', []):
    print(f"  - {group.get('name')}")
    print(f"    Bid count: {len(group.get('cashbids', []))}")
    for bid in group.get('cashbids', [])[:2]:
        print(f"      {bid.get('delivery_start')} - {bid.get('delivery_end')}: basis {bid.get('basis')}")
