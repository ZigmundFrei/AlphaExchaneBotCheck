# Для поиска и вывода сделок по бонусному и реф кодам за месяц и все время
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json
import xlsxwriter

# Просмотр сделок за месяц и все время по бонусным кодам
def get_trans_history_disc(username, disc_code, _):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Сделки!B2:1000000").execute()
    rows = resp['values']
    rows[0].insert(0, 'deal_id')
    headers = rows.pop(0)
    for i, row in enumerate(rows):
        row.insert(0, i)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    all_trans = {one_doc['deal_id']: one_doc for one_doc in sheet_data if 'OPERTYPE' in one_doc.keys() and one_doc['OPERTYPE'] in ['EUR=>RUB', 'EUR=>USDT']
                    and one_doc['CurrStatus'] == 'Выполнена'}
    today = datetime.now()
    month_trans = {}
    month3_trans = {}
    for key, value in all_trans.items():
        date1 = datetime(int(value['CreateDateTime'].split('.')[2]), int(value['CreateDateTime'].split('.')[1]), int(value['CreateDateTime'].split('.')[0]))  # выбранная дата
        date2 = date1 + timedelta(days=31) # добавляем 30 дней, чтобы получить дату через месяц
        date3 = date1 + timedelta(days=92)
        if date2 >= today: #Добавить проверку длины бонусного кода и распределять на ДИСКОНТ и РЕФЕРАЛКУ
            month_trans[key] = value
            month3_trans[key] = value
        elif date3 >= today:
            month3_trans[key] = value
    mess_disc = _('<b>История сделок по дисконтному коду <em>{disc_code}</em></b> \n\n').format(disc_code=disc_code)
    for id, val in all_trans.items():
        if val['Reference_Number_FROM'] == disc_code:
            mess_disc += _('<em>Дата:</em> {date}\n' \
                          '<em>Тип сделки:</em> {exchangeId}\n' \
                          '<em>Сумма сделки:</em> {amount} EUR\n' \
                          '<em>Город:</em> {City}\n\n').format(date=val["CreateDateTime"],
                                                   exchangeId=val["exchangeId"],
                                                   amount=val["sendAmount"],
                                                   City=val["City"])
        else: pass
    mess_disc_month = _('<b>История сделок по дисконтному коду за последний месяц <em>{disc_code}</em></b> \n\n').format(disc_code=disc_code)
    for id, val in month_trans.items():
        if val['Reference_Number_FROM'] == disc_code:
            mess_disc_month +=_('<em>Дата:</em> {date}\n' \
                            '<em>Тип сделки:</em> {exchangeId}\n' \
                            '<em>Сумма сделки:</em> {amount} EUR\n' \
                            '<em>Город:</em> {City}\n\n').format(date=val["CreateDateTime"],
                                                                 exchangeId=val["exchangeId"],
                                                                 amount=val["sendAmount"],
                                                                 City=val["City"])
    mess_disc_3month = _('<b>История сделок по дисконтному коду за последние 3 месяца <em>{disc_code}</em></b> \n\n').format(disc_code=disc_code)
    for id, val in month3_trans.items():
        if val['Reference_Number_FROM'] == disc_code:
            mess_disc_3month +=_('<em>Дата:</em> {date}\n' \
                            '<em>Тип сделки:</em> {exchangeId}\n' \
                            '<em>Сумма сделки:</em> {amount} EUR\n' \
                            '<em>Город:</em> {City}\n\n').format(date=val["CreateDateTime"],
                                                                 exchangeId=val["exchangeId"],
                                                                 amount=val["sendAmount"],
                                                                 City=val["City"])
    return mess_disc, mess_disc_month, mess_disc_3month

