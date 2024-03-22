import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import re
import json
import unidecode

def check_balance(username):
    with open('contacts.json', 'r', encoding='utf8') as f:
        ACTIVE_CONTACT_LIST = json.load(f)
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Баланс валют!A2:R1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    rows = list(map(lambda row: list(map(lambda elem: elem.replace(u'\xa0', ''), row)), resp['values'][-100:]))
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    #balance = [one_doc for one_doc in sheet_data if 'date' in one_doc and len(one_doc['date']) == 10 and not re.findall(r'[a-zA-Z]', one_doc['date'])]
    balance = [one_doc for one_doc in sheet_data if 'date' in one_doc]
    tomorrow = str((datetime.now()+timedelta(days=1)).strftime('%d.%m.%Y'))
    today = str(datetime.now().strftime('%d.%m.%Y'))
    yesterday = str((datetime.now()-timedelta(days=1)).strftime('%d.%m.%Y'))
    mess_tommorow = ''
    mess = ''
    tomorrow_flag = False
    day_start = False
    user_existence_flag = False
    #if balance[-1]['date'] != tomorrow:
    #    balance = balance[-6:]
    #    mess_tommorow = '\n<em><b>На завтра нет данных!</b></em>'
    #else:
    #    balance = balance[-9:]
    for info in balance:
        if 'tec' in info.keys():
            if info['date'] == yesterday or info['date'] == today or info['date'] == tomorrow and info['tec'] == 'start':
                if info['date'] == tomorrow:
                    tomorrow_flag = True
                day_start = True
                mess += f'\n<b>Дата: {info["date"]}</b>\n'
            elif info['tec'] == 'end':
                day_start = False
        if day_start == True and info['date'] != '':
            if ACTIVE_CONTACT_LIST[username]['ContactType']=='Партнер':
                user_existence_flag = True
                if info['date'] == yesterday or info['date'] == today or info['date'] == tomorrow:
                    username_mess = ''
                else:
                    username_mess = f'<b>{info["date"]}</b> \n'
                mess += username_mess
                mess += f'<b><em>{info["currency"]}</em></b>\n' \
                        f'<em>Сумма на начало:</em> {info["opening balance"]} \n' \
                        f'<em>Сумма поступлений:</em> {info["inflow"]}\n' \
                        f'<em>Сумма выбытий:</em> {info["outflow"]}\n' \
                        f'<em>Cумма на конец:</em> {info["closing balance"]}\n'
                if (info['date'] == yesterday or info['date'] == today or info['date'] == tomorrow) and info['currency'] == 'USDT': 
                    mess += f'<em>Курс USDT/EUR</em>: {info["USD/EUR"]}\n'
            else:
                if info['date']==username:
                    user_existence_flag = True
                    mess += f'<b><em>{info["currency"]}</em></b>\n' \
                        f'<em>Сумма на начало:</em> {info["opening balance"]} \n' \
                        f'<em>Сумма поступлений:</em> {info["inflow"]}\n' \
                        f'<em>Сумма выбытий:</em> {info["outflow"]}\n' \
                        f'<em>Cумма на конец:</em> {info["closing balance"]}\n'
    if not tomorrow_flag:
        mess_tommorow = '\n<em><b>На завтра нет данных!</b></em>'
    mess += mess_tommorow
    if not user_existence_flag:
        mess = 'Для вас нет записей'
    return mess

def cards_balance(username):
    with open('contacts.json', 'r', encoding='utf8') as f:
        ACTIVE_CONTACT_LIST = json.load(f)
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Баланс карт!A2:N1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    rows = list(map(lambda row: list(map(lambda elem: elem.replace(u'\xa0', ''), row)), resp['values'][-100:]))
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    #balance = [one_doc for one_doc in sheet_data if 'date' in one_doc and len(one_doc['date']) == 10 and not re.findall(r'[a-zA-Z]', one_doc['date'])]
    balance = [one_doc for one_doc in sheet_data if 'date' in one_doc]
    tomorrow = str((datetime.now()+timedelta(days=1)).strftime('%d.%m.%Y'))
    today = str(datetime.now().strftime('%d.%m.%Y'))
    yesterday = str((datetime.now()-timedelta(days=1)).strftime('%d.%m.%Y'))
    mess_tommorow = ''
    mess = ''
    tomorrow_flag = False
    day_start = False
    user_existence_flag = False
    #if balance[-1]['date'] != tomorrow:
    #    balance = balance[-6:]
    #    mess_tommorow = '\n<em><b>На завтра нет данных!</b></em>'
    #else:
    #    balance = balance[-9:]
    for info in balance:
        if 'tec' in info.keys():
            if info['date'] == yesterday or info['date'] == today or info['date'] == tomorrow and info['tec'] == 'start':
                if info['date'] == tomorrow:
                    tomorrow_flag = True
                day_start = True
                mess += f'\n<b>Дата: {info["date"]}</b>\n'
            elif info['tec'] == 'end':
                day_start = False
        if day_start == True and info['date'] != '':
            mess += f'<b><em>{info["AccTypeTO"]}</em></b>\n' \
                    f'<em>Валюта:</em> {info["currency"]}\n' \
                    f'<em>Сумма поступлений:</em> {info["inflow"]}\n' \
                    f'<em>Сумма выбытий:</em> {info["outflow"]}\n' \
                    f'<em>Cумма на конец:</em> {info["closing balance"]}\n' \
                    f'<em>Статус:</em> {info["CurrStatus"]}\n' \
                    f'<em>Куратор:</em> {info["Dealer"]}\n\n' 
    if not tomorrow_flag:
        mess_tommorow = '\n<em><b>На завтра нет данных!</b></em>'
    mess += mess_tommorow
    return mess

