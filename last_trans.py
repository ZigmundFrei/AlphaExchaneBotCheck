# Для подсчета дней с последней сделки
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def get_last_trans():
    CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Сделки!2:1000000").execute()
    rows = resp['values']
    headers = rows.pop(0)
    sheet_data = [dict(zip(headers, one_row)) for one_row in rows]
    last_trans = {one_doc['TG_Contact']: one_doc['CreateDateTime'] for one_doc in sheet_data if 'CurrStatus' in one_doc and 'TG_Contact' in one_doc and one_doc['CurrStatus'] == 'Выполнена'}
    resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Контакты!A3:A1000000").execute()
    contacts_list = resp['values']
    res_list = []
    today = datetime.today()

    for contact in contacts_list:
        if len(contact)>=1 and contact[0] in last_trans.keys():
            date1 = datetime(int(last_trans[contact[0]].split('.')[2]), int(last_trans[contact[0]].split('.')[1]), int(last_trans[contact[0]].split('.')[0]))  # выбранная дата
            res_list.append(((date1-today).days)*-1-1)
        else:
            res_list.append('')
    # Ищем последнюю строку
    rows = service.spreadsheets().values().get(spreadsheetId=sheet_id,
                                            range='Контакты!A2:1000000').execute().get('values', [])
    last_row = rows[-1] if rows else None
    last_row_id = len(rows) + 1
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
        "valueInputOption": "USER_ENTERED",
        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        "data": [
            {"range": f"Контакты!AP{3}",
            "majorDimension": "COLUMNS",  # Сначала заполнять строки, затем столбцы
            "values": [
                res_list,  # Заполняем первую строку
            ]}
        ]
    }).execute()