def get_trans_history_ref(username, ref_code, _):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Сделки!B2:1000000").execute()
    rows = resp['values']
    rows[0].insert(0, 'deal_id')
    headers = rows.pop(0)
    for i, row in enumerate(rows):
        row.insert(0, i)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    all_trans = {one_doc['deal_id']: one_doc for one_doc in sheet_data if 'OPERTYPE' in one_doc.keys() and one_doc['OPERTYPE'] in ['EUR=>RUB', 'EUR=>USDT']
                    and one_doc['CurrStatus'] == 'Выполнена'}
    today = datetime.now()
    month_trans = {}
    month3_trans = {}
    for key, value in all_trans.items():
        date1 = datetime(int(value['CreateDateTime'].split('.')[2]), int(value['CreateDateTime'].split('.')[1]), int(value['CreateDateTime'].split('.')[0]))  # выбранная дата
        date2 = date1 + timedelta(days=31) # добавляем 30 дней, чтобы получить дату через месяц
        date3 = date1 + timedelta(days=92)
        if date2 >= today: #Добавить проверку длины бонусного кода и распределять на ДИСКОНТ и РЕФЕРАЛКУ
            month_trans[key] = value
            month3_trans[key] = value
        elif date3 >= today:
            month3_trans[key] = value
    mess_ref = _('<b>История сделок по реферальному коду <em>{ref_code}</em></b> \n\n').format(ref_code=ref_code)
    for id, val in all_trans.items():
        if val['Reference_Number_FROM'] == ref_code:
            mess_ref += _('<em>Дата:</em> {date}\n' \
                          '<em>Тип сделки:</em> {exchangeId}\n' \
                          '<em>Сумма сделки:</em> {amount} EUR\n' \
                          '<em>Город:</em> {City}\n\n').format(date=val["CreateDateTime"],
                                                   exchangeId=val["exchangeId"],
                                                   amount=val["sendAmount"],
                                                   City=val["City"])
        else: pass
    mess_ref_month = _('<b>История сделок по реферальному коду за последний месяц <em>{ref_code}</em></b> \n\n').format(ref_code=ref_code)
    for id, val in month_trans.items():
        if val['Reference_Number_FROM'] == ref_code:
            mess_ref_month +=_('<em>Дата:</em> {date}\n' \
                            '<em>Тип сделки:</em> {exchangeId}\n' \
                            '<em>Сумма сделки:</em> {amount} EUR\n' \
                            '<em>Город:</em> {City}\n\n').format(date=val["CreateDateTime"],
                                                                 exchangeId=val["exchangeId"],
                                                                 amount=val["sendAmount"],
                                                                 City=val["City"])
    mess_ref_3month = _('<b>История сделок по реферальному коду за последние 3 месяца <em>{ref_code}</em></b> \n\n').format(ref_code=ref_code)
    for id, val in month3_trans.items():
        if val['Reference_Number_FROM'] == ref_code:
            mess_ref_3month +=_('<em>Дата:</em> {date}\n' \
                            '<em>Тип сделки:</em> {exchangeId}\n' \
                            '<em>Сумма сделки:</em> {amount} EUR\n' \
                            '<em>Город:</em> {City}\n\n').format(date=val["CreateDateTime"],
                                                                 exchangeId=val["exchangeId"],
                                                                 amount=val["sendAmount"],
                                                                 City=val["City"])
    return mess_ref, mess_ref_month, mess_ref_3month

def get_trans_history(username, _):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Сделки!B2:1000000").execute()
    rows = resp['values']
    rows[0].insert(0, 'deal_id')
    headers = rows.pop(0)
    for i, row in enumerate(rows):
        row.insert(0, i)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    trans = {one_doc['deal_id']: one_doc for one_doc in sheet_data if 'OPERTYPE' in one_doc.keys() and one_doc['OPERTYPE'] in ['EUR=>RUB', 'EUR=>USDT']
                    and one_doc['CurrStatus'] == 'Выполнена' and one_doc['TG_Contact'] == username}
    if len(trans) == 0:
        mess = _('<b>Вы не совершали сделок</b>')
    else:
        mess = _('<b>История всех Ваших сделок: </b> \n\n')
        for id, val in trans.items():
            mess += _('<em>Дата:</em> {date}\n' \
                        '<em>Тип сделки:</em> {exchangeId}\n' \
                        '<em>Сумма сделки:</em> {amount} EUR\n' \
                        '<em>Город:</em> {City}\n\n').format(date=val["CreateDateTime"],
                                                exchangeId=val["exchangeId"],
                                                amount=val["sendAmount"],
                                                City=val["City"])
    return mess

