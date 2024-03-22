import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import json
import time
from datetime import datetime, timedelta
import re
DEFAULT_LANGUAGE = "RU"


def write_feedback(date_time, tel_id, tel_nick, tel_name, client_feedback):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

    spreadsheetId = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'  # сохраняем идентификатор файла

    # Ищем последнюю строку
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                               range='Обратная связь!A2:100000').execute().get('values', [])
    last_row = rows[-1] if rows else None
    last_row_id = len(rows) + 2

    headers_inds = {header: ind for ind, header in enumerate(rows[0])}
    headers_vars = {
        'string_number': last_row_id,
        'date_time': date_time,
        'tel_id': tel_id,
        'tel_name': tel_name,
        'operator_fio': '',
        'operator_comment': '',
        'tel_nick': tel_nick,
        'client_feedback': client_feedback
    }

    new_dict = {headers_vars[header]: ind for header, ind in headers_inds.items()}
    new_row = list(dict(sorted(new_dict.items(), key=lambda item: item[1])).keys())
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
        "valueInputOption": "USER_ENTERED",
        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        "data": [
            {"range": f"Обратная связь!A{last_row_id}:100000",
             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
             "values": [
                 new_row  # Заполняем первую строку
             ]}
        ]
    }).execute()


def write_contact(TG_Contact, user_ID, NameSurname, AccTypeFROM, CurrFROM, City, ContactType, ContactDealer, CurrStatus,
                  Discount_Number, Referral_Number):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

    spreadsheetId = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'  # сохраняем идентификатор файла

    # Ищем последнюю строку
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                               range='Контакты!A2:AO1000000').execute().get('values', [])
    last_row = rows[-1] if rows else None
    last_row_id = len(rows) + 1
    print(last_row_id, last_row)
    headers_inds = {header: ind for ind, header in enumerate(rows[0])}
    print(headers_inds)
    headers_vars = {
        'TG_Contact': TG_Contact,
        'user_ID': user_ID,
        'NameSurname': NameSurname,
        'AccTypeFROM': AccTypeFROM,
        'CurrFROM': CurrFROM,
        'Sex': '-',
        'REGION': 'ME',
        'City': City,
        'ContactType': ContactType,
        'ContactDealer': ContactDealer,
        'CurrStatus': CurrStatus,
        'ContactOwnerTG':'NEW',
        'ContactOwnerID':'NEW',
        'ContactOwnerFIO':'NEW',
        'Discount_Number': Discount_Number,
        'Referral_Number': Referral_Number,
        'DiscTurnoverUSDT': f'''=СУММЕСЛИМН('Сделки'!K:K;'Сделки'!P:P;'Контакты'!O{last_row_id+1};'Сделки'!L:L;"USDT";'Сделки'!N:N;"Выполнена")''',
        'DiscTurnover3MUSDT': f'''=СУММЕСЛИМН('Сделки'!K:K;'Сделки'!P:P;'Контакты'!O{last_row_id+1};'Сделки'!L:L;"USDT";'Сделки'!N:N;"Выполнена";'Сделки'!B:B;">"&СЕГОДНЯ()-90)''',
        'DiscTurnoverRUB': f'''=СУММЕСЛИМН('Сделки'!K:K;'Сделки'!P:P;'Контакты'!O{last_row_id+1};'Сделки'!L:L;"RUB";'Сделки'!N:N;"Выполнена")''',
        'DiscTurnover3MRUB': f'''=СУММЕСЛИМН('Сделки'!K:K;'Сделки'!P:P;'Контакты'!O{last_row_id+1};'Сделки'!L:L;"RUB";'Сделки'!N:N;"Выполнена";'Сделки'!B:B;">"&СЕГОДНЯ()-90)''',
        'Discount': f'=МАКС(W{last_row_id+1};X{last_row_id+1})',
        'DiscClientCategory': f'''=ЕСЛИ(ВПР(U{last_row_id+1};'СтавкиРеферал'!H:I;2;ЛОЖЬ)=0;"Базовый";ВПР(U{last_row_id+1};'СтавкиРеферал'!H:I;2;ЛОЖЬ))''',
        'DiscClientCategoryUSDT': f'''=МАКС(ЕСЛИ(И(I{last_row_id+1}="Клиент";K{last_row_id+1}="Активный");ЕСЛИ(Q{last_row_id+1}>='СтавкиРеферал'!$D$5;'СтавкиРеферал'!$H$5;ЕСЛИ('Контакты'!Q{last_row_id+1}>='СтавкиРеферал'!$D$4;'СтавкиРеферал'!$H$4;ЕСЛИ('Контакты'!Q{last_row_id+1}>='СтавкиРеферал'!$D$3;'СтавкиРеферал'!$H$3;0))));ЕСЛИ(И(I{last_row_id+1}="Клиент";K{last_row_id+1}="Активный");ЕСЛИ(R{last_row_id+1}>='СтавкиРеферал'!$E$5;'СтавкиРеферал'!$H$5;ЕСЛИ('Контакты'!R{last_row_id+1}>='СтавкиРеферал'!$E$4;'СтавкиРеферал'!$H$4;ЕСЛИ('Контакты'!R{last_row_id+1}>='СтавкиРеферал'!$E$3;'СтавкиРеферал'!$H$3;0)))))''',
        'DiscClientCategoryRUB': f'''=МАКС(ЕСЛИ(И(I{last_row_id+1}="Клиент";K{last_row_id+1}="Активный");ЕСЛИ(S{last_row_id+1}>='СтавкиРеферал'!$F$5;'СтавкиРеферал'!$H$5;ЕСЛИ('Контакты'!S{last_row_id+1}>='СтавкиРеферал'!$F$4;'СтавкиРеферал'!$H$4;ЕСЛИ('Контакты'!S{last_row_id+1}>='СтавкиРеферал'!$F$3;'СтавкиРеферал'!$H$3;0))));ЕСЛИ(И(I{last_row_id+1}="Клиент";K{last_row_id+1}="Активный");ЕСЛИ(T{last_row_id+1}>='СтавкиРеферал'!$G$5;'СтавкиРеферал'!$H$5;ЕСЛИ('Контакты'!T{last_row_id+1}>='СтавкиРеферал'!$G$4;'СтавкиРеферал'!$H$4;ЕСЛИ('Контакты'!T{last_row_id+1}>='СтавкиРеферал'!$G$3;'СтавкиРеферал'!$H$3;0)))))''',
        'ReferalTurnoverUSDT': f'''=СУММЕСЛИМН('Сделки'!K:K;'Сделки'!P:P;'Контакты'!P{last_row_id+1};'Сделки'!L:L;"USDT";'Сделки'!N:N;"Выполнена")''',
        'ReferalTurnover3MUSDT': f'''=СУММЕСЛИМН('Сделки'!K:K;'Сделки'!P:P;'Контакты'!P{last_row_id+1};'Сделки'!L:L;"USDT";'Сделки'!N:N;"Выполнена";'Сделки'!B:B;">"&СЕГОДНЯ()-90)''',
        'ReferalTurnover30DUSDT':f'''=СУММЕСЛИМН('Сделки'!K:K;'Сделки'!P:P;'Контакты'!P{last_row_id+1};'Сделки'!L:L;"USDT";'Сделки'!N:N;"Выполнена";'Сделки'!B:B;">"&СЕГОДНЯ()-30)''' ,
        'ReferalTurnoverRUB': f'''=СУММЕСЛИМН('Сделки'!K:K;'Сделки'!P:P;'Контакты'!P{last_row_id+1};'Сделки'!L:L;"RUB";'Сделки'!N:N;"Выполнена")''',
        'ReferalTurnover3MRUB': f'''=СУММЕСЛИМН('Сделки'!K:K;'Сделки'!P:P;'Контакты'!P{last_row_id+1};'Сделки'!L:L;"RUB";'Сделки'!N:N;"Выполнена";'Сделки'!B:B;">"&СЕГОДНЯ()-90)''',
        'ReferalTurnover30DRUB':f'''=СУММЕСЛИМН('Сделки'!K:K;'Сделки'!P:P;'Контакты'!P{last_row_id+1};'Сделки'!L:L;"RUB";'Сделки'!N:N;"Выполнена";'Сделки'!B:B;">"&СЕГОДНЯ()-30)''',
        'ReferalBenefitEUR':f'''=СУММЕСЛИМН('Сделки'!AA:AA;'Сделки'!N:N;"РасчБонВыполнена";'Сделки'!D:D;A{last_row_id+1})''',
        'ReferalBenefit3MEUR':f'''=СУММЕСЛИМН('Сделки'!AA:AA;'Сделки'!N:N;"РасчБонВыполнена";'Сделки'!D:D;A{last_row_id+1};'Сделки'!B:B;">"&СЕГОДНЯ()-90)''',
        'ReferalBenefit30DEUR':f'''=СУММЕСЛИМН('Сделки'!AA:AA;'Сделки'!N:N;"РасчБонВыполнена";'Сделки'!D:D;A{last_row_id+1};'Сделки'!B:B;">"&СЕГОДНЯ()-30)''',
        'ReferalPayoutEUR':f'''=СУММЕСЛИМН('Сделки'!G:G;'Сделки'!D:D;A{last_row_id+1};'Сделки'!H:H;"EUR";'Сделки'!N:N;"Выполнена";'Сделки'!E:E;"Выплата бонусов")''',
        'ReferalPayout3MEUR':f'''=СУММЕСЛИМН('Сделки'!G:G;'Сделки'!D:D;A{last_row_id+1};'Сделки'!H:H;"EUR";'Сделки'!N:N;"Выполнена";'Сделки'!E:E;"Выплата бонусов";'Сделки'!B:B;">"&СЕГОДНЯ()-90)''',
        'ReferalPayout30DEUR':f'''=СУММЕСЛИМН('Сделки'!G:G;'Сделки'!D:D;A{last_row_id+1};'Сделки'!H:H;"EUR";'Сделки'!N:N;"Выполнена";'Сделки'!E:E;"Выплата бонусов";'Сделки'!B:B;">"&СЕГОДНЯ()-30)''',
        'TurnoverQty': f'''=СЧЁТЕСЛИМН('Сделки'!D:D;'Контакты'!A{last_row_id+1};'Сделки'!N:N;"РасчБонВыполнена")''',
        'Turnover3MQty': f'''=СЧЁТЕСЛИМН('Сделки'!D:D;'Контакты'!A{last_row_id+1};'Сделки'!N:N;"РасчБонВыполнена";'Сделки'!B:B;">"&СЕГОДНЯ()-90)''',
        'Turnover30DQty':f'''=СЧЁТЕСЛИМН('Сделки'!D:D;'Контакты'!A{last_row_id+1};'Сделки'!N:N;"РасчБонВыполнена";'Сделки'!B:B;">"&СЕГОДНЯ()-30)''',
        'RefClientCategoryUSDT': f'''=МАКС(ЕСЛИ(И(I{last_row_id+1}="Клиент";K{last_row_id+1}="Активный");ЕСЛИ(Y{last_row_id+1}>='СтавкиРеферал'!$D$5;'СтавкиРеферал'!$H$5;ЕСЛИ('Контакты'!Y{last_row_id+1}>='СтавкиРеферал'!$D$4;'СтавкиРеферал'!$H$4;ЕСЛИ('Контакты'!Y{last_row_id+1}>='СтавкиРеферал'!$D$3;'СтавкиРеферал'!$H$3;0))));ЕСЛИ(И(I{last_row_id+1}="Клиент";K{last_row_id+1}="Активный");ЕСЛИ(Z{last_row_id+1}>='СтавкиРеферал'!$E$5;'СтавкиРеферал'!$H$5;ЕСЛИ('Контакты'!Z{last_row_id+1}>='СтавкиРеферал'!$E$4;'СтавкиРеферал'!$H$4;ЕСЛИ('Контакты'!Z{last_row_id+1}>='СтавкиРеферал'!$E$3;'СтавкиРеферал'!$H$3;0)))))''',
        'RefClientCategoryRUB': f'''=МАКС(ЕСЛИ(И(I{last_row_id+1}="Клиент";K{last_row_id+1}="Активный");ЕСЛИ(AB{last_row_id+1}>='СтавкиРеферал'!$F$5;'СтавкиРеферал'!$H$5;ЕСЛИ('Контакты'!AB{last_row_id+1}>='СтавкиРеферал'!$F$4;'СтавкиРеферал'!$H$4;ЕСЛИ('Контакты'!AB{last_row_id+1}>='СтавкиРеферал'!$F$3;'СтавкиРеферал'!$H$3;0))));ЕСЛИ(И(I{last_row_id+1}="Клиент";K{last_row_id+1}="Активный");ЕСЛИ(AC{last_row_id+1}>='СтавкиРеферал'!$G$5;'СтавкиРеферал'!$H$5;ЕСЛИ('Контакты'!AC{last_row_id+1}>='СтавкиРеферал'!$G$4;'СтавкиРеферал'!$H$4;ЕСЛИ('Контакты'!AC{last_row_id+1}>='СтавкиРеферал'!$G$3;'СтавкиРеферал'!$H$3;0)))))'''
    }
    new_dict = {ind: headers_vars[header] for header, ind in headers_inds.items()}
    new_row = list(dict(sorted(new_dict.items(), key=lambda item: item[0])).values())
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
        "valueInputOption": "USER_ENTERED",
        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        "data": [
            {"range": f"Контакты!A{last_row_id + 1}:100000",
             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
             "values": [
                 new_row,  # Заполняем первую строку
             ]}
        ]
    }).execute()
    scrab_contact_list()

