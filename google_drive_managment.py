from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

def upload_image_to_google_drive(image_file_path, name, credentials_path, folder_id=None):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('drive', 'v3', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    
    file_metadata = {'name': name, 
                     'parents': ['1egn3JC_dy9cJ4quW6cXXvhoKHX2lX9tW']}
    
    uploaded_file = service.files().create(
        body=file_metadata, media_body=image_file_path, fields='id, webContentLink'
        ).execute()
    download_link = uploaded_file.get('webContentLink')
    print(f'Ссылка на документ: {download_link}')
    return download_link

def get_file_id_by_name(file_name, credentials_path):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('drive', 'v3', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    
    # Поиск файлов по имени
    results = service.files().list(q=f"name='{file_name}'").execute()
    items = results.get('files', [])
    
    if not items:
        print('Файл не найден.')
    else:
        print('ID найденных файлов:')
        for item in items:
            print(f"{item['name']}: {item['id']}")

def get_file_link_by_id(file_id, credentials_path):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('drive', 'v3', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    
    # Получаем метаданные файла
    file_metadata = service.files().get(fileId=file_id, fields='webViewLink').execute()
    
    # Извлекаем ссылку на просмотр файла
    web_view_link = file_metadata.get('webViewLink')
    
    if web_view_link:
        return web_view_link
    else:
        return "Ссылка на файл не найдена."