def check_status(username, _):
    with open('contacts.json', 'r', encoding='utf8') as f:
        ACTIVE_CONTACT_LIST = json.load(f)
    user_category = ACTIVE_CONTACT_LIST[username]['ContactType']
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Сделки!B2:1000000").execute()
    rows = resp['values']
    rows[0].insert(0, 'deal_id')
    headers = rows.pop(0)
    for i, row in enumerate(rows):
        row.insert(0, i)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    trans = {one_doc['deal_id']: one_doc for one_doc in sheet_data if 'OPERTYPE' in one_doc.keys() and one_doc['OPERTYPE'] in ['EUR=>RUB', 'EUR=>USDT']
                    and one_doc['CurrStatus'] == 'Выполнена' and one_doc['TG_Contact'] == username}
    rub_trans_sum = 0
    rub_trans_3sum = 0
    usdt_trans_sum = 0
    usdt_trans_3sum = 0
    client_sale = '0%'
    currency = 'RUB'
    client_sum = 0
    today = datetime.now()
    for tran in trans.values():
        date1 = datetime(int(tran['CreateDateTime'].split('.')[2]), int(tran['CreateDateTime'].split('.')[1]), int(tran['CreateDateTime'].split('.')[0]))
        date2 = date1 + timedelta(days=92)
        if tran['OPERTYPE'] == 'EUR=>RUB':
            if date2 >= today:
                rub_trans_3sum += round(float(tran['receiveAmount'].replace(',', '.')), 2)
            rub_trans_sum += round(float(tran['receiveAmount'].replace(',', '.')), 2)
        else:
            if date2 >= today:
                usdt_trans_3sum += round(float(tran['receiveAmount'].replace(',', '.')), 2)
            usdt_trans_sum += round(float(tran['receiveAmount'].replace(',', '.')), 2)
    if rub_trans_sum/3500000 >= usdt_trans_sum/50000:
        currency = 'RUB'
        client_sum = round(rub_trans_sum,2)
        if user_category == 'Клиент' and rub_trans_sum < 3500000 and rub_trans_3sum < 700000 \
            or user_category == 'Обменник' and rub_trans_sum < 175000000 and rub_trans_3sum < 35000000 \
            or user_category == 'Партнер' and rub_trans_sum < 87500000 and rub_trans_3sum < 17500000:
            client_status = _('Базовый')
            client_sale = '0%'
            if user_category == 'Клиент':
                sum = 3500000
            elif user_category == 'Обменник':
                sum = 175000000
            else:
                sum = 875000000
            client_next_status_mess = _('до следующего статуса "Бронзовый", '\
             'предоставляющего скидку в размере 10%, необходиимо обменять еще {sum} {currency}').format(sum=sum-rub_trans_sum,
                                                                                                      currency=currency)
        elif user_category == 'Клиент' and rub_trans_sum >= 3500000 and rub_trans_sum < 7000000 or rub_trans_3sum >= 700000 and rub_trans_3sum < 1750000 \
            or user_category == 'Обменник' and rub_trans_sum >= 175000000 and rub_trans_sum < 350000000 and rub_trans_3sum >= 35000000 and rub_trans_3sum < 70000000 \
            or user_category == 'Партнер' and rub_trans_sum >= 87500000 and rub_trans_sum < 175000000 and rub_trans_3sum >= 17500000 and rub_trans_3sum < 35000000:
            client_status = _('Бронзовый')
            client_sale = '10%'
            if user_category == 'Клиент':
                sum = 7000000
            elif user_category == 'Обменник':
                sum = 350000000
            else:
                sum = 175000000
            client_next_status_mess = _('до следующего статуса "Серебряный", '\
             'предоставляющего скидку в размере 20%, необходиимо обменять еще {sum} {currency}').format(sum=sum-rub_trans_sum,
                                                                                                      currency=currency)
        elif user_category == 'Клиент' and rub_trans_sum >= 7000000 and rub_trans_sum < 17500000 or rub_trans_3sum >= 1750000 and rub_trans_3sum < 3500000 or \
            user_category == 'Обменник' and rub_trans_sum >= 350000000 and rub_trans_sum < 840000000 or rub_trans_3sum >= 70000000 and rub_trans_3sum < 210000000 or \
            user_category == 'Партнер' and rub_trans_sum >= 175000000 and rub_trans_sum < 420000000 or rub_trans_3sum >= 35000000 and rub_trans_3sum < 105000000:
            client_status = _('Серебряный')
            client_sale = '20%'
            client_next_status_mess = _('до следующего статуса "Золотой", '\
             'предоставляющего скидку в размере 30%, необходиимо обменять еще {sum} {currency}').format(sum=17500000-rub_trans_sum,
                                                                                                      currency=currency)
        elif user_category == 'Клиент' and rub_trans_sum >= 17500000 or rub_trans_3sum >= 3500000 or \
            user_category == 'Обменник' and rub_trans_sum >= 840000000 or rub_trans_3sum >= 210000000 or \
            user_category == 'Партнер' and rub_trans_sum >= 420000000 or rub_trans_3sum >= 105000000:
            client_status = _('Золотой')
            client_sale = '30%'
            client_next_status_mess = _('Ваш статус максимальный')
    else:
        currency = 'USDT'
        client_sum = round(usdt_trans_sum,2)
        if user_category == 'Клиент' and usdt_trans_sum < 50000 and usdt_trans_3sum < 10000 or \
            user_category == 'Обменник' and usdt_trans_sum < 2500000 and usdt_trans_3sum < 500000 or \
            user_category == 'Партнер' and usdt_trans_sum < 1250000 and usdt_trans_3sum < 250000:
            client_status = _('Базовый')
            client_sale = '0%'
            if user_category == 'Клиент':
                sum = 50000
            elif user_category == 'Обменник':
                sum = 2500000
            else:
                sum = 1250000
            client_next_status_mess = _('до следующего статуса "Бронзовый", '\
             'предоставляющего скидку в размере 10%, необходиимо обменять еще {sum} {currency}').format(sum=sum-usdt_trans_sum,
                                                                                                      currency=currency)
        elif user_category == 'Клиент' and usdt_trans_sum >= 50000 and usdt_trans_sum < 100000 or usdt_trans_3sum >= 10000 and usdt_trans_3sum < 25000 or \
            user_category == 'Обменник' and usdt_trans_sum >= 2500000 and usdt_trans_sum < 5000000 or usdt_trans_3sum >= 500000 and usdt_trans_3sum < 1000000 or \
            user_category == 'Партнер' and usdt_trans_sum >= 1250000 and usdt_trans_sum < 250000 or usdt_trans_3sum >= 250000 and usdt_trans_3sum < 500000:
            client_status = _('Бронзовый')
            client_sale = '10%'
            if user_category == 'Клиент':
                sum = 1000000
            elif user_category == 'Обменник':
                sum = 5000000
            else:
                sum = 2500000
            client_next_status_mess = _('до следующего статуса "Серебряный", '\
             'предоставляющего скидку в размере 20%, необходиимо обменять еще {sum} {currency}').format(sum=sum-usdt_trans_sum,
                                                                                                      currency=currency)
        elif user_category == 'Клиент' and usdt_trans_sum >= 100000 and usdt_trans_sum < 250000 or usdt_trans_3sum >= 25000 and usdt_trans_3sum < 50000 or \
            user_category == 'Обменник' and usdt_trans_sum >= 5000000 and usdt_trans_sum < 12000000 or usdt_trans_3sum >= 1000000 and usdt_trans_3sum < 3000000 or \
            user_category == 'Партнер' and usdt_trans_sum >= 250000 and usdt_trans_sum < 6000000 or usdt_trans_3sum >= 500000 and usdt_trans_3sum < 1500000:
            client_status = _('Серебряный')
            client_sale = '20%'
            if user_category == 'Клиент':
                sum = 250000
            elif user_category == 'Обменник':
                sum = 12000000
            else:
                sum = 6000000
            client_next_status_mess = _('до следующего статуса "Золотой", '\
             'предоставляющего скидку в размере 30%, необходиимо обменять еще {sum} {currency}').format(sum=sum-usdt_trans_sum,
                                                                                                      currency=currency)
        elif user_category == 'Клиент' and usdt_trans_sum >= 250000 or usdt_trans_3sum >= 50000 or \
            user_category == 'Обменник' and usdt_trans_sum >= 12000000 or usdt_trans_3sum >= 3000000 or \
            user_category == 'Партнер' and usdt_trans_sum >= 6000000 or usdt_trans_3sum >= 1500000:
            client_status = _('Золотой')
            client_sale = '30%'
            client_next_status_mess = _('Ваш статус максимальный')
        else:
            client_sale = '0%'
    if float(client_sale[:-1])*0.01 == float(ACTIVE_CONTACT_LIST[username]['Discount'].replace(',','.')):
        client_sale = str(float(ACTIVE_CONTACT_LIST[username]['Discount'].replace(',', '.')) * 100) + '%'
        mess = _('<b>Дополнительная информация о размере скидки: </b> \n\n' \
                 'Ваш статус: "{status}"\n' \
                 'Предоставляемая скидка: {sale} от нормы прибыльности по операциям обмена.\n\n' \
                 'Суммарно Вы обменяли {sum} {currency}').format(status='Особый',
                                                                sale=client_sale,
                                                                sum=client_sum,
                                                                currency=currency)
    else:
        mess = _('<b>Дополнительная информация о размере скидки: </b> \n\n'\
             'Ваш статус: "{status}"\n'\
             'Предоставляемая скидка: {sale} от нормы прибыльности по операциям обмена.\n\n'\
             'Суммарно Вы обменяли {sum} {currency}, {next_status_mess}').format(status=client_status,
                                                                                         sale=client_sale,
                                                                                         sum=client_sum,
                                                                                         currency=currency,
                                                                                         next_status_mess=client_next_status_mess)
    return mess