def scrab_deals_list():
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Сделки!2:100000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    tgnicks_data = {one_doc['TG_Contact']: one_doc for one_doc in sheet_data if 'TG_Contact' in one_doc}
    return tgnicks_data

def update_contact(username, city, acc_type_from, curr_from, rows, service, spreadsheetId, users):
    # Читаем ключи из файла
    for row_index, user in enumerate(users):
        if 'TG_Contact' in user.keys() and 'City' in user.keys() and 'AccTypeFROM' in user.keys() and 'CurrFROM' in user.keys():
            if user['TG_Contact'] == str(username) and (user['City'] != city or user['AccTypeFROM'] != acc_type_from or user['CurrFROM'] != curr_from):
                results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                    "valueInputOption": "USER_ENTERED",
                    # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                    "data": [
                        {"range": f"Контакты!H{row_index + 3}:100000",
                         "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                         "values": [
                             [city]  # Заполняем первую строку
                         ]},
                        {"range": f"Контакты!D{row_index + 3}:100000",
                         "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                         "values": [
                             [acc_type_from, curr_from]  # Заполняем первую строку
                         ]}
                    ]
                }).execute()
                time.sleep(0.5)
    last_row = rows[-1] if rows else None
    last_row_id = len(rows) + 1

def write_update_contacts():
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'
    contacts_info = scrab_deals_list()
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

    spreadsheetId = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'  # сохраняем идентификатор файла
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                               range='Контакты!A2:AK1000000').execute().get('values', [])
    headers = rows.pop(0)
    users = [dict(zip(headers, one_row)) for one_row in rows]
    for contact in contacts_info:
        if 'City' in contacts_info[contact] and 'FINOFFICETO' in contacts_info[contact] and 'receiveCurrencyName' in contacts_info[contact]:
            update_contact(contact, contacts_info[contact]['City'], contacts_info[contact]['FINOFFICETO'], contacts_info[contact]['receiveCurrencyName'], rows, service, spreadsheetId, users)
