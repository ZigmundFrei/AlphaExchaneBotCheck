import requests
import math
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import datetime
from pytz import timezone
from multiprocessing.dummy import Pool as ThreadPool
import utils 
import re
### Блок для перевода текста


# Создание функции переводчика


def scrab_usdt_euro_rate(username, euro_amount):
    tz = timezone('Europe/Moscow')
    '''CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Баланс валют!2:100000").execute()

    rows = resp['values']

    headers = rows.pop(0)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    current_time = datetime.datetime.now(tz)

    USDT_EUR = 0.0
    found_flag = 'not found'
    for one_doc in sheet_data:
        if 'date' not in one_doc or one_doc['date'].strip() == '' or 'USD/EUR' not in one_doc or re.findall(r'[a-zA-Z]', one_doc['date']): continue
        doc_day = int(one_doc['date'].split('.')[0])
        doc_month = int(one_doc['date'].split('.')[1])
        doc_year = int(one_doc['date'].split('.')[2])
        usd_eur = one_doc['USD/EUR']
        currency = one_doc['currency']
        if doc_day == current_time.day and doc_month == current_time.month and doc_year == current_time.year and currency == 'USDT' and usd_eur != '':
            USDT_EUR = float(usd_eur.replace(',', '.'))
            found_flag = 'found
    date = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    print(f'{date}, tg_username = {username}, USDT_EURO GGLSH = {USDT_EUR} ({found_flag}), EURO AMOUNT = {euro_amount}')'''
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Length": "736",
        "Origin": "https://www.tradingview.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    data = {
        "columns":["name","description","currency_logoid","base_currency_logoid","update_mode","type","typespecs","exchange","provider-id","close","pricescale","minmov","fractional","minmove2","currency","change","24h_vol|5","24h_vol_change|5","high","low","volume","Recommend.All"],
        "filter":[{"left":"exchange","operation":"nequal","right":"BITMEX"},{"left":"description","operation":"nmatch","right":"Calculated By Tradingview"},{"left":"description","operation":"nmatch","right":"DOLLAR FORWARD"},{"left":"name","operation":"match","right":"^USDTEUR$"}],
        "ignore_unknown_fields": False,
        "options":{"lang":"en"},
        "range":[0,100],
        "sort":{"sortBy":"24h_vol|5","sortOrder":"desc"},
        "symbols":{"query":{"types":[]},"tickers":[]},
        "markets":["crypto"]
        }
    response = requests.post(url='https://scanner.tradingview.com/crypto/scan', headers=headers, json=data).json()
    USDT_EUR = response['data'][0]['d'][9] * 0.985
    date = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    print(f'{date}, tg_username = {username}, USDT_EURO = {USDT_EUR} tradingview, EURO AMOUNT = {euro_amount}')
    return USDT_EUR


def scrab_usdt_kzt_rate(username, kzt_amount):
    tz = timezone('Europe/Moscow')
    headers = {
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Length": "686",
        "Origin": "https://www.tradingview.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    data = {"filter":[{"left":"name,description","operation":"match","right":"usdtkzt"}],"options":{"lang":"en"},"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"expression":{"left":"type","operation":"in_range","right":["spot"]}}]}}]},"markets":["crypto"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["base_currency_logoid","currency_logoid","name","close","change","change_abs","high","low","volume","24h_vol|5","24h_vol_change|5","Recommend.All","exchange","description","type","subtype","update_mode","pricescale","minmov","fractional","minmove2"],"sort":{"sortBy":"name","sortOrder":"asc"},"price_conversion":{"to_symbol":False},"range":[0,150]}

    response = requests.post(url='https://scanner.tradingview.com/crypto/scan', headers=headers, json=data).json()
    USDT_KZT = response['data'][0]['d'][3] #* 0.993
    date = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    print(f'{date}, tg_username = {username}, USDT_KZT = {USDT_KZT} tradingview, KZT AMOUNT = {kzt_amount}')
    return USDT_KZT


