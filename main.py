# import json

# with open('data_storage/placeholder.json', 'r') as f:
#     data = json.load(f)

# marin_vax = {}

# for day in data:
#     if 'marin_pop' in day:
#         marin_vax[day['date']] = day['marin_pop']

# with open('data_storage/marin_vax.json', 'w') as f:
#     json.dump(marin_vax, f)

from downloader import download_data
download_data()