def scrab_contact_list():
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Контакты!2:1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    tgnicks_data = {one_doc['TG_Contact']: one_doc for one_doc in sheet_data if 'ContactType' in one_doc and one_doc['ContactType'] in ['Клиент','Партнер','Куратор', 'Обменник']}
    with open('contacts.json', 'w', encoding='utf8') as f:
        json.dump(tgnicks_data, f, ensure_ascii=False, indent=2)
    return tgnicks_data

def add_row(DealID, DateID, createDateTime, dealer, RefHolder, exchangeId, OPERTYPE, sendCurrencyName, sendAmount, FINOFFICEFROM, \
            accountFROM, ExchRate_FROM_TO_Plan, receiveAmount, receiveCurrencyName, FINOFFICETO, accountTO, tg_Contact,
            reference_Number_FROM, \
            city, commission, profit_TOT_Percent, profit_TOT_EUR, profit_ADMIN_EUR, profit_PARTNER_EUR, \
            profit_DEALER_EUR, profit_P2P_EUR, CurrStatus, Profit_Referral_EUR, comment, operation, curr_commission, usdteur, ExchRateUSDTEUR, ExchRateEURUSDT):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

    spreadsheetId = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'  # сохраняем идентификатор файла

    # Ищем последнюю строку
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                               range='Сделки!A2:AM100000').execute().get('values', [])
    last_row = rows[-1] if rows else None
    last_row_id = len(rows)

    print(last_row_id, last_row)
    headers_inds = {header: ind for ind, header in enumerate(rows[0])}
    print(headers_inds)
    if ExchRate_FROM_TO_Plan == '':
        ExchRate_FROM_TO_Plan = f'=I{last_row_id + 2}{receiveAmount}O{last_row_id + 2}'
    if operation == 'admin' or operation == 'rubeur':
        receiveAm = sendAmount
        sendAm = f'=O{last_row_id + 2}{receiveAmount}M{last_row_id + 2}'
    elif operation == 'rubeur2':
        receiveAm = f'=O{last_row_id + 1}'
        sendAm = f'=I{last_row_id + 1}{receiveAmount}M{last_row_id + 2}'
    elif operation == 'eurrub2':
        receiveAm = f'=I{last_row_id + 1}'
        sendAm = f'=O{last_row_id + 2}{receiveAmount}M{last_row_id + 2}'
    elif operation == 'rubeur3':
        receiveAm = f'=O{last_row_id}'
        sendAm = f'=I{last_row_id}{receiveAmount}M{last_row_id + 2}'
    elif operation == 'rubeur4':
        receiveAm = f'=O{last_row_id}'
        sendAm = f'=I{last_row_id+1}'
    elif operation == 'eurrub3':
        receiveAm = f'=O{last_row_id}'
        sendAm = f'=I{last_row_id + 1}/M{last_row_id + 2}'
    elif operation == 'Расходы':
        receiveAm = ''
        sendAm = sendAmount
    elif operation == 'Трансфер денег':
        receiveAm = sendAmount
        sendAm = sendAmount
    else:
        receiveAm = f'=I{last_row_id + 2}{receiveAmount}M{last_row_id + 2}'
        sendAm = sendAmount
    if sendAmount == '' and operation != 'admin' and operation != 'admin2':
        sendAm = f'=O{last_row_id + 1}'
    elif sendAmount == '' and operation == 'admin' and OPERTYPE == 'USDT=>EUR':
        sendAm = f'=I{last_row_id + 1}*M{last_row_id + 2}'
        receiveAm = receiveAmount
    elif sendAmount == '' and operation == 'admin' and OPERTYPE == 'USDT=>RSD':
        sendAm = f'=I{last_row_id + 1}/M{last_row_id + 2}'
        receiveAm = receiveAmount
    elif sendAmount == '' and operation == 'admin2' and OPERTYPE == 'USDT=>EUR':
        sendAm = f'=I{last_row_id}*M{last_row_id + 2}'
        receiveAm = receiveAmount
    elif sendAmount == '' and operation == 'admin2' and OPERTYPE == 'USDT=>RSD':
        sendAm = f'=I{last_row_id}/M{last_row_id + 2}'
        receiveAm = receiveAmount
    elif sendAmount == 'rubkzt4':
        pass
    if commission == 'VPR' and (exchangeId == 'RUB=>EUR' or exchangeId == 'RUB=>BGN' or exchangeId == 'RUB=>RSD'):
        commission = f"=ВПР(T{last_row_id};'Контакты'!A:L;12;ЛОЖЬ)"
    elif commission == 'VPR' and exchangeId == 'RUB=>KZT':
        commission = f"=ВПР(T{last_row_id-1};'Контакты'!A:L;12;ЛОЖЬ)"
    elif commission == 'VPR' and (exchangeId == 'USDT=>RSD' or exchangeId == 'USDT=>EUR' or exchangeId == 'USDT=>BGN' or exchangeId == 'USDT=>UAH' or exchangeId == 'USDT=>KZT'):
        commission = f"=ВПР(T{last_row_id+1};'Контакты'!A:L;12;ЛОЖЬ)"
    if curr_commission == 'VPR in 2':
        curr_commission = f"=ВПР(T{last_row_id+1};'Контакты'!A:M;13;ЛОЖЬ)"
    elif curr_commission == 'VPR in 3':
        curr_commission = f"=ВПР(T{last_row_id};'Контакты'!A:M;13;ЛОЖЬ)"
    elif curr_commission == 'VPR in 4':
        curr_commission = f"=ВПР(T{last_row_id-1};'Контакты'!A:M;13;ЛОЖЬ)"
    else:
        curr_commission = ''
    ExchRate_FROM_TO_Fact = ''
    if exchangeId == 'RUB=>EUR' and OPERTYPE == 'EUR=>RUB' or exchangeId == 'EUR=>RUB' and sendCurrencyName in ['USDT'] or\
        exchangeId == 'USDT=>UAH' and receiveCurrencyName == 'UAH' or exchangeId == 'USDT=>RUB' and receiveCurrencyName == 'RUB' or\
            exchangeId == 'EUR=>RUB' and sendCurrencyName == 'USDT':
        ExchRate_FROM_TO_Fact = f"=O{last_row_id + 2}/I{last_row_id + 2}"
    elif exchangeId == 'RUB=>EUR' and OPERTYPE == 'RUB=>USDT' or exchangeId == 'USDT=>EUR' and sendCurrencyName == 'EUR' or \
        exchangeId == 'USDT=>UAH' and sendCurrencyName == 'UAH' or exchangeId == 'USDT=>RUB' and sendCurrencyName == 'RUB' \
            or exchangeId == 'EUR=>RUB' and sendCurrencyName == 'RUB':
        ExchRate_FROM_TO_Fact = f"=I{last_row_id + 2}/O{last_row_id + 2}"
    if usdteur == True:
        inUSDT = f'=AK{last_row_id+2}/AL{last_row_id+2}'
        if exchangeId in ['USDT=>EUR', 'RUB=>EUR', 'Расходы', 'Трансфер денег']:
            inEUR = f'=I{last_row_id+2}'
        else:
            inEUR = f'=O{last_row_id+2}'
    else:
        inUSDT, inEUR = '', ''
    createdAt = datetime.now().timestamp()
    headers_vars = {
        'DateID': DateID,
        'createdAt': createdAt,
        'CreateDateTime': createDateTime,
        'DealID': DealID,
        'Dealer': dealer,
        'RefHolder': RefHolder,
        'exchangeId': exchangeId,
        'OPERTYPE': OPERTYPE,
        'sendAmount': sendAm,
        'sendCurrencyName': sendCurrencyName,
        'FINOFFICEFROM': FINOFFICEFROM,
        'AccountFROM': accountFROM,
        'ExchRate_FROM_TO_Plan': ExchRate_FROM_TO_Plan,
        'ExchRate_FROM_TO_Fact': ExchRate_FROM_TO_Fact,
        'receiveAmount': receiveAm,
        'receiveCurrencyName': receiveCurrencyName,
        'FINOFFICETO': FINOFFICETO,
        'AccountTO': accountTO,
        'CurrStatus': CurrStatus,
        'TG_Contact': tg_Contact,
        'Reference_Number_FROM': reference_Number_FROM,
        'City': city,
        'ACCOUNT_Dt': '',
        'ACCOUNT_Ct': '',
        'Commission': commission,
        'CurrCommission': curr_commission,
        'AccTypeCommission': 'Alpha_TG_Bot',
        'Profit_TOT_Percent': profit_TOT_Percent,
        'Profit_TOT_EUR': profit_TOT_EUR,
        'Profit_ADMIN_EUR': profit_ADMIN_EUR,
        'Profit_PARTNER_EUR': profit_PARTNER_EUR,
        'Profit_DEALER_EUR': profit_DEALER_EUR,
        'Profit_P2P_EUR': profit_P2P_EUR,
        'Profit_Referral_EUR': Profit_Referral_EUR,
        'Comment': comment,
        'inUSDT': inUSDT,
        'inEUR': inEUR,
        'ExchRateUSDTEUR': ExchRateUSDTEUR,
        'ExchRateEURUSDT': ExchRateEURUSDT
    }

    new_dict = {ind: headers_vars[header] for header, ind in headers_inds.items()}
    new_row = list(dict(sorted(new_dict.items(), key=lambda item: item[0])).values())

    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
        "valueInputOption": "USER_ENTERED",
        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        "data": [
            {"range": f"Сделки!A{last_row_id + 2}:100000",
             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
             "values": [
                 new_row,  # Заполняем первую строку
             ]}
        ]
    }).execute()

    results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
        "requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": 804296252,
                    "startRowIndex": last_row_id + 1,
                    "endRowIndex": last_row_id + 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "NUMBER",
                            "pattern": "0"
                        }
                    },
                },
                "fields": 'userEnteredFormat.numberFormat'
            }
        }]
    }).execute()

    results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
        "requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": 804296252,
                    "startRowIndex": last_row_id + 1,
                    "endRowIndex": last_row_id + 2,
                    "startColumnIndex": 2,
                    "endColumnIndex": 8
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 221 / 256,
                            "green": 234 / 256,
                            "blue": 212 / 256
                        }
                    },
                },
                "fields": 'userEnteredFormat.backgroundColor'
            }
        }]
    }).execute()

    results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
        "requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": 804296252,
                    "startRowIndex": last_row_id + 1,
                    "endRowIndex": last_row_id + 2,
                    "startColumnIndex": 12,
                    "endColumnIndex": 14
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 221 / 256,
                            "green": 234 / 256,
                            "blue": 212 / 256
                        }
                    },
                },
                "fields": 'userEnteredFormat.backgroundColor'
            }
        }]
    }).execute()

    results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
        "requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": 804296252,
                    "startRowIndex": last_row_id + 1,
                    "endRowIndex": last_row_id + 2,
                    "startColumnIndex": 17,
                    "endColumnIndex": 18
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 255 / 256,
                            "green": 235 / 256,
                            "blue": 156 / 256
                        }
                    },
                },
                "fields": 'userEnteredFormat.backgroundColor'
            }
        }]
    }).execute()

    results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
        "requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": 804296252,
                    "startRowIndex": last_row_id + 1,
                    "endRowIndex": last_row_id + 2,
                    "startColumnIndex": 19,
                    "endColumnIndex": 25
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 221 / 256,
                            "green": 234 / 256,
                            "blue": 212 / 256
                        }
                    },
                },
                "fields": 'userEnteredFormat.backgroundColor'
            }
        }]
    }).execute()