def scrab_usdt_rub_rate(username, rub_amount):
    tz = timezone('Europe/Moscow')
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Length": "736",
        "Origin": "https://www.tradingview.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    data = {
        "columns":["name","description","currency_logoid","base_currency_logoid","update_mode","type","typespecs","exchange","provider-id","Recommend.MA","close","pricescale","minmov","fractional","minmove2","currency","SMA20","SMA50","SMA200","BB.upper","BB.lower"],
        "filter":[{"left":"exchange","operation":"nequal","right":"BITMEX"},{"left":"description","operation":"nmatch","right":"Calculated By Tradingview"},{"left":"description","operation":"nmatch","right":"DOLLAR FORWARD"},{"left":"name","operation":"match","right":"^USDTRUB$"}],
        "ignore_unknown_fields":False,
        "options":{"lang":"en"},
        "range":[0,100],
        "sort":{"sortBy":"24h_vol|5","sortOrder":"desc"},
        "symbols":{"query":{"types":[]},"tickers":[]},
        "markets":["crypto"]
        }
    response = requests.post(url='https://scanner.tradingview.com/crypto/scan', headers=headers, json=data).json()
    USDT_RUB = response['data'][0]['d'][10]
    date = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    print(f'{date}, tg_username = {username}, USDT_RUB = {USDT_RUB} tradingview, RUB AMOUNT = {rub_amount}')
    return USDT_RUB

def compute_usdt_euro_amount(euro_amount, username):
    # Границу переопределил на 5000, было 3000 (09.02.2023)
    return_norm = 0.015 if euro_amount < 5000 else 0.01

    usdt_euro_rate = scrab_usdt_euro_rate(username, euro_amount)
    usdt_amount = euro_amount * (1 + return_norm) / usdt_euro_rate
    #Переменные для списка актуальных курсов
    ##Курс до 5000 евро
    low_rate = 1 * (1 + 0.015) / usdt_euro_rate
    ##Курс свыше 5000 евро
    high_rate = 1 * (1 + 0.01) / usdt_euro_rate
    return {
        'usdt_amount': math.ceil(usdt_amount),
        'usdt_eur_rate': round(euro_amount / math.ceil(usdt_amount), 4),
        'low_rate': round(1 / low_rate, 4),
        'high_rate': round(1 / high_rate, 4),
        'usdt_eur_rate_gs': usdt_euro_rate
    }


def compute_usdt_rub_amount(rub_amount, username, cash_flag, bank_name):
    # Границу переопределил на 5000, было 3000 (09.02.2023)
    return_norm = 0.01 if rub_amount < 500000 else 0.015
    if bank_name == utils._('Сбербанк'):
        payment = ["582"]
    elif bank_name == utils._('Тинькофф'):
        payment = ["581"]
    elif bank_name == utils._('Райффайзен'):
        payment = ["64"]
    else:
        payment = ["64", "582", "581", "583"]
    if cash_flag:
        response = requests.get(url='https://garantex.org/api/v2/depth?market=usdtrub').json()
        usdt_rub_rate = float(response['asks'][0]['price'])
    else:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU",
            "Cache-Control": "no-cache",
            "Content-Length": "149",
            "content-type": "application/json;charset=UTF-8",
            "Origin": "https://www.bybit.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }
        # уточнить параметры у Антона
        data = {"userId": 19502056,
                "tokenId": "USDT",
                "currencyId": "RUB",
                "payment": payment,
                "side": "0",
                "size": "10",
                "page": "1",
                "amount": "",
                "authMaker": False,
                "canTrade": False}

        r = requests.post('https://api2.bybit.com/fiat/otc/item/online', headers=headers, json=data)
        json_data = r.json()
        #usdt_rub_rate = get_p2p_rate((rub_amount, 1, username, bank_name))[1] #далее предусмотреть выбор банка в p2p
        usdt_rub_rate = float(json_data['result']['items'][3]['price'])
    usdt_amount = rub_amount * (1 + return_norm) / usdt_rub_rate
    #Переменные для списка актуальных курсов
    ##Курс до 5000 евро
    low_rate = 1 * (1 + 0.01) * usdt_rub_rate #0.015
    ##Курс свыше 5000 евро
    high_rate = 1 * (1 + 0.015) * usdt_rub_rate #0.01
    return {
        'usdt_amount': math.ceil(usdt_amount),
        'usdt_rub_rate': round(rub_amount / math.ceil(usdt_amount), 4),
        'low_rate': round(low_rate, 4),
        'high_rate': round(high_rate, 4),
        'usdt_rub_rate_bybit': usdt_rub_rate
    }