def get_bonus_history(username, balance_now, partner_flag):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="РасчетБонусов!A3:K1000000").execute()
    rows = resp['values']
    rows[0].insert(0, 'deal_id')
    headers = rows.pop(0)
    rows = list(map(lambda row: list(map(lambda elem: elem.replace(u'\xa0', ''), row)), rows))
    for i, row in enumerate(rows):
        row.insert(0, i)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    all_trans = {one_doc['deal_id']: one_doc for one_doc in sheet_data if one_doc['TG_Contact'] == username and one_doc['profit_destr'] == 'Партнер'} if partner_flag else\
    {one_doc['deal_id']: one_doc for one_doc in sheet_data if one_doc['TG_Contact'] == username and one_doc['profit_destr'] in ['P2P', 'Куратор', 'Обменник']}
    if balance_now:
        try:
            balance = list(all_trans.values())[-1]['end']
        except Exception as e:
            balance = 0
        return balance
    else:
        today = datetime.now()
        mess = '<b>История начислений и выплат премий в EUR для пользователя <em>{username}</em></b> \n'.format(username=username)
        for key, value in all_trans.items():
            date = datetime(int(value['date1'].split('/')[2]), int(value['date1'].split('/')[0]), int(value['date1'].split('/')[1]))
            if today - date <= timedelta(days=365):
                if value['profit_destr'] == 'Партнер':
                    if_partner = '(Вознаграждение ПАРТНЕРА)'
                else:
                    if_partner = ''
                mess += f'\n<b><em>Дата: {value["date1"]}</em> {if_partner}</b>\n' \
                        f'<em>На начало:</em> {value["start"]} \n' \
                        f'<em>Начисление:</em> {value["acrual"]}\n' \
                        f'<em>Оплата:</em> {value["charge"]}\n' \
                        f'<em>На конец:</em> {value["end"]}\n'
            else: pass
        if len(mess) < 90:
            mess = 'Для пользователя <em>{username}</em> отсутствуют записи'.format(username=username)
        return mess