def calculate_indexes(deal_type, partner_flag, eur_rate):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

    spreadsheetId = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'  # сохраняем идентификатор файла

    # Ищем последнюю строку
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                               range='Сделки!B2:AI100000').execute().get('values', [])
    last_row = rows[-1] if rows else None
    last_row_id = len(rows) + 1

    if deal_type == 'RE' and partner_flag == False:
        ProfitTOT_Percent = f'=(1-(I{last_row_id - 2}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,1'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,4'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,4'
        Profit_P2P_EUR = f'=AC{last_row_id}*0,1'
        Profit_Referral_EUR = ''
    elif deal_type == 'RE' and partner_flag == True:
        ProfitTOT_Percent = f'=(1-(I{last_row_id - 2}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,15'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,2'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,25'
        Profit_P2P_EUR = f'=AC{last_row_id}*0,1'
        Profit_Referral_EUR = f'=AC{last_row_id}*0,3'
    elif deal_type == 'RK' and partner_flag == False:
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100/{str(eur_rate).replace(".",",")}'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,1'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,4'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,4'
        Profit_P2P_EUR = f'=AC{last_row_id}*0,1'
        Profit_Referral_EUR = ''
    elif deal_type == 'RK' and partner_flag == True:
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100/'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100/{str(eur_rate).replace(".",",")}'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,15'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,2'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,25'
        Profit_P2P_EUR = f'=AC{last_row_id}*0,1'
        Profit_Referral_EUR = f'=AC{last_row_id}*0,3'
    elif deal_type == 'ER' and partner_flag == False:
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,1'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,4'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,4'
        Profit_P2P_EUR = f'=AC{last_row_id}*0,1'
        Profit_Referral_EUR = ''
    elif deal_type == 'ER' and partner_flag == True:
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,15'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,2'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,25'
        Profit_P2P_EUR = f'=AC{last_row_id}*0,1'
        Profit_Referral_EUR = f'=AC{last_row_id}*0,3'
    elif deal_type == 'UE' and partner_flag == False:
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100*{str(eur_rate).replace(".",",")}'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,1'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,5'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,4'
        Profit_P2P_EUR = f'=AC{last_row_id}*0'
        Profit_Referral_EUR = ''
    elif deal_type == 'UE' and partner_flag == True:
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100*{str(eur_rate).replace(".",",")}'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,2'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,2'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,2'
        Profit_P2P_EUR = f'=AC{last_row_id}*0,1'
        Profit_Referral_EUR = f'=AC{last_row_id}*0,3'
    elif deal_type == 'EU' and partner_flag == False:
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100*{str(eur_rate).replace(".",",")}'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,1'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,5'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,4'
        Profit_P2P_EUR = f'=AC{last_row_id}*0'
        Profit_Referral_EUR = ''
    elif deal_type == 'EU' and partner_flag == True:
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100*{str(eur_rate).replace(".",",")}'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,2'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,2'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,2'
        Profit_P2P_EUR = f'=AC{last_row_id}*0,1'
        Profit_Referral_EUR = f'=AC{last_row_id}*0,3'
    elif deal_type == 'UU' and partner_flag == False:
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100*{str(eur_rate).replace(".",",")}'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,1'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,5'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,4'
        Profit_P2P_EUR = f'=AC{last_row_id}*0'
        Profit_Referral_EUR = ''
    elif deal_type == 'UU' and partner_flag == True:
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100*{str(eur_rate).replace(".",",")}'
        Profit_ADMIN_EUR = f'=AC{last_row_id}*0,2'
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,2'
        Profit_DEALER_EUR = f'=AC{last_row_id}*0,2'
        Profit_P2P_EUR = f'=AC{last_row_id}*0,1'
        Profit_Referral_EUR = f'=AC{last_row_id}*0,3'
    elif deal_type == 'Откуп':
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100'
        Profit_ADMIN_EUR = ''
        Profit_PARTNER_EUR = f'=AC{last_row_id}*1'
        Profit_DEALER_EUR = ''
        Profit_P2P_EUR = ''
        Profit_Referral_EUR = ''
    elif deal_type == 'Снятие с карт':
        ProfitTOT_Percent = f'=(1-(I{last_row_id}/O{last_row_id}))*100'
        Profit_TOT_EUR = f'=O{last_row_id}*AB{last_row_id}/100'
        Profit_ADMIN_EUR = ''
        Profit_PARTNER_EUR = f'=AC{last_row_id}*0,5'
        Profit_DEALER_EUR = ''
        Profit_P2P_EUR = f'=AC{last_row_id}*0,5'
        Profit_Referral_EUR = ''
    headers_vars = {
        'Profit_TOT_Percent': ProfitTOT_Percent,
        'Profit_TOT_EUR': Profit_TOT_EUR,
        'Profit_ADMIN_EUR': Profit_ADMIN_EUR,
        'Profit_PARTNER_EUR': Profit_PARTNER_EUR,
        'Profit_DEALER_EUR': Profit_DEALER_EUR,
        'Profit_P2P_EUR': Profit_P2P_EUR,
        'Profit_Referral_EUR': Profit_Referral_EUR
    }

    print(last_row_id, last_row)
    work_headers = ['Profit_TOT_Percent', 'Profit_TOT_EUR', 'Profit_ADMIN_EUR', 'Profit_PARTNER_EUR',
                    'Profit_DEALER_EUR', 'Profit_P2P_EUR', 'Profit_Referral_EUR']
    headers_inds = {header: ind for ind, header in enumerate(rows[0]) if header in work_headers}
    print(headers_inds)

    new_dict = {ind: headers_vars[header] for header, ind in headers_inds.items()}
    new_row = list(dict(sorted(new_dict.items(), key=lambda item: item[0])).values())

    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
        "valueInputOption": "USER_ENTERED",
        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        "data": [
            {"range": f"Сделки!AB{last_row_id}:100000",
             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
             "values": [
                 new_row,  # Заполняем первую строку
             ]}
        ]
    }).execute()
    