def compute_usdt_uah_amount(uah_amount, username, bank_name):
    # Границу переопределил на 5000, было 3000 (09.02.2023)
    return_norm = 0.015 if uah_amount < 200000 else 0
    if bank_name == utils._('Monobank'):
        payment = ["43"]
    elif bank_name == utils._('PUMB'):
        payment = ["61"]
    elif bank_name == utils._('ПриватБанк'):
        payment = ["60"]
    elif bank_name == utils._('А-Банк'):
        payment = ["1"]
    elif bank_name == utils._('Izibank'):
        payment = ["544"]
    else:
        payment = ["43", "60", "1", "61", "544"]
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU",
        "Cache-Control": "no-cache",
        "Content-Length": "149",
        "content-type": "application/json;charset=UTF-8",
        "Origin": "https://www.bybit.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    # уточнить параметры у Антона
    data = {"userId": 19502056,
            "tokenId":"USDT",
            "currencyId":"UAH",
            "payment": payment,
            "side":"1",
            "size":"10",
           "page":"1",
           "amount":"",
           "authMaker":False,
           "canTrade":False}
    r = requests.post('https://api2.bybit.com/fiat/otc/item/online', headers=headers, json=data)
    json_data = r.json()
    usdt_uah_rate = float(json_data['result']['items'][1]['price'])
    usdt_amount = uah_amount * (1 + return_norm) / usdt_uah_rate
    #Переменные для списка актуальных курсов
    ##Курс до 5000 евро
    low_rate = 1 * (1 - 0.015) * usdt_uah_rate
    ##Курс свыше 5000 евро
    high_rate = 1 * (1 - 0.01) * usdt_uah_rate
    return {
        'usdt_amount': math.ceil(usdt_amount),
        'usdt_uah_rate': round(uah_amount / math.ceil(usdt_amount), 4),
        'low_rate': round(low_rate, 4),
        'high_rate': round(high_rate, 4),
        'usdt_uah_rate_bybit': usdt_uah_rate
    }

def compute_usdt_kzt_amount(kzt_amount, username, bank_name):
    # Границу переопределил на 5000, было 3000 (09.02.2023)
    return_norm = 0.015 if kzt_amount < 2499999 else 0
    if bank_name == utils._('Kaspi Bank'):
        payment = ["150"]
    elif bank_name == utils._('Halyk Bank'):
        payment = ["203"]
    elif bank_name == utils._('ЦентрКредит Банк'):
        payment = ["211"]
    elif bank_name == utils._('Jysan Bank'):
        payment = ["149"]
    elif bank_name == utils._('Forte Bank'):
        payment = ["144"]
    elif bank_name == utils._('Altyn Bank'):
        payment = ["280"]
    elif bank_name == utils._('Freedom Bank'):
        payment = ["549"]
    else:
        payment = ["150", "203", "280", "211", "144", "549", "149"]
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU",
        "Cache-Control": "no-cache",
        "Content-Length": "149",
        "content-type": "application/json;charset=UTF-8",
        "Origin": "https://www.bybit.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    # уточнить параметры у Антона
    data = {"userId": 19502056,
            "tokenId":"USDT",
            "currencyId":"KZT",
            "payment": payment,
            "side":"1",
            "size":"10",
           "page":"1",
           "amount":"",
           "authMaker":False,
           "canTrade":False}
    r = requests.post('https://api2.bybit.com/fiat/otc/item/online', headers=headers, json=data)
    json_data = r.json()
    usdt_kzt_rate = float(json_data['result']['items'][1]['price'])
    usdt_amount = kzt_amount * (1 + return_norm) / usdt_kzt_rate
    #Переменные для списка актуальных курсов
    ##Курс до 5000 евро
    low_rate = 1 * (1 - 0.015) * usdt_kzt_rate
    ##Курс свыше 5000 евро
    high_rate = 1 * (1 - 0.01) * usdt_kzt_rate
    return {
        'usdt_amount': math.ceil(usdt_amount),
        'usdt_kzt_rate': round(kzt_amount / math.ceil(usdt_amount), 4),
        'low_rate': round(low_rate, 4),
        'high_rate': round(high_rate, 4),
        'usdt_kzt_rate_bybit': usdt_kzt_rate
    }

