import requests
from pprint import pprint
import pandas as pd

def get_trc_data(trc_net, address, limit=50):
    api_path = 'https://apilist.tronscanapi.com/api/token_trc20/transfers?' if trc_net == 'TRC-20' else \
                    'https://apilist.tronscanapi.com/api/transfer?'
    data_key = 'token_transfers' if trc_net == 'TRC-20' else 'data'
    address_atr = 'relatedAddress' if trc_net == 'TRC-20' else 'address'
    all_data = []
    start_count = 0
    while True:
        url = f'{api_path}' \
            f'limit={limit}&' \
            f'start={start_count}&' \
            f'sort=-timestamp&' \
            f'count=true&' \
            f'filterTokenValue=0&' \
            f'{address_atr}={address}'
    
        data = requests.get(url).json()
        len_data = data['total']
        all_data.extend(data[data_key])
        if start_count + limit < len_data:
            start_count += limit
        else:
            break
    return all_data

def check_risk_trc(all_data_trc10, all_data_trc20):
    risk = False
    all_data = all_data_trc10 + all_data_trc20
    for one_tranfer in all_data:
        riskTransaction = one_tranfer['riskTransaction']
        if riskTransaction:
            risk = riskTransaction
            break 
    return risk

#all_data_trc10 = get_trc_data('TRC-10', 'TYK7FcLzXHoX8Ek8KvRZPvjwwbJCW6Wwvu')
#all_data_trc20 = get_trc_data('TRC-20', 'TYK7FcLzXHoX8Ek8KvRZPvjwwbJCW6Wwvu')
#RISK_TRC = check_risk_trc(all_data_trc10, all_data_trc20)
#print(RISK_TRC)