def add_border():
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

    spreadsheetId = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'  # сохраняем идентификатор файла

    # Ищем последнюю строку
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                               range='Сделки!B2:100000').execute().get('values', [])
    last_row_id = len(rows)

    results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
        "requests": [
            {
                "updateBorders": {
                    "range": {
                        "sheetId": 804296252,
                        "startRowIndex": last_row_id,
                        "endRowIndex": last_row_id + 1,
                        "startColumnIndex": 1,
                        "endColumnIndex": 35
                    },
                    "bottom": {
                        "style": "DOUBLE",
                        "width": 1,
                    },
                    # "innerHorizontal": {
                    #    "style": "DOUBLE",
                    #    "width": 1,
                    # },
                }
            }]
    }).execute()


def write_pending_order(createDateTime=None, dealer=None, dealType=None, exchFROM_Amount=None, orderRate=None, user_ID=None,
                        tg_Contact=None,
                        city=None, currStatus=None, chat_ID=None, ):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

    spreadsheetId = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'  # сохраняем идентификатор файла

    # Ищем последнюю строку
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                               range='Отложенные ордеры!C2:100000').execute().get('values', [])
    last_row = rows[-1] if rows else None
    last_row_id = len(rows)

    print(last_row_id, last_row)
    headers_inds = {header: ind for ind, header in enumerate(rows[0])}
    print(headers_inds)
    headers_vars = {
        'CreateDateTime': createDateTime,
        'Dealer': dealer,
        'DealType': dealType,
        'ExchFROM_Amount': exchFROM_Amount,
        'OrderRate': orderRate,
        'City': city,
        'CurrStatus': currStatus,
        'user_ID': user_ID,
        'TG_Contact': tg_Contact,
        'Chat_ID': chat_ID
    }

    new_dict = {ind: headers_vars[header] for header, ind in headers_inds.items()}
    new_row = list(dict(sorted(new_dict.items(), key=lambda item: item[0])).values())

    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
        "valueInputOption": "USER_ENTERED",
        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        "data": [
            {"range": f"Отложенные ордеры!C{last_row_id + 2}:100000",
             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
             "values": [
                 new_row,  # Заполняем первую строку
             ]}
        ]
    }).execute()