def compute_rub_euro_amount(euro_amount, username, cash_flag, bank_name):
    # переопределили норму доходности (09.02.2023)
    if euro_amount < 500:
        return_norm = 0.033
    elif euro_amount < 1000:
        return_norm = 0.0255
    elif euro_amount < 3000:
        return_norm = 0.019
    elif euro_amount < 10000:
        return_norm = 0.017
    else:
        return_norm = 0.015
    usdt_euro_rate = scrab_usdt_euro_rate(username, euro_amount)
    if cash_flag:
        response = requests.get(url='https://garantex.org/api/v2/depth?market=usdtrub').json()
        p2p_rub_usdt = float(response['asks'][0]['price']) * 1.0025
    else:
        p2p_rub_usdt = get_p2p_rate((euro_amount, usdt_euro_rate, username, bank_name))[1] #далее предусмотреть выбор банка в p2p
    rub_amount = euro_amount * (1 + return_norm) * (p2p_rub_usdt) / usdt_euro_rate
    return {
        'rub_amount': math.ceil(rub_amount),
        'currency_rate': round(math.ceil(rub_amount) / euro_amount, 2),
        'p2p_rub_usdt': p2p_rub_usdt,
        'usdt_euro_rate': usdt_euro_rate
    }

def compute_rub_kzt_amount(kzt_amount, username, bank_name):
    # переопределили норму доходности (09.02.2023)
    if kzt_amount < 250000:
        return_norm = 0.03
    elif kzt_amount < 500000:
        return_norm = 0.0225
    elif kzt_amount < 1400000:
        return_norm = 0.016
    elif kzt_amount < 4800000:
        return_norm = 0.014
    else:
        return_norm = 0.012
    usdt_kzt_rate = scrab_usdt_kzt_rate(username, kzt_amount)
    p2p_rub_usdt = get_p2p_rate((kzt_amount, 1/usdt_kzt_rate, username, bank_name))[1] #далее предусмотреть выбор банка в p2p
    rub_amount = kzt_amount * (1 + return_norm) * (p2p_rub_usdt) / usdt_kzt_rate
    return {
        'rub_amount': math.ceil(rub_amount),
        'currency_rate': round(math.ceil(rub_amount) / kzt_amount, 4),
        'p2p_rub_usdt': p2p_rub_usdt,
        'usdt_euro_rate': usdt_kzt_rate
    }


def get_p2p_rate(pool_doc):
    #________________________________Bybit
    euro_amount = pool_doc[0]
    usdt_euro_rate = pool_doc[1]
    username = pool_doc[2]
    bank_name = pool_doc[3]
    tz = timezone('Europe/Moscow')
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU",
        "Cache-Control": "no-cache",
        "Content-Length": "149",
        "content-type": "application/json;charset=UTF-8",
        "Origin": "https://www.bybit.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    # уточнить параметры у Антона
    if bank_name == utils._('Сбербанк'):
        payment = ["582"]
    elif bank_name == utils._('Тинькофф'):
        payment = ["581"]
    elif bank_name == utils._('Райффайзен'):
        payment = ["64"]
    else:
        payment = ["583"]
    data = {"userId": 19502056,
            "tokenId": "USDT",
            "currencyId": "RUB",
            "payment": payment,
            "side": "1",
            "size": "10",
            "page": "1",
            "amount": "",
            "authMaker": False,
            "canTrade": False}

    r = requests.post('https://api2.bybit.com/fiat/otc/item/online', headers=headers, json=data)
    json_data = r.json()

    price = 0.0
    found_flag = 'found'
    nick_name_saler = 'NaN'
    q = 0
    for row in json_data['result']['items'][4:]:
        order_rub_min = float(row['minAmount'])
        order_rub_max = float(row['maxAmount'])
        recent_execute_rate = int(row['recentExecuteRate'])
        recent_order_num = int(row['recentOrderNum'])
        rub_usdt = float(row['price'])  # rub/usdt
        rub_need = euro_amount / usdt_euro_rate * rub_usdt
        if (payment != ["583"] and rub_need >= order_rub_min and rub_need <= order_rub_max or payment == ["583"]) and recent_execute_rate >= 95 and recent_order_num >= 100:
            q += 1
            price += rub_usdt + 0.15
            nick_name_saler = row['nickName']
    if price == 0.0 or q == 0:
        price = float(json_data['result']['items'][-1]['price']) + 0.15
        found_flag = 'not found'
    else:
        price = price / q
    date = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    print(f'{date}, tg_username = {username}, RUB_USDT P2P = {price} ({found_flag}), EURO AMOUNT = {euro_amount}, nickName = {nick_name_saler}\n')
    return (euro_amount, price, username)