def get_logs_history(username):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="LogAction!A2:K1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows][-500:]
    today = datetime.now()
    messages_list = []
    mess = '<b>История действий пользователей за последние 24 часа:</b> \n'
    messages_list.append(mess)
    for log in sheet_data:
        date = datetime.strptime(log['date_time'], '%Y-%m-%d %H:%M:%S')
        if today - date <= timedelta(days=1):
            if len(mess) < 3800 and (username == 'Все' or username != 'Все' and username == '@' + log["user_name"]):
                mess = f'<em>Время:</em> {log["date_time"]}\n' \
                        f'<em>Ник пользователя:</em> {log["user_name"]} \n' \
                        f'<em>Имя пользователя:</em> {log["user_fio"]}\n' \
                        f'<em>Действие:</em> {log["action"]}\n\n'
                messages_list.append(mess)
        else: pass
    if len(messages_list) == 0:
        messages_list.append('Записей не найдено')
    return messages_list

def create_deals_xlsx(username, city, curator_username):
    append_flag = False
    res_rows = []
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    #resp = service.spreadsheets().values().batchGet(spreadsheetId=sheet_id, ranges=["Сделки!B2:C100000", "Сделки!E2:F100000", "Сделки!G2:I100000", "Сделки!P2:Q100000"]).execute()
    #deals_data = (sub_data0 + sub_data1 + sub_data2 + sub_data3 for sub_data0, sub_data1, sub_data2, sub_data3 in zip(resp['valueRanges'][0]['values'], resp['valueRanges'][1]['values'], resp['valueRanges'][2]['values'], resp['valueRanges'][3]['values']))
    workbook = xlsxwriter.Workbook('Deals.xlsx')
    worksheet = workbook.add_worksheet('Сделки')
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Сделки!A2:AA1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    rows = list(map(lambda row: list(map(lambda elem: elem.replace(u'\xa0', ''), row)), rows))
    with open('contacts.json', 'r', encoding='utf8') as f:
        ACTIVE_CONTACT_LIST = json.load(f)
    if username == 'Все':
        res_rows = [row for row in rows if len(row)>21 and row[6] in ['RSD=>RUB','RUB=>RSD','USDT=>USDT','USDT=>EUR', 'RUB=>EUR', 'USDT=>RUB', 'RUB=>EUR', 'BGN=>RUB', 'RUB=>BGN', 'USDT=>BGN'] and row[21] in city]
    elif curator_username is None and username != 'Все' and ACTIVE_CONTACT_LIST[username]["ContactType"] != "Куратор":
        res_rows = [row for row in rows if len(row)>21 and row[6] in ['RSD=>RUB','RUB=>RSD','EUR=>USDT','USDT=>EUR', 'RUB=>EUR', 'USDT=>RUB', 'EUR=>RUB', 'BGN=>RUB', 'RUB=>BGN', 'USDT=>BGN'] and row[19]==username and row[21] in city]
    elif curator_username is not None and username != 'Все' and ACTIVE_CONTACT_LIST[curator_username]["ContactType"] == "Куратор":
        res_rows = [row for row in rows if len(row)>21 and row[6] in ['RSD=>RUB','RUB=>RSD','EUR=>USDT','USDT=>EUR', 'RUB=>EUR', 'USDT=>RUB', 'EUR=>RUB', 'BGN=>RUB', 'RUB=>BGN', 'USDT=>BGN'] and row[4]==curator_username and row[21] in city]
    else:
        res_rows = [row for row in rows if len(row)>21 and row[19]==username and row[21] in city]     
    res = False if len(res_rows) < 1 else True
    worksheet.write_row('A1', headers)
    for row_num, row_data in enumerate(res_rows):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num+1, col_num, cell_data)
    workbook.close()
    return res