def log_action(date_time, user_name, user_id, user_fio, action, comment):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

    spreadsheetId = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'  # сохраняем идентификатор файла

    # Ищем последнюю строку
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                               range='LogAction!A2:100000').execute().get('values', [])
    last_row = rows[-1] if rows else None
    last_row_id = len(rows) + 2

    headers_inds = {header: ind for ind, header in enumerate(rows[0])}
    headers_vars = {
        'string_number': last_row_id,
        'date_time': date_time,
        'bot_name': 'Alpha_TG_Bot',
        'user_name': user_name,
        'user_id': user_id,
        'user_fio': user_fio,
        'action': action,
        'comment': comment
    }

    new_dict = {headers_vars[header]: ind for header, ind in headers_inds.items()}
    new_row = list(dict(sorted(new_dict.items(), key=lambda item: item[1])).keys())
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
        "valueInputOption": "USER_ENTERED",
        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        "data": [
            {"range": f"LogAction!A{last_row_id}:100000",
             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
             "values": [
                 new_row  # Заполняем первую строку
             ]}
        ]
    }).execute()


def write_language(user_id, language):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Контакты!2:1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    users = [dict(zip(headers, one_row)) for one_row in rows]
    for row_index, user in enumerate(users):
        if 'TG_Contact' in user.keys() and 'user_ID' in user.keys():
            if user['TG_Contact'] == str(user_id) or user['user_ID'] == str(user_id):
                results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
                    "valueInputOption": "USER_ENTERED",
                    # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                    "data": [
                        {"range": f"Контакты!AR{row_index + 3}:100000",
                         "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                         "values": [
                             [language]  # Заполняем первую строку
                         ]}
                    ]
                }).execute()