def get_rates_data(username, bank_name):
    usdt_euro_rate = scrab_usdt_euro_rate(username, '*for get_rates')
    euro_boards = [499, 999, 2999, 9999, 10001] #границы для запроса к P2P
    pool_data = [(euro_board, usdt_euro_rate, username, bank_name) for euro_board in euro_boards]
    pool = ThreadPool(20)
    pool_result = pool.map(get_p2p_rate, pool_data)
    pool.close()
    pool.join()

    return_data = {}
    for pool_doc in pool_result:
        euro_amount = pool_doc[0]
        p2p_rub_usdt = pool_doc[1]
        # переопределили норму доходности (09.02.2023)
        if euro_amount < 500:
            return_norm = 0.033
        elif euro_amount < 1000:
            return_norm = 0.0255
        elif euro_amount < 3000:
            return_norm = 0.019
        elif euro_amount < 10000:
            return_norm = 0.017
        else:
            return_norm = 0.015
        rub_amount = euro_amount * (1 + return_norm) * (p2p_rub_usdt) / usdt_euro_rate
        rub_euro_rate = round(math.ceil(rub_amount) / euro_amount, 2)
        return_data[euro_amount] = rub_euro_rate
    return return_data


def get_rates_rub_kzt_data(username, bank_name):
    usdt_kzt_rate = scrab_usdt_kzt_rate(username, '*for get_rates')
    kzt_boards = [249999, 499999, 1499999, 4999999, 5000000] #границы для запроса к P2P
    pool_data = [(kz_board, usdt_kzt_rate, username, bank_name) for kz_board in kzt_boards]
    pool = ThreadPool(20)
    pool_result = pool.map(get_p2p_rate, pool_data)
    pool.close()
    pool.join()

    return_data = {}
    for pool_doc in pool_result:
        kzt_amount = pool_doc[0]
        p2p_rub_usdt = pool_doc[1]
        # переопределили норму доходности (09.02.2023)
        if kzt_amount < 249999:
            return_norm = 0.03
        elif kzt_amount < 499999:
            return_norm = 0.0225
        elif kzt_amount < 1499999:
            return_norm = 0.016
        elif kzt_amount < 4999999:
            return_norm = 0.014
        else:
            return_norm = 0.012
        rub_amount = kzt_amount * (1 + return_norm) * (p2p_rub_usdt) / usdt_kzt_rate
        rub_kzt_rate = round(math.ceil(rub_amount) / kzt_amount, 4)
        return_data[kzt_amount] = rub_kzt_rate
    return return_data