def create_contacts_report_for_split_xlsx(split):
    append_flag = False
    res_rows = []
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    workbook = xlsxwriter.Workbook('Contacts.xlsx')
    worksheet = workbook.add_worksheet('Контакты')
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Контакты!A2:AA1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    rows = list(map(lambda row: list(map(lambda elem: elem.replace(u'\xa0', ''), row)), rows))
    res_rows = [row for row in rows if len(row)>21 and row[11]==split]     
    res = False if len(res_rows) < 1 else True
    worksheet.write_row('A1', headers)
    for row_num, row_data in enumerate(res_rows):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num+1, col_num, cell_data)
    workbook.close()
    return res

def create_deals_report_for_split_xlsx(split):
    users_trans = []
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    workbook = xlsxwriter.Workbook('Contacts.xlsx')
    worksheet = workbook.add_worksheet('Контакты')
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Контакты!A2:AA1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    rows = list(map(lambda row: list(map(lambda elem: elem.replace(u'\xa0', ''), row)), rows))
    user_list = [row[0] for row in rows if len(row)>21 and row[11]==split]   
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Сделки!B2:1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    users_trans = [list(one_doc.values()) for one_doc in sheet_data if 'TG_Contact' in one_doc.keys() and one_doc['TG_Contact'] in user_list]
    res = True if len(users_trans) > 0 else False
    worksheet.write_row('A1', headers)
    for row_num, row_data in enumerate(users_trans):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num+1, col_num, cell_data)
    workbook.close()
    return res