def get_language(user_id):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Контакты!2:1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    users = [dict(zip(headers, one_row)) for one_row in rows]
    for row_index, user in enumerate(users):
        if 'user_ID' in user.keys() and str(user['user_ID']) == str(user_id):
            return user.get("Language", DEFAULT_LANGUAGE)
    return DEFAULT_LANGUAGE

def gs_write_usdrub_eurrub(USD_RUB, USD_UAH, USD_RSD, USD_KZT, EUR_RUB, EUR_UAH, EUR_KZT, EUR_RSD, EUR_USD, USD_EUR):
    past_kzt_usd, past_kzt_eur, past_uah_usd, past_uah_eur, past_rsd_usd, past_rsd_eur, past_rub_usd, past_rub_eur = 0,0,0,0,0,0,0,0
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
    rows = list(map(lambda row: list(map(lambda elem: elem.replace(u'\xa0', ''), row)), resp['values']))
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    balance = [one_doc for one_doc in sheet_data if 'date' in one_doc and len(one_doc['date']) == 10 and not re.findall(r'[a-zA-Z]', one_doc['date'])]
    tomorrow = str((datetime.now()+timedelta(days=1)).strftime('%d.%m.%Y'))
    today = str(datetime.now().strftime('%d.%m.%Y'))
    yesterday = str((datetime.now()-timedelta(days=1)).strftime('%d.%m.%Y'))
    for ind, row in enumerate(sheet_data):
        if 'date' in row.keys() and 'currency' in row.keys() and 'LOCAL/USD' in row.keys() and 'LOCAL/EUR' in row.keys() and 'USD/EUR' in row.keys() and 'EUR/USD' in row.keys():
            if  row['currency'] == 'RUB' and row['LOCAL/USD'] != '' and row['date'] == yesterday:
                past_rub_usd = float(row['LOCAL/USD'].replace(',','.'))
            elif  row['currency'] == 'KZT' and row['LOCAL/USD'] != '' and row['date'] == yesterday:
                past_kzt_usd = float(row['LOCAL/USD'].replace(',','.'))
            elif  row['currency'] == 'RSD' and row['LOCAL/USD'] != '' and row['date'] == yesterday:
                past_rsd_usd = float(row['LOCAL/USD'].replace(',','.'))
            elif  row['currency'] == 'UAH' and row['LOCAL/USD'] != '' and row['date'] == yesterday:
                past_uah_usd = float(row['LOCAL/USD'].replace(',','.'))
            if  row['currency'] == 'RUB' and row['LOCAL/EUR'] != '' and row['date'] == yesterday:
                past_rub_eur = float(row['LOCAL/EUR'].replace(',','.'))
            elif  row['currency'] == 'UAH' and row['LOCAL/EUR'] != '' and row['date'] == yesterday:
                past_uah_eur = float(row['LOCAL/EUR'].replace(',','.'))
            elif  row['currency'] == 'KZT' and row['LOCAL/EUR'] != '' and row['date'] == yesterday:
                past_kzt_eur = float(row['LOCAL/EUR'].replace(',','.'))
            elif  row['currency'] == 'RSD' and row['LOCAL/EUR'] != '' and row['date'] == yesterday:
                past_rsd_eur = float(row['LOCAL/EUR'].replace(',','.'))
            elif  row['currency'] == 'USDT' and row['USD/EUR'] != '' and row['date'] == yesterday:
                past_usd_eur = float(row['USD/EUR'].replace(',','.'))
            elif  row['currency'] == 'EUR' and row['EUR/USD'] != '' and row['date'] == yesterday:
                past_eur_usd = float(row['EUR/USD'].replace(',','.'))
            elif (row['date'] == tomorrow or row['date'] == today) and row['currency'] in ['RUB','UAH','KZT','RSD']:
                if row['currency'] == 'RUB':
                    locUSD, locEUR, past_cur_usd, past_cur_eur = USD_RUB, EUR_RUB, past_rub_usd, past_rub_eur
                elif row['currency'] == 'UAH':
                    locUSD, locEUR, past_cur_usd, past_cur_eur = USD_UAH, EUR_UAH, past_uah_usd, past_uah_eur
                elif row['currency'] == 'KZT':
                    locUSD, locEUR, past_cur_usd, past_cur_eur = USD_KZT, EUR_KZT, past_kzt_usd, past_kzt_eur
                elif row['currency'] == 'RSD':
                    locUSD, locEUR, past_cur_usd, past_cur_eur = USD_RSD, EUR_RSD, past_rsd_usd, past_rsd_eur
                results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
                    "valueInputOption": "USER_ENTERED",
                    # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                    "data": [
                        {"range": f"Баланс валют!G{ind+3}:100000",
                        "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                        "values": [
                            [locUSD, locEUR]  # Заполняем первую строку
                        ]}
                    ]
                }).execute()
                if locUSD < past_cur_usd:
                    red = 0
                    green = 1
                    blue = 0
                else:
                    red = 1
                    green = 0
                    blue = 0
                results = service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={
                    "requests": [{
                        "repeatCell": {
                            "range": {
                                "sheetId": 1144588440,
                                "startRowIndex": ind+2,
                                "endRowIndex": ind+3,
                                "startColumnIndex": 6,
                                "endColumnIndex": 7
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "backgroundColor": {
                                        "red": red,
                                        "green": green,
                                        "blue": blue
                                    }
                                },
                            },
                            "fields": 'userEnteredFormat.backgroundColor'
                        }
                    }]
                }).execute()
                if locEUR < past_cur_eur:
                    red = 0
                    green = 1
                    blue = 0
                else:
                    red = 1
                    green = 0
                    blue = 0
                results = service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={
                    "requests": [{
                        "repeatCell": {
                            "range": {
                                "sheetId": 1144588440,
                                "startRowIndex": ind+2,
                                "endRowIndex": ind+3,
                                "startColumnIndex": 7,
                                "endColumnIndex": 8
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "backgroundColor": {
                                        "red": red,
                                        "green": green,
                                        "blue": blue
                                    }
                                },
                            },
                            "fields": 'userEnteredFormat.backgroundColor'
                        }
                    }]
                }).execute()
                print(f'Курсы {row["currency"]}/USD, {row["currency"]}/EUR обновлены')
            elif (row['date'] == tomorrow or row['date'] == today) and row['currency'] == 'USDT':
                results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
                    "valueInputOption": "USER_ENTERED",
                    # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                    "data": [
                        {"range": f"Баланс валют!K{ind+3}:100000",
                        "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                        "values": [
                            [USD_EUR]  # Заполняем первую строку
                        ]}
                    ]
                }).execute()
                if USD_EUR > past_usd_eur:
                    red = 0
                    green = 1
                    blue = 0
                else:
                    red = 1
                    green = 0
                    blue = 0
                results = service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={
                    "requests": [{
                        "repeatCell": {
                            "range": {
                                "sheetId": 1144588440,
                                "startRowIndex": ind+2,
                                "endRowIndex": ind+3,
                                "startColumnIndex": 10,
                                "endColumnIndex": 11
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "backgroundColor": {
                                        "red": red,
                                        "green": green,
                                        "blue": blue
                                    }
                                },
                            },
                            "fields": 'userEnteredFormat.backgroundColor'
                        }
                    }]
                }).execute()
                print('Курс USD/EUR обновлен')
            elif (row['date'] == tomorrow or row['date'] == today) and row['currency'] == 'EUR':
                results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
                    "valueInputOption": "USER_ENTERED",
                    # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                    "data": [
                        {"range": f"Баланс валют!L{ind+3}:100000",
                        "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                        "values": [
                            [EUR_USD]  # Заполняем первую строку
                        ]}
                    ]
                }).execute()
                if EUR_USD > past_eur_usd:
                    red = 0
                    green = 1
                    blue = 0
                else:
                    red = 1
                    green = 0
                    blue = 0
                results = service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={
                    "requests": [{
                        "repeatCell": {
                            "range": {
                                "sheetId": 1144588440,
                                "startRowIndex": ind+2,
                                "endRowIndex": ind+3,
                                "startColumnIndex": 11,
                                "endColumnIndex": 12
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "backgroundColor": {
                                        "red": red,
                                        "green": green,
                                        "blue": blue
                                    }
                                },
                            },
                            "fields": 'userEnteredFormat.backgroundColor'
                        }
                    }]
                }).execute()
                print('Курс EUR/USD обновлен')