def get_fiat_rates_tradingview():    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Length": "396",
        "Content-Type": "text/plain;charset=UTF-8",
        "Origin": "https://www.tradingview.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        }
    data = {"columns":["currency_logoid","base_currency_logoid","name","description","update_mode","type","typespecs","close","pricescale","minmov","fractional","minmove2","currency","change","change_abs","bid","ask","high","low","Recommend.All"],"ignore_unknown_fields":False,"options":{"lang":"en"},"range":[0,2000],"sort":{"sortBy":"name","sortOrder":"asc","nullsFirst":False},"preset":"forex_rates_all"}

    response = requests.post(url='https://scanner.tradingview.com/forex/scan', headers=headers, json=data).json()
    USD_RUB = 0
    EUR_RUB = 0
    BGN_RUB = 0
    EUR_USD = 0
    EUR_UAH = 0
    USD_UAH = 0
    USD_KZT = 0
    EUR_KZT = 0
    RSD_USD = 0
    RSD_EUR = 0
    for pair in response['data']:
        if pair['d'][2] == 'USDRUB' and USD_RUB == 0:
            USD_RUB = pair['d'][7]
        elif pair['d'][2] == 'EURRUB' and EUR_RUB == 0:
            EUR_RUB = pair['d'][7]
        elif pair['d'][2] == 'USDBGN' and BGN_RUB == 0:
            BGN_RUB = pair['d'][7]
        elif pair['d'][2] == 'EURUSD' and EUR_USD == 0:
            EUR_USD = pair['d'][7]
        elif pair['d'][2] == 'EURUAH' and EUR_UAH == 0:
            EUR_UAH = pair['d'][7]
        elif pair['d'][2] == 'EURKZT' and EUR_KZT == 0:
            EUR_KZT = pair['d'][7]
        elif pair['d'][2] == 'USDUAH' and USD_UAH == 0:
            USD_UAH = pair['d'][7]
        elif pair['d'][2] == 'USDKZT' and USD_KZT == 0:
            USD_KZT = pair['d'][7]
        elif pair['d'][2] == 'RSDUSD' and RSD_USD == 0:
            RSD_USD = pair['d'][7]
        elif pair['d'][2] == 'RSDEUR' and RSD_EUR == 0:
            RSD_EUR = pair['d'][7]
        elif USD_RUB != 0 and EUR_RUB != 0 and BGN_RUB != 0 and EUR_USD != 0 and EUR_UAH != 0 and EUR_KZT != 0 and USD_UAH != 0 and USD_KZT != 0 and RSD_USD != 0 and RSD_EUR != 0:
            break
    BGN_RUB = USD_RUB / BGN_RUB
    tz = timezone('Europe/Moscow')
    date = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    print(f'{date}, USD_RUB = {USD_RUB}, EUR_RUB = {EUR_RUB}, BGN_RUB = {BGN_RUB}, EUR_USD = {EUR_USD}, USD_EUR = {1/EUR_USD}, EUR_UAH = {EUR_UAH}, EUR_KZT = {EUR_KZT} tradingview')
    return {'USD_RUB': USD_RUB, 'EUR_RUB': EUR_RUB, 'BGN_RUB': BGN_RUB, 'EUR_USD': EUR_USD, 'USD_EUR': 1/EUR_USD, 'EUR_UAH': EUR_UAH, 'EUR_KZT': EUR_KZT, 'RSD_USD': RSD_USD, 'RSD_EUR': RSD_EUR, 'USD_UAH': USD_UAH, 'USD_KZT': USD_KZT}


def compute_to_rub_amount(currency_amount, currency_from, bank_name, username):
    # переопределили норму доходности (09.02.2023)
    fiat_rates = get_fiat_rates_tradingview()
    eur_rub_rate = fiat_rates['EUR_RUB']
    eur_usd_rate = fiat_rates['EUR_USD']
    usdt_rub_rate = get_p2p_rate((currency_amount, eur_rub_rate, username, bank_name))[1]
    if currency_amount < 50000:
        return_norm = 0.0075
    elif currency_amount < 100000:
        return_norm = 0.0032
    elif currency_amount < 300000:
        return_norm = 0.00
    elif currency_amount < 1000000:
        return_norm = -0.0025
    else:
        return_norm = -0.005
    #currency_from_amount = currency_amount * (1 + return_norm) / usdt_rub_rate / eur_usd_rate / 0.987
    currency_from_amount = currency_amount / eur_rub_rate * (1 + return_norm)
    test_rate = usdt_rub_rate / eur_usd_rate
    return {
        'p2p_rub_usdt': usdt_rub_rate,
        'currency_amount': currency_amount,
        'currency_from_amount': math.ceil(currency_from_amount),
        'currency_rate': round(currency_amount / math.ceil(currency_from_amount), 3),
        'currency_rate_trading': test_rate,
        'usdt_eur_rate': eur_usd_rate
    }

def multi_run_wrapper(args):
   return compute_to_rub_amount(*args)

def get_rates_buy_eur_data(currency_from, bank_name, username):
    rub_boards = [49999, 99999, 299999, 999999, 1000001] #границы для запроса к P2P
    pool_data = [(rub_board, currency_from, bank_name, username) for rub_board in rub_boards]
    pool = ThreadPool(20)
    pool_result = pool.map(multi_run_wrapper, pool_data)
    pool.close()
    pool.join()

    return_data = {}
    for pool_doc in pool_result:
        currency_rate = pool_doc['currency_rate']
        currency_amount = pool_doc['currency_amount']
        return_data[currency_amount] = currency_rate
    return return_data