def get_last24h_trans(curator_type):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Сделки!B2:1000000").execute()
    rows = resp['values']
    rows[0].insert(0, 'row_num')
    headers = rows.pop(0)
    for i, row in enumerate(rows):
        row.insert(0, i)
    today = datetime.now()
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    all_trans = [one_doc for one_doc in sheet_data if 'exchangeId' in one_doc.keys() and one_doc['exchangeId'] in ['EUR=>RUB', 'EUR=>USDT', 'RUB=>EUR', 'USDT=>EUR', 'USDT=>RUB', 'RUB=>USDT', 'USDT=>EUR', 'USDT=>KZT', 'USDT=>UAH']
                    and one_doc['CurrStatus'] == 'План' and datetime(int(one_doc['CreateDateTime'].split('.')[2]), int(one_doc['CreateDateTime'].split('.')[1]), int(one_doc['CreateDateTime'].split('.')[0]))+ timedelta(days=1)>=today]
    result = {}
    deal_id = ''
    for trans in all_trans[-1000:]:
        if curator_type == 'P2P':
            if trans['receiveCurrencyName'] == 'USDT' or trans['sendCurrencyName'] == 'USDT':
                result[trans['row_num']] = trans['DealID']
        else:
            if trans['DealID'] == deal_id:
                pass
            else:
                if trans['receiveCurrencyName'] != 'USDT' and trans['sendCurrencyName'] != 'USDT':
                    result[trans['row_num']] = trans['DealID']
                    deal_id = trans['DealID']
    mess = ''
    for deal_id in result.values():
        for one_doc in all_trans[-1000:]:
            if one_doc['DealID'] == deal_id:
                mess += f'<em>ID сделки:</em> {one_doc["DealID"]}\n' \
                        f'<em>Направление:</em> {one_doc["exchangeId"]} \n' \
                        f'<em>Имя пользователя:</em> {one_doc["TG_Contact"]}\n' \
                        f'<em>Город:</em> {one_doc["City"]}\n\n'
                break
    return (result, mess)