def get_city_commission(city_name, exch_sum, deal_type, currency):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="EP_DeposWithdr!2:100").execute()
    rows = resp['values']
    headers = rows.pop(0)
    exchangers = [dict(zip(headers, one_row)) for one_row in rows]
    commission = 100
    min_sum_exch = 1000000000
    for exchanger in exchangers:
        if 'ExchangePointCity' in exchanger.keys() and 'ExchangePointDealType' in exchanger.keys() and 'ExchangePointDealCur' in exchanger.keys():
            if exchanger['ExchangePointCity'] == str(city_name) and exchanger['ExchangePointDealType'] == str(deal_type) and exchanger['ExchangePointDealCur'] == str(currency):
                if exchanger['ExchangePointComission'] != '' or exchanger['ExchangePointComissionMin'] != '' or exchanger['ExchangePointComissionMax'] != '':
                    min_sum_exch = float(exchanger['ExchangePointDealCurMin'].replace(',','.')) if float(exchanger['ExchangePointDealCurMin'].replace(',','.')) < min_sum_exch else min_sum_exch
                if float(exchanger['ExchangePointDealCurMin'].replace(',','.')) <= exch_sum and float(exchanger['ExchangePointDealCurMax'].replace(',','.')) >= exch_sum:
                    if exchanger['ExchangePointComissionType'] == 'Fix' and exchanger['ExchangePointComission'] != '':
                        commission = float(exchanger['ExchangePointComission'].replace(',','.')) if float(exchanger['ExchangePointComission'].replace(',','.'))<commission else commission
                    elif exchanger['ExchangePointComissionType'] == 'Flex' and exchanger['ExchangePointComissionMin'] != '' and exchanger['ExchangePointComissionMax'] != '':
                        commission = (float(exchanger['ExchangePointComissionMin'].replace(',','.'))+float(exchanger['ExchangePointComissionMax'].replace(',','.')))/2 if (float(exchanger['ExchangePointComissionMin'].replace(',','.'))+float(exchanger['ExchangePointComissionMax'].replace(',','.')))/2<commission else commission
                    elif exchanger['ExchangePointComissionType'] == 'Flex' and exchanger['ExchangePointComissionMin'] == '' and exchanger['ExchangePointComissionMax'] != '':
                        commission = float(exchanger['ExchangePointComissionMax'].replace(',','.')) if float(exchanger['ExchangePointComissionMax'].replace(',','.'))<commission else commission
                    elif exchanger['ExchangePointComissionType'] == 'Flex' and exchanger['ExchangePointComissionMin'] != '' and exchanger['ExchangePointComissionMax'] == '':
                        commission = float(exchanger['ExchangePointComissionMin'].replace(',','.')) if float(exchanger['ExchangePointComissionMin'].replace(',','.'))<commission else commission
    min_sum_exch = None if min_sum_exch == 1000000000 else min_sum_exch
    commission = None if commission == 100 else commission
    return commission, min_sum_exch