def gs_write_close_order(deals_dict, deal_id, cur_contact, fact_giv, fact_get, image_url, status, comment):
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Сделки!A2:AK1000000").execute()
    if status != 'Отменена':
        ind = None
        for key, value in deals_dict.items():
            if value == deal_id:
                ind = key
        if ind is None:
            return None
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
            "valueInputOption": "USER_ENTERED",
            # Записываем отдаваемую сумму
            "data": [
                {"range": f"Сделки!E{ind+3}:100000",
                "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                "values": [
                    [cur_contact]  # Заполняем первую строку
                ]}
            ]
        }).execute()
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
            "valueInputOption": "USER_ENTERED",
            # Записываем отдаваемую сумму
            "data": [
                {"range": f"Сделки!I{ind+3}:100000",
                "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                "values": [
                    [fact_giv]  # Заполняем первую строку
                ]}
            ]
        }).execute()
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
            "valueInputOption": "USER_ENTERED",
            # Записываем отдаваемую сумму
            "data": [
                {"range": f"Сделки!O{ind+3}:100000",
                "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                "values": [
                    [fact_get]  # Заполняем первую строку
                ]}
            ]
        }).execute()
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
            "valueInputOption": "USER_ENTERED",
            # Записываем отдаваемую сумму
            "data": [
                {"range": f"Сделки!S{ind+3}:100000",
                "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                "values": [
                    [status]  # Заполняем первую строку
                ]}
            ]
        }).execute()
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
            "valueInputOption": "USER_ENTERED",
            # Записываем отдаваемую сумму
            "data": [
                {"range": f"Сделки!AI{ind+3}:100000",
                "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                "values": [
                    [image_url]  # Заполняем первую строку
                ]}
            ]
        }).execute()
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
            "valueInputOption": "USER_ENTERED",
            # Записываем отдаваемую сумму
            "data": [
                {"range": f"Сделки!AN{ind+3}:100000",
                "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                "values": [
                    [comment]  # Заполняем первую строку
                ]}
            ]
        }).execute()
    else:
        rows = resp['values']
        rows[0].insert(0, 'row_num')
        headers = rows.pop(0)
        for i, row in enumerate(rows):
            row.insert(0, i)
        today = datetime.now()
        sheet_data = [dict(zip(headers, one_row)) for one_row in rows[-1000:]]
        all_trans = [one_doc for one_doc in sheet_data if 'exchangeId' in one_doc.keys() and one_doc['exchangeId'] in ['EUR=>RUB', 'EUR=>USDT', 'RUB=>EUR', 'USDT=>EUR', 'USDT=>RUB', 'RUB=>USDT', 'USDT=>EUR', 'USDT=>KZT', 'USDT=>UAH']
                        and one_doc['CurrStatus'] in ['План', 'РасчБонПлан'] and datetime(int(one_doc['CreateDateTime'].split('.')[2]), int(one_doc['CreateDateTime'].split('.')[1]), int(one_doc['CreateDateTime'].split('.')[0]))+ timedelta(days=1)>=today]
        for trans in all_trans:
            if trans['DealID'] == deal_id:
                results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
                    "valueInputOption": "USER_ENTERED",
                    # Записываем отдаваемую сумму
                    "data": [
                        {"range": f"Сделки!E{trans['row_num']+3}:100000",
                        "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                        "values": [
                            [cur_contact]  # Заполняем первую строку
                        ]}
                    ]
                }).execute()
                results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
                    "valueInputOption": "USER_ENTERED",
                    # Записываем отдаваемую сумму
                    "data": [
                        {"range": f"Сделки!S{trans['row_num']+3}:100000",
                        "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                        "values": [
                            [status]  # Заполняем первую строку
                        ]}
                    ]
                }).execute()
                results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
                    "valueInputOption": "USER_ENTERED",
                    # Записываем отдаваемую сумму
                    "data": [
                        {"range": f"Сделки!AI{trans['row_num']+3}:100000",
                        "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                        "values": [
                            [image_url]  # Заполняем первую строку
                        ]}
                    ]
                }).execute()
                results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
                    "valueInputOption": "USER_ENTERED",
                    # Записываем отдаваемую сумму
                    "data": [
                        {"range": f"Сделки!AN{trans['row_num']+3}:100000",
                        "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                        "values": [
                            [comment]  # Заполняем первую строку
                        ]}
                    ]
                }).execute()