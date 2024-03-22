# при нажатии
import telebot
from telebot import types
from telebot.storage import StateMemoryStorage
from states_machine import RateStates, MainMenue, FormOrder
from utils import construct_translator
from config import *
from datetime import datetime
from pytz import timezone
import rates_funcs as rates_funcs
import math
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from gs_write_funcs import write_feedback, add_row, write_contact, log_action, calculate_indexes, add_border, \
    write_pending_order, write_language, scrab_contact_list, update_contact, write_update_contacts, gs_write_usdrub_eurrub, get_city_commission
from tron_risk import *
import random
import string
import os
from trans_history import get_trans_history_ref, get_trans_history_disc, get_trans_history, check_status, get_bonus_history, get_logs_history, \
    create_deals_xlsx, create_contacts_report_for_split_xlsx, create_deals_report_for_split_xlsx, get_last24h_trans, gs_write_close_order
from last_trans import get_last_trans
from gs_balance import check_balance, cards_balance
from google_drive_managment import upload_image_to_google_drive
import time
from apscheduler.schedulers.background import BackgroundScheduler
#from apscheduler.schedulers.blocking import BlockingScheduler
import re
import json
import traceback
import gettext


# rates_funcs.get_rates_data('tima')

### Блок для перевода текста

from utils import _


# Создание функции переводчика
get_user_translator = construct_translator()
###


try:
# ----------------------------------------------------------------------
    GROUP_CHAT_ID = -942693297 #942693297 - Alpha 917301290 - test
    state_storage = StateMemoryStorage()
    bot = telebot.TeleBot(ACCESS_TOKEN, state_storage=state_storage)
    tz = timezone('Europe/Podgorica')  # Поменять на Черногорию
    # Переменные заявки RUB_EUR (RE)
    OPER_NAME_RE = ''
    BANK_RE = ''
    SUM_EUR_RE = None  # вводится пользователем
    SUM_RUB_RE = None  # рассчитывается через rates_funcs
    RUB_EURO_RATE = None
    CITY_RE = None
    ORDER_TIME_RE = None
    ORDER_TIME_UE = None
    REF_CODE_RE = None
    DISCOUNT_RE = None  # для определения размера скидки клиента
    DISCOUNT_UE = None
    RUB_INFO = None  # переменная необходима для хранения данных о курсах при вызове команды RUB_EURO и используется для добавления записей в GSH
    # Переменные заявки USDT_EUR (UE)
    OPER_NAME_UE = ''
    SUM_EUR_UE = None  # вводится пользователем
    BLOCKCHAIN = None
    ADDRESS = None
    SUM_USDT_UE = None  # рассчитывается через rates_funcs
    RISK_TRC = None
    USDT_EURO_RATE = None
    CITY_UE = None
    REF_CODE_UE = None
    USDT_EURO_RATE_GS = None
    # Флаги для заглушек
    RATES_FLAG = False
    START_FLAG = False
    #FORM_ORDER_FLAG = False
    OPER_FLAG_EUR_RUB = False
    OPER_FLAG_EUR_RUB_BACK = False
    OPER_FLAG_USDT_EURO_BACK = False
    OPER_FLAG_USDT_EURO = False
    BANK_FLAG = False
    SUM_RUB_FLAG = False
    SUM_USDT_FLAG = False
    CITY_RE_FLAG = False
    CITY_UE_FLAG = False
    ANOTHER_CITY_RE_FLAG = False
    ANOTHER_CITY_UE_FLAG = False
    ORDER_CONFIRM_RE_FLAG = False
    ORDER_CONFIRM_UE_FLAG = False
    FIND_USER_FLAG = False
    NAME_FLAG = False
    LANGUAGE_FLAG = False
    FEEDBACK_FLAG = False  # Для проверки активации кнопки "Осавить отзыв"
    REFERRAL_FLAG = False  # Для проверки активации кнопки "Бонусная брограмма"
    MESSAGE_FLAG = False
    USER_OWNER = False
    CREATE_FLAG = False
    SEX_FLAG = False
    CITY_FLAG = False
    USER_STATUS_FLAG = False
    REFERRAL_OPTIONS_FLAG = False
    REFERRAL_CHARGES_FLAG = False # Для просмотра начислений по реф коду
    REFERRAL_HIST_FLAG = False # Для просмотра истории сделок по реф коду
    REFERRAL_PERIOD_FLAG = False
    DISCONT_PERIOD_FLAG = False
    PENDING_ORDER_FLAG = False
    DOCS_FLAG = False  # проверяем, в каком месте вызывается команда /documents
    CASH_FLAG = False  # проверяем, если был выбран способ оплаты наличными. Нужно обновлять флаг каждый раз, когда вызывается команда form_order
    CASH_CITY = ''  # когда CASH_FLAG переключим на True, ереопределим переменную CASH_CITY на выбранное место внесения рублей (Москва, Санкт-Петербург, Черногория)
    ORDER_TIME_FLAG_RE = False  # для проверки выбора времени сделки RUB-EUR
    FRIEND_REF_FLAG_RE = False  # Код реферальной программы друга, если клиент не хочет использовать свой
    RES_ORDER_FLAG_RE = False  # Переключаем на True, когда определили код реф программы и просим подвтерждение
    ORDER_TIME_FLAG_UE = False  # для проверки выбора времени сделки USDT-EUR
    FRIEND_REF_FLAG_UE = False  # Код реферальной программы друга, если клиент не хочет использовать свой
    RES_ORDER_FLAG_UE = False  # Переключаем на True, когда определили код реф программы и просим подвтерждение
    ADMIN_FLAG = False
    message_city = []
    message_sex = []
    message_user_status = []
    message_last_trans = []
    message_user_owner = []
    MAIN_MENU_BUTTONS = [_('🔁 Обмен по заявке'), _('📞 Связаться с оператором'), _('💸 Наши курсы'), _('📘 Документы'),
                        _('👨‍👦‍👦 Бонусная программа'), _('⚙️ Команды'), _('🕛 История сделок'), _('📨 Оставить отзыв'), _('📽 Обучающее видео')]
    CITY_BUTTONS = [_('Бар'), _('Бечичи'), _('Будва'), _('Котор'), _('Петровац'), _('Подгорица'), _('Тиват'),
                    _('Ульцинь'), _('Херцег Нови'), _('Цетине'), _('Другая локация')]
    CITY_CASH_BUTTONS = [_('Москва'), _('Санкт-Петербург'), _('Владивосток'), _('Волгоград'), _('Воронеж'), _('Грозный'), _('Екатеринбург'), _('Иркутск'), _('Казань'),
                    _('Краснодар'), _('Махачкала'), _('Новосибирск'), _('Омск'), _('Оренбург'), _('Пятигорск'), _('Ростов-На-Дону'), _('Самара'), _('Симферополь'),
                     _('Сочи'), _('Сургут'), _('Тюмень'), _('Уфа'), _('Хабаровск'), _('Челябинск'), ('Другая локация')]
    ADMIN_MENU_BUTTONS = ['Откуп', 'Снятие с карт', 'Расходы', 'Трансфер денег', 'Выплата бонусов', 'Баланс валют', 'Действия пользователей', 'Отчетность', 'Закрытие сделок', 'Закрыть панель']
    ADMIN_MENU_BUTTONS_EX = ['Выплата бонусов', 'Выплаты и бонусы', 'Отчет по сделкам', 'Закрыть панель']
    mb = types.KeyboardButton(_('Главное меню'))
    @bot.message_handler(commands=['admin'])
    def admin(message):
        bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
        if message.chat.id != GROUP_CHAT_ID:
            with open('contacts.json', 'r', encoding='utf8') as f:
                ACTIVE_CONTACT_LIST = json.load(f)
            username = '@' + message.chat.username if message.chat.username is not None else 'None'
            user_id = message.from_user.id
            all_users_id_type = [[user_info['user_ID'], user_info['ContactType'], user_info['CurrStatus'], user_info['ContactOwnerTG']] for user_info in ACTIVE_CONTACT_LIST.values()]
            for elem in all_users_id_type:
                if str(user_id) in elem and elem[1] in ['Куратор', 'Партнер', 'Обменник'] and elem[2] != 'Блок':
                    #global FORM_ORDER_FLAG, FEEDBACK_FLAG
                    #FORM_ORDER_FLAG, FEEDBACK_FLAG = False, False
                    global admin_sum, admin_cross_rate, admin_seller_nik, admin_city, admin_currency, bonus_flag, comment, operation, bank_acc
                    admin_sum, admin_cross_rate, admin_seller_nik, admin_city, admin_currency, comment, operation, bank_acc = None,  None, None, None, None, None, None, None
                    bonus_flag = False
                    global admin_deals_city, admin_deals_city_flag
                    admin_deals_city_flag = False
                    admin_deals_city = []
                    global ADMIN_FLAG, KURATOR_BONUS_FLAG
                    ADMIN_FLAG = True
                    KURATOR_BONUS_FLAG = False
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if elem[1] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                    markup.add(*menu_buttons)
                    mess = '<b>Панель администратора открыта</b>'
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                    log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                    message.from_user.full_name, 'Админ панель (admin)', '-')
                    break
                else:
                    pass
    @bot.message_handler(commands=['change_language'])
    def change_language(message):
        #global FORM_ORDER_FLAG, FEEDBACK_FLAG
        #FORM_ORDER_FLAG, FEEDBACK_FLAG = False, False
        _ = get_user_translator(message.from_user.id)
        global LANGUAGE_FLAG
        LANGUAGE_FLAG = True
        mess = _('<b>Смена языка</b>\n' \
                'Выберите доступный язык\n')
        a = types.ReplyKeyboardRemove()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        b1 = types.KeyboardButton(_('RU'))
        b2 = types.KeyboardButton(_('EN'))
        b3 = types.KeyboardButton(_('SR'))
        markup.add(b1, b2, b3)
        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
    @bot.message_handler(commands=['feedback'])
    def feedback(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['FEEDBACK_FLAG'] = True
                data['FORM_ORDER_FLAG'] = False
            _ = get_user_translator(message.from_user.id)
            mess = _('<b>Оставить отзыв</b>\n\n' \
                    'Ваш отзыв поможет нам стать лучше!\n\n' \
                    'Если у Вас есть идеи по улучшению работы сервиса или Вы столкнулись с проблемой, пожалуйста, напишите об этом здесь.\n\n')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            b1 = types.KeyboardButton(_('Главное меню'))
            markup.add(b1)
            bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                    message.from_user.full_name, 'Оставить отзыв (feedback)', '-')
    @bot.message_handler(commands=['trans_history'])
    def trans_history(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['FEEDBACK_FLAG'] = False
                data['FORM_ORDER_FLAG'] = False
            _ = get_user_translator(message.from_user.id)
            username = '@' + message.chat.username if message.chat.username is not None else 'None'
            res = False
            try:
                res = create_deals_xlsx(username, CITY_BUTTONS+CITY_CASH_BUTTONS, None)
                mess = 'Отчет сформирован успешно!' if res else 'Не удалось найти сделок по данным критериям'
            except Exception as e:
                print('Exception: ' + str(e))
                mess = 'Не удалось составить отчет для данного пользователя'
            if res:
                with open('Deals.xlsx', 'rb') as doc:
                    bot.send_document(message.chat.id, doc)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
            markup.add(*menu_buttons)
            bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                    message.from_user.full_name, 'История сделок (trans_history)', '-')
    @bot.message_handler(commands=['refferal'])
    def refferal(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['FEEDBACK_FLAG'] = False
                data['FORM_ORDER_FLAG'] = False
                data['REFERRAL_FLAG'] = False
            _ = get_user_translator(message.from_user.id)
            #ACTIVE_CONTACT_LIST = scrab_contact_list()
            with open('contacts.json', 'r', encoding='utf8') as f:
                ACTIVE_CONTACT_LIST = json.load(f)
            a = types.ReplyKeyboardRemove()
            username = '@' + message.chat.username if message.chat.username is not None else 'None'
            user_id = message.from_user.id
            all_user_ids = [user_info['user_ID'] for user_info in ACTIVE_CONTACT_LIST.values()]
            if (username in ACTIVE_CONTACT_LIST or user_id in all_user_ids) and ACTIVE_CONTACT_LIST[username][
                'CurrStatus'] == 'Активный':
                user_info = ACTIVE_CONTACT_LIST[username]
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['REFERRAL_FLAG'] = True
                mess = _('Здесь Вы можете посмотреть всю информацию по бонусной программе, а именно:\n\n' \
                        '1) Историю обменов по Вашему <b>реферальному</b> и <b>дисконтному</b> коду.\n\n' \
                        '2) Историю начислений и выплат по Вашему <b>реферальному</b> коду.\n\n' \
                        '3) Общую информацию в <b>Карте бонусной программы</b>.')
                b1 = types.KeyboardButton(_('Реферальная программа'))
                b2 = types.KeyboardButton(_('Дисконтная программа'))
                b3 = types.KeyboardButton(_('Карта бонусной программы'))
                b4 = types.KeyboardButton(_('Главное меню'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b3, b2, b1, b4)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif (username in ACTIVE_CONTACT_LIST or user_id in all_user_ids) and ACTIVE_CONTACT_LIST[username][
                'CurrStatus'] != 'Активный':
                mess = _('Ваша учетная запись временно заблокирована в соответствии с правилами совершения операций с беспоставочными финансовыми инструментами. Для разблокировки Вашей учетной записи или формирования заявки на обмен Вы можете связаться с оператором с помощью команды /contact_operator')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            else:
                mess = _('Вам не присвоен код реферальной программы. Совершите хотя бы одну операцию для присвоения кода')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                    message.from_user.full_name, 'Реферальная программа (refferal)', '-')
    @bot.message_handler(commands=['tutorial'])
    def tutorial(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['FEEDBACK_FLAG'] = False
                data['FORM_ORDER_FLAG'] = False
                data['DOCS_FLAG'] = False
            _ = get_user_translator(message.from_user.id)
            mess = _(f"Обучающее видео доступно по ссылке: <a href='{LINK_TUTORIAL}'>ОБУЧАЮЩЕЕ ВИДЕО</a>")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
            markup.add(*menu_buttons)
            bot.send_video(chat_id=message.chat.id,
                           video=open('C:/Users/admin/Documents/AlphaCapitalHowToBot1.mp4', 'rb'),
                           supports_streaming=True, width=1080, height=1920)
            #bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                       message.from_user.full_name, 'Обучающее видео (tutorial)', '-')
    @bot.message_handler(commands=['start'])
    def start(message):
        if message.chat.id != GROUP_CHAT_ID:
            _ = get_user_translator(message.from_user.id)
            bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['START_FLAG'] = True
                bot.send_video(chat_id=message.chat.id,
                               video=open('C:/Users/admin/Documents/AlphaCapitalHowToBot1.mp4', 'rb'),
                               supports_streaming=True, width=1080, height=1920)
                mess = _('Привет, <b>{first_name}!</b>\n\n' \
                        'Наш бот поможет Вам сформировать заявку для обмена валют, а также покажет список наших курсов.\n' \
                        'Перечень доступных команд можно посмотреть с помощью /help\n\n' \
                        'Call the /help commad if you want to change the bot language\n'
                        '<b><em>Для обладателей промокодов курсы еще выгоднее!</em></b>').format(
                    first_name=message.from_user.first_name)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                #ACTIVE_CONTACT_LIST = scrab_contact_list()
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                if username not in ACTIVE_CONTACT_LIST:
                    existed_disc_codes = [one_doc['Discount_Number'] for one_doc in ACTIVE_CONTACT_LIST.values()]
                    existed_ref_codes = [one_doc['Referral_Number'] for one_doc in ACTIVE_CONTACT_LIST.values() if 'Referral_Number' in one_doc]
                    while True:
                        s = string.ascii_lowercase + string.ascii_uppercase + string.digits
                        disc_code = ''.join(random.sample(s, 4))
                        ref_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                        if disc_code not in existed_disc_codes and ref_code not in existed_ref_codes:
                            break
                    write_contact(TG_Contact=username, user_ID=message.from_user.id, NameSurname=message.from_user.full_name,
                                        AccTypeFROM='', CurrFROM='RUB',
                                        City='Alpha_TG_Bot', ContactType='Клиент', ContactDealer='Alpha_TG_Bot', CurrStatus='Активный',
                                        Discount_Number=disc_code, Referral_Number=ref_code)
                log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                        message.from_user.full_name, 'Старт (start)', '-')
    @bot.message_handler(commands=['help'])
    def help(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['RATES_FLAG'] = False
                data['FORM_ORDER_FLAG'] = False
                data['FEEDBACK_FLAG'] = False
                data['DOCS_FLAG'] = False
            _ = get_user_translator(message.from_user.id)
            mess = _('<b>Список доступных команд:</b>\n\n' \
                    '/form_order - <em>Обменять валюту по заявке в Telegram. Для этого Вам необходимо сформировать заявку с помощью нашего бота</em>\n\n' \
                    '/contact_operator - <em>Обменять валюту по связи с оператором. Вы можете напрямую связаться с оператором. После ввода данной команды наш сотрудник' \
                    ' получит сообщение с просьбой связаться с Вами</em>\n\n' \
                    '/get_rates - <em>Получить список наших курсов</em>\n\n' \
                    '/documents - <em>Правила совершения операций по обмену валют и реферальная программа</em>\n\n' \
                    '/refferal - <em>Получить карточку реферальной программы</em>\n\n' \
                    '/feedback - <em>Оставить отзыв и пожелания</em>\n\n' \
                    '/change_language - <em>Сменить язык</em>')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
            markup.add(*menu_buttons)
            bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                    message.from_user.full_name, 'Команды (help)', '-')
    @bot.message_handler(commands=['documents'])
    def documents(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['RATES_FLAG'] = False
                data['FORM_ORDER_FLAG'] = False
                data['FEEDBACK_FLAG'] = False
                data['DOCS_FLAG'] = False
            _ = get_user_translator(message.from_user.id)
            #ACTIVE_CONTACT_LIST = scrab_contact_list()
            with open('contacts.json', 'r', encoding='utf8') as f:
                ACTIVE_CONTACT_LIST = json.load(f)
            username = '@' + message.chat.username if message.chat.username is not None else 'None'
            user_id = message.from_user.id
            all_user_ids = [user_info['user_ID'] for user_info in ACTIVE_CONTACT_LIST.values()]
            if (username in ACTIVE_CONTACT_LIST or user_id in all_user_ids) and ACTIVE_CONTACT_LIST[username][
                'CurrStatus'] != 'Активный':
                mess = _('Ваша учетная запись временно заблокирована в соответствии с правилами совершения операций с беспоставочными финансовыми инструментами. Для разблокировки Вашей учетной записи или формирования заявки на обмен Вы можете связаться с оператором /contact_operator')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            else:
                client_warning_mess = _(
                    '<b>Список документов, регулирующих правила совершения операций по обмену валют:</b>\n\n' \
                    "1. <a href='{LINK_PUB_OFFER}'>Публичная оферта</a>\n\n" \
                    "2. <a href='{LINK_OPER_RULES}'>Правила совершения операций P2P</a>\n\n" \
                    "3. <a href='{LINK_RATES}'>Тарифы AlphaCapital.Exchange</a>\n\n" \
                    "4. <a href='{LINK_DISC_PROG}'>Дисконтная программа</a>\n\n" \
                    "5. <a href='{LINK_REF_PROG}'>Реферальная программа</a>\n\n" \
                    "6. <a href='{LINK_CONF_POL}'>Политика конфиденциальности</a>\n\n" \
                    "7. <a href='{LINK_AML}'>Уведомление по AML</a>\n\n" \
                    "8. <a href='{LINK_BANK_RISC}'>Уведомление о рисках банк.карты</a>\n\n" \
                    "9. <a href='{LINK_RISK_WARNING}'>Уведомление о рисках мошенничества</a>\n" ).format(LINK_OPER_RULES=LINK_OPER_RULES,
                                                        LINK_RATES=LINK_RATES,
                                                        LINK_DISC_PROG=LINK_DISC_PROG,
                                                        LINK_REF_PROG=LINK_REF_PROG,
                                                        LINK_CONF_POL=LINK_CONF_POL,
                                                        LINK_AML=LINK_AML,
                                                        LINK_BANK_RISC=LINK_BANK_RISC,
                                                        LINK_RISK_WARNING=LINK_RISK_WARNING,
                                                        LINK_PUB_OFFER=LINK_PUB_OFFER)
                if DOCS_FLAG is True:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    b1 = types.KeyboardButton(_('Да'))
                    b2 = types.KeyboardButton(_('Нет'))
                    markup.add(b1, b2)
                    bot.send_message(message.chat.id, client_warning_mess, parse_mode='html', reply_markup=markup)
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                    markup.add(*menu_buttons)
                    bot.send_message(message.chat.id, client_warning_mess, parse_mode='html', reply_markup=markup)
            log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                    message.from_user.full_name, 'Документы (documents)', '-')
    @bot.message_handler(commands=['get_rates'])
    def get_rates(message):
        if message.chat.id != GROUP_CHAT_ID:
            start = datetime.now()
            #global bank_acc
            #bank_acc = None
            #global FORM_ORDER_FLAG
            #FORM_ORDER_FLAG = False
            #global FEEDBACK_FLAG
            #FEEDBACK_FLAG = False
            #global RATES_FLAG
            #RATES_FLAG = True
            _ = get_user_translator(message.from_user.id)
            #ACTIVE_CONTACT_LIST = scrab_contact_list()
            with open('contacts.json', 'r', encoding='utf8') as f:
                ACTIVE_CONTACT_LIST = json.load(f)
            a = types.ReplyKeyboardRemove()
            username = '@' + message.chat.username if message.chat.username is not None else 'None'
            user_id = message.from_user.id
            discount = ACTIVE_CONTACT_LIST[username]['Discount'] if username in ACTIVE_CONTACT_LIST else '0'
            all_user_ids = [user_info['user_ID'] for user_info in ACTIVE_CONTACT_LIST.values()]
            if (username in ACTIVE_CONTACT_LIST or user_id in all_user_ids) and ACTIVE_CONTACT_LIST[username][
                'CurrStatus'] != 'Активный':
                mess = _('Ваша учетная запись временно заблокирована в соответствии с правилами совершения операций с беспоставочными финансовыми инструментами. Для разблокировки Вашей учетной записи или формирования заявки на обмен Вы можете связаться с оператором /contact_operator')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            else:
                bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['RATES_FLAG'] = True
                    data['FORM_ORDER_FLAG'] = False
                    data['bank_acc'] = None
                #RATES_FLAG = True
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton(_('Обмен РУБЛЕЙ на ЕВРО'))
                b2 = types.KeyboardButton(_('Обмен USDT на ЕВРО'))
                b3 = types.KeyboardButton(_('Обмен ЕВРО на РУБЛИ'))
                b4 = types.KeyboardButton(_('Обмен USDT на РУБЛИ'))
                b5 = types.KeyboardButton(_('Обмен USDT на ГРИВНЫ'))
                b6 = types.KeyboardButton(_('Обмен USDT на ТЕНГЕ'))
                b7 = types.KeyboardButton(_('Обмен РУБЛЕЙ на ТЕНГЕ'))
                markup.add(b1, b2, b3, b4, b5, b6, b7)
                mess1 = _('Выберите валютную операцию, для которой хотите посмотреть курс')
                bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=markup)
    @bot.message_handler(commands=['contact_operator'])
    def contact_operator(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['FEEDBACK_FLAG'] = False
                data['FORM_ORDER_FLAG'] = False
            _ = get_user_translator(message.from_user.id)
            client_mess = _('Ваша заявка передана оператору. В ближайшее время с Вами свяжется наш сотрудник.')
            from_id = message.from_user.id
            first_name = message.from_user.first_name
            username = '@' + message.chat.username if message.chat.username is not None else '-'
            date = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            # date = datetime.utcfromtimestamp(message.json['date']).strftime('%Y-%m-%d %H:%M:%S')
            # TODO: НЕ ПЕРЕВОДИТЬ?
            operator_mess = '<em>Источник:</em> Alpha_TG_Bot\n' \
                            '<b>СВЯЗЬ С ОПЕРАТОРОМ</b>\n' \
                            '<em>Имя клиента:</em> {first_name}\nID клиента: {from_id}\n' \
                            '<em>Ник клиента:</em> {username}\n' \
                            '<em>Время формирования заявки:</em> {date}'.format(first_name=first_name, from_id=from_id,
                                                                                username=username, date=date)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
            markup.add(*menu_buttons)
            if '@' not in str(username):
                exc_mess = _(
                    '<b>У Вас нет имени пользователя, что не даст нам возможности связаться с Вами. Просьба заполнить в настройках пользователя.</b>')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, exc_mess, parse_mode='html', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, client_mess, parse_mode='html', reply_markup=markup)
                bot.send_message(GROUP_CHAT_ID, operator_mess, parse_mode='html')
            log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                    message.from_user.full_name, 'Связаться с оператором (contact_operator)', '-')
    @bot.message_handler(commands=['form_order'])
    def form_order(message):
        if message.chat.id != GROUP_CHAT_ID:
            _ = get_user_translator(message.from_user.id)
            #global FORM_ORDER_FLAG
            global OPER_FLAG_EUR_RUB, OPER_FLAG_EUR_RUB_BACK, OPER_FLAG_USDT_EURO, OPER_FLAG_USDT_EURO_BACK, BANK_FLAG, SUM_RUB_FLAG, SUM_USDT_FLAG, CITY_RE_FLAG, CITY_UE_FLAG, ANOTHER_CITY_RE_FLAG, ANOTHER_CITY_UE_FLAG, ORDER_CONFIRM_RE_FLAG, ORDER_CONFIRM_UE_FLAG, CHECK_ADDRESS, CHOOSE_BLOCKCHAIN
            global CASH_FLAG
            global FIND_USER_FLAG
            global NAME_FLAG
            global FEEDBACK_FLAG
            global REFERRAL_FLAG
            global MESSAGE_FLAG
            global USER_OWNER
            global CREATE_FLAG
            global SEX_FLAG
            global CITY_FLAG
            global USER_STATUS_FLAG
            #global FORM_ORDER_FLAG
            global ORDER_TIME_FLAG_RE
            global RUB_INFO
            global FRIEND_REF_FLAG_RE
            global DISCOUNT_RE
            global DISCOUNT_UE
            global RES_ORDER_FLAG_RE
            global ORDER_TIME_FLAG_UE
            global FRIEND_REF_FLAG_UE
            global RES_ORDER_FLAG_UE
            global REF_CDOE_UE, REF_CODE_RE
            global FEEDBACK_FLAG
            global add_username
            #global RATES_FLAG
            #RATES_FLAG = False
            FEEDBACK_FLAG = False
            PENDING_ORDER_FLAG = False
            RES_ORDER_FLAG_RE = False
            #FORM_ORDER_FLAG = True
            OPER_FLAG_EUR_RUB = False
            OPER_FLAG_EUR_RUB_BACK = False
            OPER_FLAG_USDT_EURO_BACK = False
            OPER_FLAG_USDT_EURO = False
            BANK_FLAG = False
            SUM_RUB_FLAG = False
            SUM_USDT_FLAG = False
            CHECK_ADDRESS = False
            CHOOSE_BLOCKCHAIN = False
            CITY_RE_FLAG = False
            CITY_UE_FLAG = False
            ANOTHER_CITY_RE_FLAG = False
            ANOTHER_CITY_UE_FLAG = False
            ORDER_CONFIRM_RE_FLAG = False
            ORDER_CONFIRM_UE_FLAG = False
            FIND_USER_FLAG = False
            ORDER_TIME_FLAG_UE = False
            FRIEND_REF_FLAG_UE = False
            RES_ORDER_FLAG_UE = False
            CASH_FLAG = False
            ORDER_TIME_FLAG_RE = False
            RUB_INFO = None
            FRIEND_REF_FLAG_RE = False
            DISCOUNT_RE = None
            DISCOUNT_UE = None
            REF_CODE_RE = None
            REF_CODE_UE = None
            add_username = ''
            #ACTIVE_CONTACT_LIST = scrab_contact_list()
            with open('contacts.json', 'r', encoding='utf8') as f:
                ACTIVE_CONTACT_LIST = json.load(f)
            bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['FORM_ORDER_FLAG'] = True
                data['RATES_FLAG'] = False
                data['FEEDBACK_FLAG'] = False
                data['PENDING_ORDER_FLAG'] = False
                data['RES_ORDER_FLAG_RE'] = False
                data['FORM_ORDER_FLAG'] = True
                data['OPER_FLAG_EUR_RUB'] = False
                data['OPER_FLAG_EUR_RUB_BACK'] = False
                data['OPER_FLAG_USDT_EURO_BACK'] = False
                data['OPER_FLAG_USDT_EURO'] = False
                data['BANK_FLAG'] = False
                data['SUM_RUB_FLAG'] = False
                data['SUM_USDT_FLAG'] = False
                data['CHECK_ADDRESS'] = False
                data['CHOOSE_BLOCKCHAIN'] = False
                data['CITY_RE_FLAG'] = False
                data['CITY_UE_FLAG'] = False
                data['ANOTHER_CITY_RE_FLAG'] = False
                data['ANOTHER_CITY_UE_FLAG'] = False
                data['ORDER_CONFIRM_RE_FLAG'] = False
                data['ORDER_CONFIRM_UE_FLAG'] = False
                data['FIND_USER_FLAG'] = False
                data['ORDER_TIME_FLAG_UE'] = False
                data['FRIEND_REF_FLAG_UE'] = False
                data['RES_ORDER_FLAG_UE'] = False
                data['CASH_FLAG'] = False
                data['ORDER_TIME_FLAG_RE'] = False
                data['RUB_INFO'] = None
                data['FRIEND_REF_FLAG_RE'] = False
                data['DISCOUNT_RE'] = None
                data['DISCOUNT_UE'] = None
                data['REF_CODE_RE'] = None
                data['REF_CODE_UE'] = None
                data['CASH_CITY'] = ''
            a = types.ReplyKeyboardRemove()
            username = '@' + message.chat.username if message.chat.username is not None else 'None'
            user_id = message.from_user.id
            all_user_ids = [user_info['user_ID'] for user_info in ACTIVE_CONTACT_LIST.values()]
            if (username in ACTIVE_CONTACT_LIST or user_id in all_user_ids) and ACTIVE_CONTACT_LIST[username][
                'CurrStatus'] != 'Активный':
                mess = _('Ваша учетная запись временно заблокирована в соответствии с правилами совершения операций с беспоставочными финансовыми инструментами. Для разблокировки Вашей учетной записи или формирования заявки на обмен Вы можете связаться с оператором /contact_operator')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            else:
                mess = _('Какая операция Вас интересует:\n' \
                        '1. Обмен РУБЛЕЙ на ЕВРО\n' \
                        '2. Обмен USDT на ЕВРО?\n' \
                        '3. Обмен ЕВРО на РУБЛИ\n' \
                        '4. Обмен USDT на РУБЛИ\n' \
                        '5. Обмен USDT на ГРИВНЫ\n' \
                        '6. Обмен USDT на ТЕНГЕ\n' \
                        '7. Обмен РУБЛЕЙ на ТЕНГЕ\n\n' \
                        '<em>Если ввели/выбрали неверное значение на одном из этапов формирования заявки, перезапустите команду: /form_order</em>')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                b1 = types.KeyboardButton(_('Обмен РУБЛЕЙ на ЕВРО'))
                b2 = types.KeyboardButton(_('Обмен USDT на ЕВРО'))
                b3 = types.KeyboardButton(_('Обмен ЕВРО на РУБЛИ'))
                b4 = types.KeyboardButton(_('Обмен USDT на РУБЛИ'))
                b5 = types.KeyboardButton(_('Обмен USDT на ГРИВНЫ'))
                b6 = types.KeyboardButton(_('Обмен USDT на ТЕНГЕ'))
                b7 = types.KeyboardButton(_('Обмен РУБЛЕЙ на ТЕНГЕ'))
                markup.add(b1, b2, b3, b4, b5, b6, b7, mb)
                if '@' not in str(username):
                    exc_mess = _(
                        '<b>У Вас нет имени пользователя (username), что не даст нам возможности связаться с Вами. Просьба заполнить в настройках пользователя.</b>')
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                    markup.add(*menu_buttons)
                    bot.send_message(message.chat.id, exc_mess, parse_mode='html', reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                    message.from_user.full_name, 'Обмен по заявке (form_order)', '-')            
    @bot.message_handler(content_types=['photo'])
    def get_photo(message):
        with open('contacts.json', 'r', encoding='utf8') as f:
                ACTIVE_CONTACT_LIST = json.load(f)
        if ADMIN_FLAG and operation == 'Закрытие сделок' and message.photo and message.text != 'Отмена':
            file_id = message.photo[-1].file_id
            photo_info = bot.get_file(file_id)
            downloaded_photo = bot.download_file(photo_info.file_path)
            with open(f'documents/{admin_seller_nik}_{deal_id}.jpg', 'wb') as new_file:
                new_file.write(downloaded_photo)
            image_url = upload_image_to_google_drive(image_file_path = f'documents/{admin_seller_nik}_{deal_id}.jpg',
                                                     name = f'{admin_seller_nik}_{deal_id}.jpg',
                                                     credentials_path = 'files/alphaexchange-c7c913c383ee.json',
                                                     folder_id = None)
            mess = 'Документ добавлен, пришлите еще или нажмите "Далее"'
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            markup.add('Далее')
            bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
    @bot.message_handler(content_types=['text'])
    def get_user_operation(message):
        _ = get_user_translator(message.from_user.id)
        with open('contacts.json', 'r', encoding='utf8') as f:
                ACTIVE_CONTACT_LIST = json.load(f)
        global BANK_RE, OPER_NAME_RE
        global OPER_FLAG_EUR_RUB, OPER_FLAG_EUR_RUB_BACK, OPER_FLAG_USDT_EURO, OPER_FLAG_USDT_EURO_BACK, BANK_FLAG, SUM_RUB_FLAG, ORDER_CONFIRM_RE_FLAG, ORDER_CONFIRM_UE_FLAG, SUM_USDT_FLAG, CHECK_ADDRESS, CHOOSE_BLOCKCHAIN
        global RUB_EURO_RATE, SUM_RUB_RE, SUM_EUR_RE
        global USDT_EURO_RATE, SUM_EUR_UE, SUM_USDT_UE
        global BLOCKCHAIN, ADDRESS, RISK_TRC
        global OPER_NAME_UE
        global CITY_RE, CITY_UE, CITY_RE_FLAG, CITY_UE_FLAG, ANOTHER_CITY_RE_FLAG, ANOTHER_CITY_UE_FLAG
        global DOCS_FLAG
        global PENDING_ORDER_FLAG
        global CASH_FLAG, CASH_CITY
        global FEEDBACK_FLAG
        global LANGUAGE_FLAG
        global REFERRAL_FLAG
        global MESSAGE_FLAG
        global USER_OWNER
        global CREATE_FLAG
        global SEX_FLAG
        global CITY_FLAG
        global USER_STATUS_FLAG
        global REFERRAL_OPTIONS_FLAG
        global REFERRAL_CHARGES_FLAG
        global REFERRAL_HIST_FLAG
        global REFERRAL_PERIOD_FLAG
        global DISCONT_PERIOD_FLAG
        global ORDER_TIME_FLAG_RE
        global ORDER_TIME_RE
        global ORDER_TIME_UE
        global RUB_INFO
        global FRIEND_REF_FLAG_RE
        global DISCOUNT_RE
        global DISCOUNT_UE
        global RES_ORDER_FLAG_RE
        global ORDER_TIME_FLAG_UE
        global FRIEND_REF_FLAG_UE
        global RES_ORDER_FLAG_UE
        global USDT_EURO_RATE_GS
        global REF_CODE_RE, REF_CODE_UE
        global FIND_USER_FLAG
        global NAME_FLAG
        global ADMIN_FLAG, KURATOR_BONUS_FLAG
        #global RATES_FLAG
        global add_username
        global admin_sum, deal_id, deal_id_dict, image_url, fact_get, fact_giv, end_flag, oper_type, admin_cross_rate, admin_seller_nik, admin_city, admin_currency, bonus_flag, comment, operation, bank_acc, admin_deals_city, admin_deals_city_flag
        cities = [_('Бар'),
                _('Бечичи'),
                _('Будва'),
                _('Котор'),
                _('Петровац'),
                _('Подгорица'),
                _('Тиват'),
                _('Ульцинь'),
                _('Херцег Нови'),
                _('Цетине')
                ]
        bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
        ru_bank_names = [_('Сбербанк'), _('Тинькофф'), _('Райффайзен'), _('Прочие')]
        ua_bank_names = [_('Monobank'), _('PUMB'), _('ПриватБанк'), _('А-Банк'), _('Izibank')]
        kzt_bank_names = [_('Kaspi Bank'), _('Halyk Bank'), _('ЦентрКредит Банк'), _('Jysan Bank'), _('Forte Bank'), _('Altyn Bank'), _('Freedom Bank')]
        # Команды для /start
        if message.text == _('🔁 Обмен по заявке') or message.text == _('Обмен по заявке'):
            form_order(message)
        elif message.text == _('📞 Связаться с оператором') or message.text == _('Связаться с оператором'):
            contact_operator(message)
        elif message.text == _('💸 Наши курсы') or message.text == _('Наши курсы'):
            get_rates(message)
        elif message.text == _('📘 Документы') or message.text == _('Документы'):
            bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['DOCS_FLAG'] = False
            documents(message)
        elif message.text == _('📽 Обучающее видео') or message.text == _('Обучающее видео'):
            tutorial(message)
        elif message.text == _('👨‍👦‍👦 Бонусная программа') or message.text == _('Бонусная программа'):
            refferal(message)
        elif message.text == _('⚙️ Команды') or message.text == _('Команды'):
            help(message)
        elif message.text == _('🕛 История сделок'):
            trans_history(message)
        elif message.text == _('Старт'):
            start(message)
        elif message.text == _('📨 Оставить отзыв') or message.text == _('Оставить отзыв'):
            feedback(message)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            ### Курсы валют
            if data.get('RATES_FLAG')==True and message.text in [_('Обмен РУБЛЕЙ на ЕВРО'), _('Обмен ЕВРО на РУБЛИ'), _('Обмен USDT на РУБЛИ'), _('Обмен USDT на ГРИВНЫ'), _('Обмен USDT на ТЕНГЕ'), _('Обмен РУБЛЕЙ на ТЕНГЕ')]:
                data['bank_acc'] = message.text
                mess = 'Выберите банк:'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                if message.text in [_('Обмен РУБЛЕЙ на ЕВРО'), _('Обмен ЕВРО на РУБЛИ'), _('Обмен USDT на РУБЛИ'), _('Обмен РУБЛЕЙ на ТЕНГЕ')]:
                    menu_buttons = form_menu_buttons(_(ru_bank_names))
                elif message.text in [_('Обмен USDT на ТЕНГЕ')]:
                    menu_buttons = form_menu_buttons(_(kzt_bank_names))
                elif message.text in [_('Обмен USDT на ГРИВНЫ')]:
                    menu_buttons = form_menu_buttons(_(ua_bank_names))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif data.get('RATES_FLAG')==True and (data['bank_acc'] is not None or message.text in [_('Обмен USDT на ЕВРО'), _('Обмен USDT на ЕВРО')]):
                if message.text in [_('Обмен USDT на ЕВРО')]:
                    data['bank_acc'] = message.text
                start = datetime.now()
                a = types.ReplyKeyboardRemove()
                mess1 = _('<em>Пожалуйста, подождите, происходит загрузка курсов валют...</em>')
                bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=a)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                discount = ACTIVE_CONTACT_LIST[username]['Discount'] if username in ACTIVE_CONTACT_LIST else '0'
                if data['bank_acc'] == _('Обмен РУБЛЕЙ на ЕВРО'):
                    rates_data = rates_funcs.get_rates_data(username, message.text)
                    rub_euro_rate_499 = round(rates_data[499] * (1 - float(discount.replace(',', '.')) / 100), 2) # курс до 500 евро
                    rub_euro_rate_999 = round(rates_data[999] * (1 - float(discount.replace(',', '.')) / 100), 2) # курс до 1000 евро
                    rub_euro_rate_2999 = round(rates_data[2999] * (1 - float(discount.replace(',', '.')) / 100), 2) # курс до 2999 евро
                    rub_euro_rate_9999 = round(rates_data[9999] * (1 - float(discount.replace(',', '.')) / 100), 2) # курс до 9999 евро
                    rub_euro_rate_10001 = round(rates_data[10001] * (1 - float(discount.replace(',', '.')) / 100), 2) # курс до 10001 евро
                    mess2 = _('<b>Курсы обмена с учетом скидки по вашему дисконтному коду </b>\n\n' \
                            '<em><b>Курс является индикативным и фиксируется в момент сделки</b></em>\n\n' \
                            '{bank_name}\n'
                            '<b>💳 RUB(<em>ваши</em>) ➡️ EUR(<em>наши</em>) 💶</b>\n' \
                            '📍 100-499 EUR: {rub_euro_rate_499}\n' \
                            '📍 500-999 EUR: {rub_euro_rate_999}\n' \
                            '📍 1000-2999 EUR: {rub_euro_rate_2999}\n' \
                            '📍 3000-9999 EUR: {rub_euro_rate_9999}\n' \
                            '📍 от 10000 EUR: {rub_euro_rate_10001}\n\n' \
                            '<b><em>Чтобы узнать о дополнительных возможностях заработка при привлечении клиентов, пожалуйста, воспользуйтесь командой ' \
                            'в меню "Бонусная программа" или введите /refferal</em></b>\n\n').format(
                        bank_name=message.text,
                        rub_euro_rate_499=rub_euro_rate_499,
                        rub_euro_rate_999=rub_euro_rate_999,
                        rub_euro_rate_2999=rub_euro_rate_2999,
                        rub_euro_rate_9999=rub_euro_rate_9999,
                        rub_euro_rate_10001=rub_euro_rate_10001)
                elif data['bank_acc'] == _('Обмен ЕВРО на РУБЛИ'):
                    rates_data_buy = rates_funcs.get_rates_buy_eur_data(currency_from='EUR_RUB', bank_name=message.text, username=username)
                    rub_euro_rate_buy_49999 = round(rates_data_buy[49999] * (1 - float(discount.replace(',', '.')) / 100), 2) # курс до 500 евро
                    rub_euro_rate_buy_99999 = round(rates_data_buy[99999] * (1 - float(discount.replace(',', '.')) / 100), 2) # курс до 1000 евро
                    rub_euro_rate_buy_299999 = round(rates_data_buy[299999] * (1 - float(discount.replace(',', '.')) / 100), 2) # курс до 2999 евро
                    rub_euro_rate_buy_999999 = round(rates_data_buy[999999] * (1 - float(discount.replace(',', '.')) / 100), 2) # курс до 9999 евро
                    rub_euro_rate_buy_1000001 = round(rates_data_buy[1000001] * (1 - float(discount.replace(',', '.')) / 100), 2) # курс до 10001 евро
                    mess2 = _('<b>Курсы обмена с учетом скидки по вашему дисконтному коду </b>\n\n' \
                            '<em><b>Курс является индикативным и фиксируется в момент сделки</b></em>\n\n' \
                            '{bank_name}\n'
                            '<b>💶 EUR=>RUB 💳</b>\n' \
                            '📌 100-499 EUR: {rub_euro_rate_buy_49999}\n' \
                            '📌 500-999 EUR: {rub_euro_rate_buy_99999}\n' \
                            '📌 1000-2999 EUR: {rub_euro_rate_buy_299999}\n' \
                            '📌 3000-9999 EUR: {rub_euro_rate_buy_999999}\n' \
                            '📌 от 10000 EUR: {rub_euro_rate_buy_1000001}\n\n' \
                            '<b><em>Чтобы узнать о дополнительных возможностях заработка при привлечении клиентов, пожалуйста, воспользуйтесь командой ' \
                            'в меню "Бонусная программа" или введите /refferal</em></b>\n\n').format(
                        bank_name=message.text,
                        rub_euro_rate_buy_49999=rub_euro_rate_buy_49999,
                        rub_euro_rate_buy_99999=rub_euro_rate_buy_99999,
                        rub_euro_rate_buy_299999=rub_euro_rate_buy_299999,
                        rub_euro_rate_buy_999999=rub_euro_rate_buy_999999,
                        rub_euro_rate_buy_1000001=rub_euro_rate_buy_1000001)
                elif data['bank_acc'] == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                    rates_data = rates_funcs.get_rates_rub_kzt_data(username, message.text)
                    rub_euro_rate_499 = round(rates_data[249999] * (1 - float(discount.replace(',', '.')) / 100), 4) # курс до 500 евро
                    rub_euro_rate_999 = round(rates_data[499999] * (1 - float(discount.replace(',', '.')) / 100), 4) # курс до 1000 евро
                    rub_euro_rate_2999 = round(rates_data[1499999] * (1 - float(discount.replace(',', '.')) / 100), 4) # курс до 2999 евро
                    rub_euro_rate_9999 = round(rates_data[4999999] * (1 - float(discount.replace(',', '.')) / 100), 4) # курс до 9999 евро
                    rub_euro_rate_10001 = round(rates_data[5000000] * (1 - float(discount.replace(',', '.')) / 100), 4) # курс до 10001 евро
                    mess2 = _('<b>Курсы обмена с учетом скидки по вашему дисконтному коду </b>\n\n' \
                            '<em><b>Курс является индикативным и фиксируется в момент сделки</b></em>\n\n' \
                            '{bank_name}\n'
                            '<b>💳 RUB(<em>ваши</em>) ➡️ KZT(<em>наши</em>) 💳</b>\n' \
                            '📍 100-499 KZT: {rub_euro_rate_499}\n' \
                            '📍 500-999 KZT: {rub_euro_rate_999}\n' \
                            '📍 1000-2999 KZT: {rub_euro_rate_2999}\n' \
                            '📍 3000-9999 KZT: {rub_euro_rate_9999}\n' \
                            '📍 от 10000 KZT: {rub_euro_rate_10001}\n\n' \
                            '<b><em>Чтобы узнать о дополнительных возможностях заработка при привлечении клиентов, пожалуйста, воспользуйтесь командой ' \
                            'в меню "Бонусная программа" или введите /refferal</em></b>\n\n').format(
                        bank_name=message.text,
                        rub_euro_rate_499=rub_euro_rate_499,
                        rub_euro_rate_999=rub_euro_rate_999,
                        rub_euro_rate_2999=rub_euro_rate_2999,
                        rub_euro_rate_9999=rub_euro_rate_9999,
                        rub_euro_rate_10001=rub_euro_rate_10001)
                elif data['bank_acc'] == _('Обмен USDT на ЕВРО'):
                    usdt_info = rates_funcs.compute_usdt_euro_amount(1, username)
                    usdt_euro_rate_1 = round(usdt_info['low_rate'] * (1 - float(discount.replace(',', '.')) / 100), 3)  # курс до 5000 евро
                    usdt_euro_rate_2 = round(usdt_info['high_rate'] * (1 - float(discount.replace(',', '.')) / 100), 3)  # курс свыше 5000 евро
                    mess2 = _('<b>Курсы обмена с учетом скидки по вашему дисконтному коду </b>\n\n' \
                            '<em><b>Курс является индикативным и фиксируется в момент сделки</b></em>\n\n' \
                            '<b>💵 USDT=>EUR 💶</b>\n' \
                            '🔸 100-4999 EUR: {usdt_euro_rate_1}\n' \
                            '🔸 от 5000 EUR: {usdt_euro_rate_2}\n\n' \
                            '<b><em>Чтобы узнать о дополнительных возможностях заработка при привлечении клиентов, пожалуйста, воспользуйтесь командой ' \
                            'в меню "Бонусная программа" или введите /refferal</em></b>\n\n').format(
                        usdt_euro_rate_1=usdt_euro_rate_1,
                        usdt_euro_rate_2=usdt_euro_rate_2)
                elif data['bank_acc'] == _('Обмен USDT на РУБЛИ'):
                    usdt_info = rates_funcs.compute_usdt_rub_amount(1, username, False, message.text)
                    usdt_euro_rate_1_buy = round(usdt_info['low_rate'] * (1 - float(discount.replace(',', '.')) / 100), 3)  # курс до 5000 евро
                    usdt_euro_rate_2_buy = round(usdt_info['high_rate'] * (1 - float(discount.replace(',', '.')) / 100), 3)  # курс свыше 5000 евро
                    mess2 = _('<b>Курсы обмена с учетом скидки по вашему дисконтному коду </b>\n\n' \
                            '<em><b>Курс является индикативным и фиксируется в момент сделки</b></em>\n\n' \
                            '{bank_name}\n'
                            '<b>💸 USDT=>RUB 💳</b>\n' \
                            '🔹 100-4999 USDT: {usdt_euro_rate_1_buy}\n' \
                            '🔹 от 5000 USDT: {usdt_euro_rate_2_buy}\n\n' \
                            '<b><em>Чтобы узнать о дополнительных возможностях заработка при привлечении клиентов, пожалуйста, воспользуйтесь командой ' \
                            'в меню "Бонусная программа" или введите /refferal</em></b>\n\n').format(
                        bank_name=message.text,
                        usdt_euro_rate_1_buy=usdt_euro_rate_1_buy,
                        usdt_euro_rate_2_buy=usdt_euro_rate_2_buy)
                elif data['bank_acc'] == _('Обмен USDT на ГРИВНЫ'):
                    usdt_info = rates_funcs.compute_usdt_uah_amount(1, username, message.text)
                    usdt_euro_rate_1 = round(usdt_info['low_rate'] * (1 - float(discount.replace(',', '.')) / 100), 3)  # курс до 5000 евро
                    usdt_euro_rate_2 = round(usdt_info['high_rate'] * (1 - float(discount.replace(',', '.')) / 100), 3)  # курс свыше 5000 евро
                    mess2 = _('<b>Курсы обмена с учетом скидки по вашему дисконтному коду </b>\n\n' \
                            '<em><b>Курс является индикативным и фиксируется в момент сделки</b></em>\n\n' \
                            '{bank_name}\n'
                            '<b>💵 USDT=>UAH 💳</b>\n' \
                            '🔸 4000-200000 UAH: {usdt_euro_rate_1}\n' \
                            '🔸 от 200000 UAH: {usdt_euro_rate_2}\n\n' \
                            '<b><em>Чтобы узнать о дополнительных возможностях заработка при привлечении клиентов, пожалуйста, воспользуйтесь командой ' \
                            'в меню "Бонусная программа" или введите /refferal</em></b>\n\n').format(
                        bank_name=message.text,
                        usdt_euro_rate_1=usdt_euro_rate_1,
                        usdt_euro_rate_2=usdt_euro_rate_2)
                elif data['bank_acc'] == _('Обмен USDT на ТЕНГЕ'):
                    usdt_info = rates_funcs.compute_usdt_kzt_amount(1, username, message.text)
                    usdt_euro_rate_1 = round(usdt_info['low_rate'] * (1 - float(discount.replace(',', '.')) / 100), 3)  # курс до 5000 евро
                    usdt_euro_rate_2 = round(usdt_info['high_rate'] * (1 - float(discount.replace(',', '.')) / 100), 3)  # курс свыше 5000 евро
                    mess2 = _('<b>Курсы обмена с учетом скидки по вашему дисконтному коду </b>\n\n' \
                            '<em><b>Курс является индикативным и фиксируется в момент сделки</b></em>\n\n' \
                            '{bank_name}\n'
                            '<b>💵 USDT=>KZT 💳</b>\n' \
                            '🔸 50000-2500000 KZT: {usdt_euro_rate_1}\n' \
                            '🔸 от 2500000 KZT: {usdt_euro_rate_2}\n\n' \
                            '<b><em>Чтобы узнать о дополнительных возможностях заработка при привлечении клиентов, пожалуйста, воспользуйтесь командой ' \
                            'в меню "Бонусная программа" или введите /refferal</em></b>\n\n').format(
                        bank_name=message.text,
                        usdt_euro_rate_1=usdt_euro_rate_1,
                        usdt_euro_rate_2=usdt_euro_rate_2)
                data['bank_acc'] = None
                #RATES_FLAG = False
                bot.set_state(message.from_user.id, MainMenue.main_menue, message.chat.id)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['RATES_FLAG'] = False
                    data['bank_acc'] = None
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess2, parse_mode='html', reply_markup=markup)
                end = datetime.now()
                print(f"Time taken in (hh:mm:ss.ms) is {end - start}")
                log_action(datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), message.from_user.username, message.from_user.id,
                    message.from_user.full_name, 'Наши курсы (get_rates)', '-')
            ### Панель администратора
            elif ADMIN_FLAG and message.text == 'Закрытие сделок':
                end_flag = False
                fact_giv = None
                fact_get = None
                comment = None
                oper_type = None
                image_url = ''
                mess = 'Выберите роль'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton('Отмена')
                operation = 'Закрытие сделок'
                markup.add('Куратор').add('P2P').add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and operation == 'Закрытие сделок' and message.text in ['Куратор', 'P2P']:
                last24 = get_last24h_trans(curator_type=message.text)
                deal_id_dict = last24[0]
                deals_mess = last24[1]
                if not deal_id_dict:
                    operation = None
                    mess = 'Нет доступных сделок'
                    username = '@' + message.chat.username if message.chat.username is not None else 'None'
                    menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    markup.add(*menu_buttons)
                else:
                    admin_seller_nik = message.text
                    mess = 'Выберите ID сделки\n\n' + deals_mess
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    b1 = types.KeyboardButton('Отмена')
                    markup.add(*list(deal_id_dict.values())).add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and operation == 'Закрытие сделок' and re.compile(r'^EX\d{8}$').match(message.text):
                deal_id = message.text
                mess = 'Выберите, что хотите сделать со сделкой'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton('Отмена')
                markup.add('Закрыть').add('Отменить').add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and operation == 'Закрытие сделок' and message.text in ['Закрыть'] and message.text != 'Отмена':
                oper_type = 'Закрыть'
                mess = 'Введите фактическую сумму в отдаваемой валюте'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton('Отмена')
                markup.add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and operation == 'Закрытие сделок' and message.text.isdigit() and fact_giv is None and message.text != 'Отмена':
                fact_giv = message.text
                mess = 'Введите фактическую сумму в получаемой валюте'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton('Отмена')
                end_flag = True
                markup.add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and operation == 'Закрытие сделок' and message.text == 'Отменить' and message.text != 'Отмена':
                oper_type = 'Отменить'
                fact_get = ''
                fact_giv = ''
                mess = 'Выберите причину отмены'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                b1 = types.KeyboardButton('Отмена')
                end_flag = True
                buttons_list = ['Больше не хочу совершать обмен', 'Клиент соответствует требованиям торговых условий', 'Увеличился курс обмена, отказ клиента',
                                'Проблемы со способом оплаты клиента', 'Не вышел на связь', 'Отмена в счет новой заявки', 'Отмена на стороне куратора']
                markup.add(*buttons_list).add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and operation == 'Закрытие сделок' and end_flag and message.text != 'Отмена' and message.text != 'Далее':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                if oper_type == 'Отменить':
                    comment = message.text
                else:
                    fact_get = message.text
                    comment = ''
                mess = 'Пришлите документ или нажмите "Далее"'
                b1 = types.KeyboardButton('Отмена')
                end_flag = True
                markup.add('Далее').add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and operation == 'Закрытие сделок' and message.text == 'Далее' and message.text != 'Отмена':
                status = 'Отменена' if oper_type == 'Отменить' else 'Выполнена'
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                gs_write_close_order(deal_id_dict, deal_id, username, fact_giv, fact_get, image_url, status, comment)
                mess = 'Запись создана'
                menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text == 'Партнерам' and ACTIVE_CONTACT_LIST['@' + message.chat.username]['ContactType'] == 'Партнер':
                mess = 'Выберите опцию'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton('Отмена')
                admin_seller_nik = 'Выбор'
                markup.add('SPLIT-1').add('SPLIT-2').add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and (message.text == 'Партнерам' and ACTIVE_CONTACT_LIST['@' + message.chat.username]['ContactOwnerTG'] in ['SPLIT-1', 'SPLIT-2'] or admin_seller_nik == 'Выбор'):
                if admin_seller_nik == 'Выбор':
                    admin_seller_nik = message.text
                else:
                    admin_seller_nik = ACTIVE_CONTACT_LIST['@' + message.chat.username]['ContactOwnerTG']
                mess = 'Выберите отчет, который хотите полуучить'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton('Отмена')
                markup.add('Список клиентов').add('Список сделок').add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text in ['Список клиентов', 'Список сделок'] and admin_seller_nik in ['SPLIT-1', 'SPLIT-2']:
                mess = 'Панель администратора'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST['@'+ message.chat.username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                markup.add(*menu_buttons)
                if message.text == 'Список сделок':
                    res = create_deals_report_for_split_xlsx(admin_seller_nik)
                else:
                    res = create_contacts_report_for_split_xlsx(admin_seller_nik)
                if res:
                    with open('Contacts.xlsx', 'rb') as doc:
                        bot.send_document(message.chat.id, doc)
                    
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text == 'Отчетность':
                mess = 'Выберите опцию'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton('Отмена')
                markup.add('Выплаты и бонусы').add('Отчет по сделкам').add('Отчет по кураторам').add('Баланс карт')
                if ACTIVE_CONTACT_LIST['@' + message.chat.username]['ContactType'] == 'Партнер' or ACTIVE_CONTACT_LIST['@' + message.chat.username]['ContactOwnerTG'] in ['SPLIT-1', 'SPLIT-2']:
                    markup.add('Партнерам').add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text == 'Трансфер денег':
                operation = message.text
                admin_sum = ''
                admin_city = None
                mess = 'Введите сумму в EUR'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton('Отмена')
                markup.add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and admin_sum is not None and operation == 'Трансфер денег' and admin_seller_nik is None and admin_city is None:
                admin_sum = message.text
                admin_seller_nik = ''
                mess = 'Введите ник получателя через @'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton('Отмена')
                markup.add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and admin_sum is not None and operation == 'Трансфер денег' and admin_seller_nik is not None and admin_city is None:
                admin_seller_nik = message.text
                admin_city = ''
                mess = 'Введите город'
                buttons = ['Бар', 'Бечичи', 'Будва', 'Котор', 'Петровац', 'Подгорица', 'Тиват',
                            'Ульцинь', 'Херцег Нови', 'Цетине', 'Отмена']
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(*buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and admin_sum is not None and operation == 'Трансфер денег' and admin_seller_nik is not None and admin_city is not None:
                admin_city = message.text
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                ref_code = ACTIVE_CONTACT_LIST[admin_seller_nik]['Discount_Number'] if admin_seller_nik in ACTIVE_CONTACT_LIST else ''
                mess = 'Операция добавлена'
                date = datetime.now(tz).strftime('%d.%m.%Y')
                with open('C:/Users/admin/PycharmProjects/BotMain_v4_Monex/app/deals_ids.json', 'r', encoding='utf8') as f:
                    DealID_num = json.load(f)
                    DealID_num["ZZ"] += 0.0000001
                    DealID = "ZZ" + (str(format(DealID_num["ZZ"], '.7f'))).replace('.','')
                with open('C:/Users/admin/PycharmProjects/BotMain_v4_Monex/app/deals_ids.json', 'w', encoding='utf8') as f:
                    json.dump(DealID_num, f, ensure_ascii=False, indent=2)
                usdt_eur_rate = rates_funcs.scrab_usdt_euro_rate(username, 1)
                add_row(DealID, date, date, username, '', operation, '', 'EUR', admin_sum, 'Наличные', '',
                        '', '/',
                        'EUR', 'Наличные', '', admin_seller_nik, ref_code, admin_city, '', '', '', '', '', '',
                        '', 'План', '', '', 'Трансфер денег', '', True, usdt_eur_rate, 1/usdt_eur_rate,)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                admin_sum, admin_cross_rate, admin_seller_nik, admin_city, admin_currency, comment, operation, bank_acc = None,  None, None, None, None, None, None, None
            elif ADMIN_FLAG and message.text == 'Действия пользователей':
                operation = 'Действия пользователей'
                mess = 'Если хотите посмотреть информации по конкретному пользователю, введите его ник через @\n'\
                                'Если хотите посмотреть информацию по всем пользователям, нажмине кнопку <em>Все</em>'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton('Все')
                b2 = types.KeyboardButton('Отмена')
                markup.add(b1, b2)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and operation == 'Действия пользователей':
                operation = ''
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                markup.add(*menu_buttons)
                if message.text != 'Отмена':
                    mess_logs_list = get_logs_history(message.text)
                    for mess in mess_logs_list:
                        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                else: bot.send_message(message.chat.id, 'Отменено', parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and (message.text in ["Отчет по сделкам", "Отчет по кураторам"] or (message.text in ['Бар', 'Бечичи', 'Будва', 'Котор', 'Петровац', 'Подгорица', 'Тиват',
                        'Ульцинь', 'Херцег Нови', 'Цетине', 'Все', 'Далее','О себе', 'О кураторе'] and operation in ["Отчет по сделкам", "Отчет по кураторам"])) and not admin_deals_city_flag:
                if message.text == 'Отчет по сделкам':
                    operation = message.text
                    mess = 'Введите города сделок'
                    buttons = ['Бар', 'Бечичи', 'Будва', 'Котор', 'Петровац', 'Подгорица', 'Тиват',
                            'Ульцинь', 'Херцег Нови', 'Цетине', 'Все', 'Далее', 'Отмена']
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    markup.add(*buttons)
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                elif message.text == 'Отчет по кураторам' and ACTIVE_CONTACT_LIST['@' + message.chat.username]['ContactType'] == 'Партнер':
                    operation = message.text
                    mess = 'Хотите посмотреть отчет о себе или о кураторе'
                    buttons = ['О себе', 'О кураторе', 'Отмена']
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    markup.add(*buttons)
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                elif message.text in ['О себе', 'О кураторе'] or message.text == 'Отчет по кураторам' and ACTIVE_CONTACT_LIST['@' + message.chat.username]['ContactType'] == 'Куратор':
                    if message.text == 'Отчет по кураторам':
                        operation = message.text
                        admin_seller_nik = '@' + message.chat.username
                    if ACTIVE_CONTACT_LIST['@' + message.chat.username]['ContactType'] == 'Партнер':
                        admin_seller_nik = '@' + message.chat.username if message.text == 'О себе' else 'Ввод куратора'
                    mess = 'Введите города сделок'
                    buttons = ['Бар', 'Бечичи', 'Будва', 'Котор', 'Петровац', 'Подгорица', 'Тиват',
                            'Ульцинь', 'Херцег Нови', 'Цетине', 'Все', 'Далее', 'Отмена']
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    markup.add(*buttons)
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                elif message.text == 'Все' :
                    admin_deals_city_flag = True
                    admin_deals_city = ['Бар', 'Бечичи', 'Будва', 'Котор', 'Петровац', 'Подгорица', 'Тиват',
                            'Ульцинь', 'Херцег Нови', 'Цетине', 'Отмена', 'Москва', '']
                    if operation == 'Отчет по сделкам':
                        mess = 'Если хотите посмотреть информации по конкретному пользователю, введите его ник через @\n'\
                                'Если хотите посмотреть информацию по всем пользователям, нажмине кнопку <em>Все</em>'
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                        b1 = types.KeyboardButton('Все')
                        b2 = types.KeyboardButton('Отмена')
                        markup.add(b1, b2)
                        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                    elif admin_seller_nik == 'Ввод куратора' and operation != 'Отчет по сделкам':
                        mess = 'Введите ник куратора через @'
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                        b2 = types.KeyboardButton('Отмена')
                        markup.add(b2)
                        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                    else:
                        admin_deals_city_flag = True 
                elif message.text == 'Далее':
                    if len(admin_deals_city) > 0 and operation != 'Отчет по кураторам':
                        admin_deals_city_flag = True 
                        mess = 'Если хотите посмотреть информации по конкретному пользователю, введите его ник через @\n'\
                                'Если хотите посмотреть информацию по всем пользователям, нажмине кнопку <em>Все</em>'
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                        b1 = types.KeyboardButton('Все')
                        b2 = types.KeyboardButton('Отмена')
                        markup.add(b1, b2)
                    elif len(admin_deals_city) > 0 and admin_seller_nik == 'Ввод куратора':
                        admin_deals_city_flag = True 
                        mess = 'Введите ник куратора через @'
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                        b2 = types.KeyboardButton('Отмена')
                        markup.add(b2)
                    else: 
                        admin_deals_city_flag = False
                        mess = 'Выберете хотя бы 1 город'
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                        buttons = ['Бар', 'Бечичи', 'Будва', 'Котор', 'Петровац', 'Подгорица', 'Тиват',
                            'Ульцинь', 'Херцег Нови', 'Цетине', 'Все', 'Далее', 'Отмена']
                        markup.add(*buttons)
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                else:
                    admin_deals_city.append(message.text)
            elif ADMIN_FLAG and admin_deals_city_flag and message.text != 'Отмена':
                res = False
                try:
                    if operation == 'Отчет по кураторам' and admin_seller_nik != 'Ввод куратора':
                        res = create_deals_xlsx(message.text, admin_deals_city, admin_seller_nik)
                    elif operation == 'Отчет по кураторам' and admin_seller_nik == 'Ввод куратора':
                        res = create_deals_xlsx('', admin_deals_city, message.text)
                    else:
                        res = create_deals_xlsx(message.text, admin_deals_city, admin_seller_nik)
                    mess = 'Отчет сформирован успешно!' if res else 'Не удалось найти сделок по данным критериям'
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    username = '@' + message.chat.username if message.chat.username is not None else 'None'
                    menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                    markup.add(*menu_buttons)
                except Exception as e:
                    print('Exception: ' + str(e))
                    mess = 'Не удалось составить отчет для данного пользователя'
                    b1 = types.KeyboardButton('Отмена')
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    markup.add(b1)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                if res:
                    with open('Deals.xlsx', 'rb') as doc:
                        bot.send_document(message.chat.id, doc)
                admin_deals_city_flag = False
                admin_deals_city = []
                admin_seller_nik = None
                operation = None
            elif ADMIN_FLAG and (message.text in ['Откуп', 'Снятие с карт']) and admin_currency is None and admin_sum is None and message.text != 'Отмена':
                operation = message.text
                mess = 'Выберите валюту'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add('EUR').add('RSD').add('Отмена')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and ((operation in ['Откуп', 'Снятие с карт'] and admin_sum is None) or admin_currency is not None and admin_sum is None or message.text == 'Выплата бонусов') and message.text != 'Отмена':
                admin_sum = 0
                if admin_currency is None and message.text != 'Выплата бонусов':
                    admin_currency = message.text
                    mess = f'Введите сумму в {admin_currency}'
                else: 
                    if message.text != 'Выплата бонусов':
                        admin_currency = message.text  
                    else:
                        admin_currency = 'EUR'
                        bonus_flag = True
                    mess = f'Введите сумму в {admin_currency}'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add('Отмена')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)

            elif ADMIN_FLAG and admin_sum is not None and admin_cross_rate is None and admin_seller_nik is None and admin_city is None and message.text != 'Отмена':
                admin_sum = message.text.replace('.',',')
                if admin_currency is not None and operation in ['Откуп', 'Снятие с карт']:
                    admin_cross_rate = 0
                    mess = 'Введите кросс курс'
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add('Отмена')
                else:
                    username = '@' + message.chat.username if message.chat.username is not None else 'None'
                    ref_code = ACTIVE_CONTACT_LIST[username]['Discount_Number'] if username in ACTIVE_CONTACT_LIST else ''
                    mess = 'Операция добавлена'
                    date = datetime.now(tz).strftime('%d.%m.%Y')
                    if bonus_flag:
                        deal_type = 'Выплата бонусов'
                        deal_status = 'План'
                        comment = ''
                        balance = get_bonus_history(username, True, False)
                        if float(admin_sum) > float(str(balance).replace(',','.')):
                            balance_flag = False
                            mess = 'Баланса недостаточно, введите другую сумму'
                        else: 
                            balance_flag = True
                    else:
                        balance_flag = True
                        deal_type = 'Расходы'
                        deal_status = 'План'
                    if balance_flag:
                        with open('C:/Users/admin/PycharmProjects/BotMain_v4_Monex/app/deals_ids.json', 'r', encoding='utf8') as f:
                            DealID_num = json.load(f)
                            DealID_num["ZZ"] += 0.0000001
                            DealID = "ZZ" + (str(format(DealID_num["ZZ"], '.7f'))).replace('.','')
                        with open('C:/Users/admin/PycharmProjects/BotMain_v4_Monex/app/deals_ids.json', 'w', encoding='utf8') as f:
                            json.dump(DealID_num, f, ensure_ascii=False, indent=2)
                        usdt_eur_rate = rates_funcs.scrab_usdt_euro_rate(username, 1)
                        add_row(DealID, date, date, username, '', deal_type, '', admin_currency, admin_sum, 'Наличные', '',
                                '', '/',
                                '', 'Наличные', '', username, ref_code, '', '', '', '', '', '', '',
                                '', deal_status, '', comment, 'Расходы', '', True, usdt_eur_rate, 1/usdt_eur_rate)
                        add_border()
                        admin_sum, admin_cross_rate, admin_seller_nik, admin_city, admin_currency, comment, operation, bank_acc = None,  None, None, None, None, None, None, None
                        balance_flag = False
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                        username = '@' + message.chat.username if message.chat.username is not None else 'None'
                        menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                        markup.add(*menu_buttons)
                    else:
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                        buttons = types.KeyboardButton('Отмена')
                        markup.add(buttons)
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                        markup.add(buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and admin_sum is not None and admin_cross_rate is not None and admin_seller_nik is None and admin_city is None and message.text != 'Отмена' and operation == 'Откуп':
                admin_cross_rate = message.text.replace('.',',')
                admin_seller_nik = ''
                mess = 'Введите ник продавца'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add('Отмена')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and admin_sum is not None and admin_cross_rate is not None and (admin_seller_nik is not None or operation == 'Снятие с карт') and admin_city is None and message.text != 'Отмена':
                if operation == 'Снятие с карт':
                    admin_cross_rate = message.text.replace('.',',')
                    admin_seller_nik = '@' + message.chat.username if message.chat.username is not None else 'None'
                else:
                    admin_seller_nik = message.text
                    bank_acc = ''
                admin_city = ''
                mess = 'Введите город'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add('Отмена')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and admin_sum is not None and admin_cross_rate is not None and admin_seller_nik is not None and admin_city is not None and bank_acc is not None and message.text != 'Отмена':
                if operation == 'Откуп':
                    admin_city = message.text
                    bank_acc = 'Наличные'
                else:
                    bank_acc = message.text
                mess = 'Операция добавлена'
                date = datetime.now(tz).strftime('%d.%m.%Y')
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                curator = ACTIVE_CONTACT_LIST[username]['ContactDealer'] if username in ACTIVE_CONTACT_LIST else ''
                ref_code = ACTIVE_CONTACT_LIST[username]['Discount_Number'] if username in ACTIVE_CONTACT_LIST else ''
                seller_ref_code = ACTIVE_CONTACT_LIST[admin_seller_nik]['Discount_Number'] if admin_seller_nik in ACTIVE_CONTACT_LIST else ''
                date = datetime.now(tz).strftime('%d.%m.%Y')
                usdt_info = rates_funcs.compute_usdt_rsd_amount(1, username) if admin_currency == 'RSD' else rates_funcs.compute_usdt_euro_amount(1, username)
                data['USDT_EURO_RATE_GS'] = usdt_info['usdt_eur_rate_gs']
                with open('C:/Users/admin/PycharmProjects/BotMain_v4_Monex/app/deals_ids.json', 'r', encoding='utf8') as f:
                    DealID_num = json.load(f)
                    DealID_num["ZZ"] += 0.0000001
                    DealID = "ZZ" + (str(format(DealID_num["ZZ"], '.7f'))).replace('.','')
                with open('C:/Users/admin/PycharmProjects/BotMain_v4_Monex/app/deals_ids.json', 'w', encoding='utf8') as f:
                    json.dump(DealID_num, f, ensure_ascii=False, indent=2)
                add_row(DealID, date, date, username, '', operation, f'USDT=>{admin_currency}', 'USDT', admin_sum, 'Binance', '',
                        admin_cross_rate, '/',
                        admin_currency, bank_acc, '', admin_seller_nik, seller_ref_code, admin_city, '', '', '', '', '', '',
                        '', 'План', '', '', 'admin', '', True, data['USDT_EURO_RATE_GS'], 1/data['USDT_EURO_RATE_GS'])
                add_row(DealID, date, date, username, '', operation, f'USDT=>{admin_currency}', admin_currency, '', bank_acc, '',
                        data['USDT_EURO_RATE_GS'], admin_sum,
                        admin_currency, 'Наличные', '', username, ref_code, admin_city, '', '', '', '', '', '',
                        '', 'План', '', '', 'admin', '', '', '', '')
                add_row(DealID, date, date, username, '', operation, f'USDT=>{admin_currency}', admin_currency, '', 'Наличные', '',
                        data['USDT_EURO_RATE_GS']*0.993, admin_sum,
                        admin_currency, bank_acc, '', username, ref_code, admin_city, 'NEW', '', '', '', '', '',
                        '', 'РасчБонПлан', '', '', 'admin2', '', '', '', '')
                eur_rate = 1 if admin_currency == 'EUR' else rates_funcs.get_fiat_rates_tradingview()['RSD_EUR']
                calculate_indexes(operation, False, eur_rate)
                add_border()
                admin_sum, admin_cross_rate, admin_seller_nik, admin_city, admin_currency, comment, operation, bank_acc = None,  None, None, None, None, None, None, None
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and admin_sum is not None and admin_cross_rate is not None and admin_seller_nik is not None and admin_city is not None and bank_acc is None and message.text != 'Отмена':
                admin_city = message.text
                bank_acc = ''
                mess = 'Введите 4 последние цифры карты'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add('Отмена')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text == 'Расходы':
                comment = ''
                mess = 'Введите комментрарий к расходам'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add('Отмена')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and comment is not None and admin_sum is None and admin_cross_rate is None and admin_seller_nik is None and admin_city is None and message.text != 'Отмена':
                admin_currency = ''
                comment = message.text
                mess = 'Выберете валюту'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add('RUB').add('USDT').add('EUR').add('Отмена')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text == 'Баланс валют':
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                mess = check_balance(username)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text == 'Баланс карт':
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                mess = cards_balance(username)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text == 'Выплаты и бонусы':
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Обменник']:
                    mess = get_bonus_history(username, False, False)
                    username = '@' + message.chat.username if message.chat.username is not None else 'None'
                    menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                    markup.add(*menu_buttons)
                elif ACTIVE_CONTACT_LIST[username]['ContactType'] == 'Партнер':
                    mess = 'Хотите посмотреть информацию о себе, о кураторе или обменнике?'
                    markup.add('О себе').add('О другом пользователе')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text in ['О себе', 'О другом пользователе']:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                if message.text == 'О себе':
                    mess = 'Хотите посмотреть информацию по себе, как о кураторе или партнере?'
                    markup.add('Как о партнере').add('Как о кураторе')
                else:
                    KURATOR_BONUS_FLAG = True
                    mess = 'Введите имя пользователя через @'
                    markup = types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text in ['Как о кураторе', 'Как о партнере']:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                mess = get_bonus_history(username, False, False) if message.text == 'Как о кураторе' else get_bonus_history(username, False, True)
                menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and KURATOR_BONUS_FLAG:
                KURATOR_BONUS_FLAG = False
                username = message.text
                mess = get_bonus_history(username, False, False)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text == 'Закрыть панель':
                ADMIN_FLAG = False
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                mess = '<b>Панель администратора закрыта</b>'
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif ADMIN_FLAG and message.text == 'Отмена':
                mess = 'Отменено'
                admin_sum, admin_cross_rate, admin_seller_nik, admin_city, admin_currency, comment, operation, bank_acc = None,  None, None, None, None, None, None, None
                bonus_flag = False
                admin_deals_city_flag = False
                admin_deals_city = []
                KURATOR_BONUS_FLAG = False
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                menu_buttons = form_menu_buttons(ADMIN_MENU_BUTTONS) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else form_menu_buttons(ADMIN_MENU_BUTTONS_EX)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            ### Рассылка сообщений
            if message.chat.id == -610534834 and not MESSAGE_FLAG and message.text != 'Видео':
                MESSAGE_FLAG = True
                USER_OWNER = False
                SEX_FLAG = False
                USER_STATUS_FLAG = False
                CITY_FLAG = False
                global message_text
                message_text = message.text
                global spam_message_id
                spam_message_id = message.message_id
                mess1 = 'Выберете принадлежность клиентов'
                buttons = ['@MonexCapital_MNE', '@vadimosx', 'NEW', 'Все']
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(*buttons)
                bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=markup)
            elif message.chat.id == -610534834 and MESSAGE_FLAG and not USER_OWNER and not SEX_FLAG and not USER_STATUS_FLAG and not CITY_FLAG and message.text != 'Отменить':
                USER_OWNER = True
                global message_user_owner
                if message.text == 'Все':
                    message_user_owner = ['@MonexCapital_MNE', '@vadimosx', 'NEW', 'Все']
                else:
                    message_user_owner.append(message.text)
                mess1 = 'Выберете город получателей'
                buttons = ['Бар', 'Бечичи', 'Будва', 'Котор', 'Петровац', 'Подгорица', 'Тиват',
                           'Ульцинь', 'Херцег Нови', 'Цетине', 'Все', 'Далее']
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(*buttons)
                bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=markup)
            elif message.chat.id == -610534834 and MESSAGE_FLAG and USER_OWNER and not SEX_FLAG and not USER_STATUS_FLAG and not CITY_FLAG and message.text != 'Отменить':
                global message_city
                if message.text == 'Далее':
                    CITY_FLAG = True
                    mess1 = 'Выберете пол получателей'
                    b1 = types.KeyboardButton('Мужчины')
                    b2 = types.KeyboardButton('Женщины')
                    b3 = types.KeyboardButton('Все')
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    markup.add(b1, b2, b3)
                    bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=markup)
                elif message.text == 'Все':
                    message_city = ['Бар', 'Бечичи', 'Будва', 'Котор', 'Петровац', 'Подгорица', 'Тиват',
                                    'Ульцинь', 'Херцег Нови', 'Цетине', 'Все', 'Далее', 'Monex_TG_Bot']
                    CITY_FLAG = True
                    mess1 = 'Выберете пол получателей'
                    b1 = types.KeyboardButton('Мужчины')
                    b2 = types.KeyboardButton('Женщины')
                    b3 = types.KeyboardButton('Все')
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    markup.add(b1, b2, b3)
                    bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=markup)
                else:
                    message_city.append(message.text)
            elif message.chat.id == -610534834 and message.text in ['Мужчины', 'Женщины',
                                                                     'Все'] and USER_OWNER and MESSAGE_FLAG and not SEX_FLAG and not USER_STATUS_FLAG and CITY_FLAG and message.text != 'Отменить':
                SEX_FLAG = True
                global message_sex
                if message.text == 'Мужчины':
                    message_sex.append('M')
                elif message.text == 'Женщины':
                    message_sex.append('W')
                else:
                    message_sex.append('M')
                    message_sex.append('W')
                    message_sex.append('')
                    message_sex.append('-')
                mess1 = 'Выберете количество дней с последнего обмена получателей'
                b1 = types.KeyboardButton('До 30 дней')
                b2 = types.KeyboardButton('От 30 до 60 дней')
                b3 = types.KeyboardButton('Более 60 дней')
                b4 = types.KeyboardButton('Все')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b1, b2, b3, b4)
                bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=markup)
            elif message.chat.id == -610534834 and message.text in ['До 30 дней', 'От 30 до 60 дней', 'Более 60 дней',
                                                                     'Все'] and USER_OWNER and MESSAGE_FLAG and SEX_FLAG and not USER_STATUS_FLAG and CITY_FLAG and message.text != 'Отменить':
                USER_STATUS_FLAG = True
                global message_last_trans
                if message.text == 'До 30 дней':
                    message_last_trans = [0, 30]
                elif message.text == 'От 30 до 60 дней':
                    message_last_trans = [30, 60]
                elif message.text == 'Более 60 дней':
                    message_last_trans = [60, 1000000]
                else:
                    message_last_trans = [-10, 1000000]
                mess1 = 'Выберете статус получателей'
                b1 = types.KeyboardButton('Базовый')
                b2 = types.KeyboardButton('Бронзовый')
                b3 = types.KeyboardButton('Серебряный')
                b4 = types.KeyboardButton('Золотой')
                b5 = types.KeyboardButton('Все')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b1, b2, b3, b4, b5)
                bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=markup)
            elif message.chat.id == -610534834 and message.text in ['Базовый', 'Бронзовый', 'Серебряный', 'Золотой',
                                                                     'Все'] and USER_OWNER and MESSAGE_FLAG and SEX_FLAG and USER_STATUS_FLAG and CITY_FLAG and message.text != 'Отменить':
                global message_user_status
                if message.text == 'Все':
                    message_user_status = ['Базовый', 'Бронзовый', 'Серебряный', 'Золотой']
                else:
                    message_user_status = [message.text]
                mess1 = f'Начать рассылку с текстом: <em>"{message_text}"</em>? \n' \
                        f'Пол клиентов: {", ".join(str(sex) for sex in message_sex)} \n' \
                        f'Города клиентов: {", ".join(str(city) for city in message_city)} \n' \
                        f'Дней с поледнего обмена: {" От/До ".join(str(trans) for trans in message_last_trans)} \n' \
                        f'Категирии клиентов: {", ".join(str(status) for status in message_user_status)}'
                b1 = types.KeyboardButton('Начать рассылку')
                b2 = types.KeyboardButton('Отменить')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                markup.add(b1, b2)
                bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=markup)
            elif message.chat.id == -610534834 and (
                    message.text == 'Начать рассылку' and USER_OWNER and MESSAGE_FLAG and SEX_FLAG and USER_STATUS_FLAG and CITY_FLAG or message.text == 'Видео') and message.text != 'Отменить':
                user_id_list = []
                if message.text != 'Видео':
                    mess1 = message_text
                    mess2 = f'Рассылка с текстом: <em>"{mess1}"</em> прошла успешно для <em>{len(user_id_list)} пользователей</em> '
                    for id in scrab_contact_list().values():
                        if 'DateLast' in id.keys():
                            if id['DateLast'] == '':
                                id['DateLast'] = -1
                            if id['Sex'] in message_sex and id['City'] in message_city and id[
                                'ContactOwnerTG'] in message_user_owner and id[
                                'DiscClientCategory'] in message_user_status and int(id['DateLast']) > \
                                    message_last_trans[0] and int(id['DateLast']) < message_last_trans[1]:
                                user_id_list.append(id['user_ID'])
                        else:
                            pass
                else:
                    mess2 = f'Рассылка ВИДЕО прошла успешно для <em>{len(user_id_list)} пользователей</em> '
                    user_id_list = [id['user_ID'] for id in scrab_contact_list().values()]
                MESSAGE_FLAG = False
                SEX_FLAG = False
                USER_STATUS_FLAG = False
                CITY_FLAG = False
                USER_OWNER = False
                message_city = []
                message_sex = []
                message_user_status = []
                message_user_owner = []
                mess3 = 'Чтобы создать новую рассылку, ответьте на это сообщение текстом, который нужно разослать'
                for user_id in user_id_list:
                    if user_id != '':
                        try:
                            if message.text != 'Видео':
                                bot.forward_message(user_id, -610534834, spam_message_id)
                            else:
                                bot.send_video(chat_id=user_id,
                                               video=open('C:/Users/admin/Documents/AlphaCapitalHowToBot1.mp4', 'rb'),
                                               supports_streaming=True, width=1080, height=1920)
                        except Exception as e:
                            pass
                bot.send_message(message.chat.id, mess2, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(message.chat.id, mess3, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
            elif message.chat.id == -610534834 and MESSAGE_FLAG and message.text == 'Отменить':
                    MESSAGE_FLAG = False
                    SEX_FLAG = False
                    USER_STATUS_FLAG = False
                    CITY_FLAG = False
                    USER_OWNER = False
                    message_city = []
                    message_sex = []
                    message_user_status = []
                    message_user_owner = []
                    mess1 = 'Чтобы создать новую рассылку, ответьте на это сообщение текстом, который нужно разослать'
                    bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
            # Сценарий Бонусной программы
            if data.get('REFERRAL_FLAG') and message.text == _('Карта бонусной программы'):
                data['DISCONT_PERIOD_FLAG'] = False
                data['REFERRAL_PERIOD_FLAG'] = False
                #ACTIVE_CONTACT_LIST = scrab_contact_list()
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                a = types.ReplyKeyboardRemove()
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                all_user_ids = [user_info['user_ID'] for user_info in ACTIVE_CONTACT_LIST.values()]
                user_info = ACTIVE_CONTACT_LIST[username]
                Discount_Number = user_info['Discount_Number']  # Номер по программе лояльности
                DiscTurnoverUSDT = user_info['DiscTurnoverUSDT']  # Накопленный итог обмена USDT
                DiscTurnover3MUSDT = user_info['DiscTurnover3MUSDT']  # Обмен 3 мес USDT
                DiscTurnoverRUB = user_info['DiscTurnoverRUB']  # Накопленный итог обмена RUB
                DiscTurnover3MRUB = user_info['DiscTurnover3MRUB']  # Обмен 3 мес RUB
                Discount = str(float(user_info['Discount'].replace(',', '.'))*100)+'%'  # Размер скидки
                DiscClientCategory = user_info['DiscClientCategory']  # Категория клиента
                DiscClientCategoryUSDT = user_info['DiscClientCategoryUSDT']  # Категория клиента USDT
                DiscClientCategoryRUB = user_info['DiscClientCategoryRUB']  # Категория клиента RUB
                Referral_Number = user_info['Referral_Number']  # Номер по реферальной программе
                ReferalTurnoverUSDT = user_info['ReferalTurnoverUSDT']
                ReferalTurnover3MUSDT = user_info['ReferalTurnover3MUSDT']
                ReferalTurnoverRUB = user_info['ReferalTurnoverRUB']
                ReferalTurnover3MRUB = user_info['ReferalTurnover3MRUB']
                mess = _('<b>Ваша текущая карточка программы лояльности:</b> \n\n' \
                        '<b>Номер по дисконтной программе:</b> {Discount_Number}\n' \
                        '<em>Накопленный итог обмена USDT:</em> {DiscTurnoverUSDT}\n' \
                        '<em>Обмен 3 мес USDT:</em> {DiscTurnover3MUSDT}\n' \
                        '<em>Накопленный итог обмена RUB:</em> {DiscTurnoverRUB}\n' \
                        '<em>Обмен 3 мес RUB:</em> {DiscTurnover3MRUB}\n' \
                        '<em>Размер скидки:</em> {Discount}\n' \
                        '<em>Категория клиента:</em> {DiscClientCategory}\n' \
                        '<b>Номер по реферальной программе :</b> {Referral_Number}\n' \
                        '<em>Накопленный итог обмена USDT:</em> {ReferalTurnoverUSDT}\n' \
                        '<em>Обмен 3 мес USDT:</em> {ReferalTurnover3MUSDT}\n' \
                        '<em>Накопленный итог обмена RUB:</em> {ReferalTurnoverRUB}\n' \
                        '<em>Обмен 3 мес RUB:</em> {ReferalTurnover3MRUB}\n').format(Discount_Number=Discount_Number,
                                                                                    DiscTurnoverUSDT=DiscTurnoverUSDT,
                                                                                    DiscTurnover3MUSDT=DiscTurnover3MUSDT,
                                                                                    DiscTurnoverRUB=DiscTurnoverRUB,
                                                                                    DiscTurnover3MRUB=DiscTurnover3MRUB,
                                                                                    Discount=Discount,
                                                                                    DiscClientCategory=DiscClientCategory,
                                                                                    Referral_Number=Referral_Number,
                                                                                    ReferalTurnoverUSDT=ReferalTurnoverUSDT,
                                                                                    ReferalTurnover3MUSDT=ReferalTurnover3MUSDT,
                                                                                    ReferalTurnoverRUB=ReferalTurnoverRUB,
                                                                                    ReferalTurnover3MRUB=ReferalTurnover3MRUB)
                mess1 = check_status(username, _)
                b1 = types.KeyboardButton(_('Реферальная программа'))
                b2 = types.KeyboardButton(_('Дисконтная программа'))
                b3 = types.KeyboardButton(_('Карта бонусной программы'))
                b4 = types.KeyboardButton(_('Главное меню'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b3, b2, b1, b4)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=markup)
            # Информация по реферальной программе
            elif data.get('REFERRAL_FLAG') and message.text == _('Реферальная программа'):
                data['REFERRAL_OPTIONS_FLAG'] = True
                mess = _('Здесь Вы можете посмотреть историю обменов, историю начислений и выплат по реферальному коду.\n'
                        'Пожалуйста, выберите пункт меню: ')
                b1 = types.KeyboardButton(_('История сделок'))
                b2 = types.KeyboardButton(_('История начислений и выплат'))
                b3 = types.KeyboardButton(_('Главное меню'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                markup.add(b1, b2, b3)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # Информация по реферальному коду
            elif data.get('REFERRAL_FLAG') and data.get('REFERRAL_OPTIONS_FLAG') and message.text in [_('История сделок'), _('История начислений и выплат')]:
                if message.text == _('История начислений и выплат'):
                    data['REFERRAL_CHARGES_FLAG'] = True
                    data['REFERRAL_HIST_FLAG'] = False
                else:
                    data['REFERRAL_HIST_FLAG'] = True
                    data['REFERRAL_CHARGES_FLAG'] = False
                mess = _('Пожалуйста, выберите период времени, за который хотите посмтреть отчет.')
                b1 = types.KeyboardButton(_('За месяц'))
                b2 = types.KeyboardButton(_('За 3 месяца'))
                b3 = types.KeyboardButton(_('За все время'))
                b4 = types.KeyboardButton(_('Назад'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b1, b2, b3, b4)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif data.get('REFERRAL_FLAG') and data.get('REFERRAL_OPTIONS_FLAG') and (data.get('REFERRAL_CHARGES_FLAG') or data.get('REFERRAL_HIST_FLAG')) and message.text in [_('За месяц'), _('За 3 месяца'), _('За все время')]:
                #ACTIVE_CONTACT_LIST = scrab_contact_list()
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                a = types.ReplyKeyboardRemove()
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                user_info = ACTIVE_CONTACT_LIST[username]
                Referral_Number = user_info['Referral_Number']
                if data.get('REFERRAL_CHARGES_FLAG'):
                    if message.text == _('За месяц'):
                        period = _('за месяц')
                        ReferalTurnoverUSDT = float(
                            re.sub(r'[^0-9,]', '', user_info['ReferalTurnover30DUSDT']).replace(',', '.'))
                        ReferalTurnoverRUB = float(re.sub(r'[^0-9,]', '', user_info['ReferalTurnover30DRUB']).replace(',', '.'))
                        TurnoverQty = user_info['Turnover30DQty']
                        ReferalBenefitEUR = float(re.sub(r'[^0-9,]', '', user_info['ReferalBenefit30DEUR']).replace(',', '.'))
                        ReferalPayoutEUR = -float(re.sub(r'[^0-9,]', '', user_info['ReferalPayout30DEUR']).replace(',', '.'))
                        OstStart = (float(re.sub(r'[^0-9,]', '', user_info['ReferalBenefitEUR']).replace(',', '.')) - float(
                            re.sub(r'[^0-9,]', '', user_info['ReferalBenefit30DEUR']).replace(',', '.'))) - (float(
                            re.sub(r'[^0-9,]', '', user_info['ReferalPayoutEUR']).replace(',', '.')) - float(
                            re.sub(r'[^0-9,]', '', user_info['ReferalPayout30DEUR']).replace(',', '.')))
                        OstEnd = round(OstStart + float(ReferalBenefitEUR) + float(ReferalPayoutEUR), 2)
                    elif message.text == _('За все время'):
                        period = _('за все время')
                        ReferalTurnoverUSDT = float(
                            re.sub(r'[^0-9,]', '', user_info['ReferalTurnoverUSDT']).replace(',', '.'))
                        ReferalTurnoverRUB = float(re.sub(r'[^0-9,]', '', user_info['ReferalTurnoverRUB']).replace(',', '.'))
                        TurnoverQty = user_info['TurnoverQty']
                        ReferalBenefitEUR = float(re.sub(r'[^0-9,]', '', user_info['ReferalBenefitEUR']).replace(',', '.'))
                        ReferalPayoutEUR = -float(re.sub(r'[^0-9,]', '', user_info['ReferalPayoutEUR']).replace(',', '.'))
                        OstStart = 0
                        OstEnd = round(OstStart + float(ReferalBenefitEUR) + float(ReferalPayoutEUR), 2)
                    else:
                        period = _('за 3 месяца')
                        float(re.sub(r'[^0-9,]', '', user_info['ReferalPayout3MEUR']).replace(',','.'))
                        ReferalTurnoverUSDT = float(re.sub(r'[^0-9,]', '', user_info['ReferalTurnover3MUSDT']).replace(',','.'))
                        ReferalTurnoverRUB = float(re.sub(r'[^0-9,]', '', user_info['ReferalTurnover3MRUB']).replace(',','.'))
                        TurnoverQty = user_info['Turnover3MQty']
                        ReferalBenefitEUR = float(re.sub(r'[^0-9,]', '', user_info['ReferalBenefit3MEUR']).replace(',','.'))
                        ReferalPayoutEUR = -float(re.sub(r'[^0-9,]', '', user_info['ReferalPayout3MEUR']).replace(',','.'))
                        OstStart = (float(re.sub(r'[^0-9,]', '', user_info['ReferalBenefitEUR']).replace(',','.'))-float(re.sub(r'[^0-9,]', '', user_info['ReferalBenefit3MEUR']).replace(',','.')))-(float(re.sub(r'[^0-9,]', '', user_info['ReferalPayoutEUR']).replace(',','.'))-float(re.sub(r'[^0-9,]', '', user_info['ReferalPayout3MEUR']).replace(',','.')))
                        OstEnd = round(OstStart + float(ReferalBenefitEUR) + float(ReferalPayoutEUR), 2)
                    mess = _('<b>Информация по Вашему реферальному коду за {period}:</b> \n\n' \
                            '<b>Номер по дисконтной программе:</b> {Referral_Number}\n' \
                            '<em>Итого сумма обменов в USDT:</em> {ReferalTurnoverUSDT} \n' \
                            '<em>Итого сумма обменов в RUB:</em> {ReferalTurnoverRUB}\n\n' \
                            '<em>Общее количество сделок:</em> {TurnoverQty}\n'
                            '<b>Расчет бонусов в EUR:</b> \n' \
                            '<em>Остаток на начало:</em> {OstStart}\n' \
                            '<em>Начисленно за отчетный перио:</em> {ReferalBenefitEUR}\n' \
                            '<em>Выплачено за отчетный период:</em> {ReferalPayoutEUR}\n' \
                            '<em>Остаток на конец:</em> {OstEnd}').format(period=period,
                                                                        Referral_Number=Referral_Number,
                                                                        ReferalTurnoverUSDT=ReferalTurnoverUSDT,
                                                                        ReferalTurnoverRUB=ReferalTurnoverRUB,
                                                                        TurnoverQty=TurnoverQty,
                                                                        OstStart=OstStart,
                                                                        ReferalBenefitEUR=ReferalBenefitEUR,
                                                                        ReferalPayoutEUR=ReferalPayoutEUR,
                                                                        OstEnd=OstEnd)
                elif data.get('REFERRAL_HIST_FLAG'):
                    ref_code = ACTIVE_CONTACT_LIST[username]['Referral_Number']
                    disc_code = ACTIVE_CONTACT_LIST[username]['Discount_Number']
                    mess_ref, mess_ref_month, mess_ref_3month = get_trans_history_ref(username, ref_code, _)
                    if message.text == _('За месяц'):
                        if _('Дата') in mess_ref_month:
                            mess = mess_ref_month
                        else:
                            mess = _('По вашему коду не было сделок за последний месяц')
                    elif message.text == _('За 3 месяца'):
                        if _('Дата') in mess_ref_3month:
                            mess = mess_ref_3month
                        else:
                            mess = _('По вашему коду не было сделок за последние 3 месяца')
                    else:
                        if _('Дата') in mess_ref:
                            mess = mess_ref
                        else:
                            mess = _('По вашему коду не было сделок')
                b1 = types.KeyboardButton(_('За месяц'))
                b2 = types.KeyboardButton(_('За 3 месяца'))
                b3 = types.KeyboardButton(_('За все время'))
                b4 = types.KeyboardButton(_('Назад'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b1, b2, b3, b4)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # Истории сделок по дисконтной программе
            elif data.get('REFERRAL_FLAG') and message.text == _('Дисконтная программа'):
                data['DISCONT_PERIOD_FLAG'] = True
                #ACTIVE_CONTACT_LIST = scrab_contact_list()
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                a = types.ReplyKeyboardRemove()
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                mess = _('Историю обменов по Вашему дисконтному коду можно посмотреть за последний месяц, 3 месяца, все время.\n' \
                        'Пожалуйста, выберите период времени: ')
                b1 = types.KeyboardButton(_('За месяц'))
                b2 = types.KeyboardButton(_('За 3 месяца'))
                b3 = types.KeyboardButton(_('За все время'))
                b4 = types.KeyboardButton(_('Назад'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b1, b2, b3, b4)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # Выбор периода для дисконтной программы
            elif data.get('REFERRAL_FLAG') and data.get('DISCONT_PERIOD_FLAG') and message.text == _('За месяц'):
                #ACTIVE_CONTACT_LIST = scrab_contact_list()
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                a = types.ReplyKeyboardRemove()
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                ref_code = ACTIVE_CONTACT_LIST[username]['Referral_Number']
                disc_code = ACTIVE_CONTACT_LIST[username]['Discount_Number']
                mess_disc, mess_disc_month, mess_disc_3month = get_trans_history_disc(username, disc_code, _)
                b1 = types.KeyboardButton(_('За месяц'))
                b2 = types.KeyboardButton(_('За 3 месяца'))
                b3 = types.KeyboardButton(_('За все время'))
                b4 = types.KeyboardButton(_('Назад'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b1, b2, b3, b4)
                if _('Дата') in mess_disc_month:
                    mess = mess_disc_month
                else:
                    mess = _('По вашему коду не было сделок за последний месяц')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif data.get('REFERRAL_FLAG') and data.get('DISCONT_PERIOD_FLAG') and message.text == _('За все время'):
                #ACTIVE_CONTACT_LIST = scrab_contact_list()
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                a = types.ReplyKeyboardRemove()
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                ref_code = ACTIVE_CONTACT_LIST[username]['Referral_Number']
                disc_code = ACTIVE_CONTACT_LIST[username]['Discount_Number']
                mess_disc, mess_disc_month, mess_disc_3month = get_trans_history_disc(username, disc_code, _)
                b1 = types.KeyboardButton(_('За месяц'))
                b2 = types.KeyboardButton(_('За 3 месяца'))
                b3 = types.KeyboardButton(_('За все время'))
                b4 = types.KeyboardButton(_('Назад'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b1, b2, b3, b4)
                if _('Дата') in mess_disc:
                    mess = mess_disc
                else:
                    mess = _('По вашему коду не было сделок')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif data.get('REFERRAL_FLAG') and data.get('DISCONT_PERIOD_FLAG') and message.text == _('За 3 месяца'):
                #ACTIVE_CONTACT_LIST = scrab_contact_list()
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                a = types.ReplyKeyboardRemove()
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                ref_code = ACTIVE_CONTACT_LIST[username]['Referral_Number']
                disc_code = ACTIVE_CONTACT_LIST[username]['Discount_Number']
                mess_disc, mess_disc_month, mess_disc_3month = get_trans_history_disc(username, disc_code, _)
                b1 = types.KeyboardButton(_('За месяц'))
                b2 = types.KeyboardButton(_('За 3 месяца'))
                b3 = types.KeyboardButton(_('За все время'))
                b4 = types.KeyboardButton(_('Назад'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b1, b2, b3, b4)
                if _('Дата') in mess_disc_3month:
                    mess = mess_disc_3month
                else:
                    mess = _('По вашему коду не было сделок за последние 3 месяца')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif data.get('REFERRAL_FLAG') and message.text == _('Назад'):
                data['DISCONT_PERIOD_FLAG'] = False
                data['REFERRAL_PERIOD_FLAG'] = False
                data['REFERRAL_CHARGES_FLAG'] = False
                data['REFERRAL_HIST_FLAG'] = False
                data['REFERRAL_OPTIONS_FLAG'] = False
                b1 = types.KeyboardButton(_('Реферальная программа'))
                b2 = types.KeyboardButton(_('Дисконтная программа'))
                b3 = types.KeyboardButton(_('Карта бонусной программы'))
                b4 = types.KeyboardButton(_('Главное меню'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b3, b2, b1, b4)
                bot.send_message(message.chat.id, text=_('Выберите доступную команду из меню'), parse_mode='html',
                                reply_markup=markup)
            elif (data.get('REFERRAL_FLAG') or data.get('FEEDBACK_FLAG') or data.get('FORM_ORDER_FLAG')) and message.text == _('Главное меню'):
                data['REFERRAL_FLAG'] = False
                data['FEEDBACK_FLAG'] = False
                data['FORM_ORDER_FLAG'] = False
                a = types.ReplyKeyboardRemove()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, text=_('Выберите доступную команду из меню'), parse_mode='html',
                                reply_markup=markup)
            if LANGUAGE_FLAG and message.text in [_('RU'), _('EN'), _('SR')]:
                username = '@' + message.chat.username if message.chat.username is not None else message.chat.id
                write_language(message.from_user.id, message.text)
                get_user_translator.clean(message.from_user.id)
                _ = get_user_translator(message.from_user.id)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                mess = _('Язык сменен')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # Обработка обратной связи клиента
            if FEEDBACK_FLAG and message.text != _('📨 Оставить отзыв') and message.text != 'Главное меню':
                if message.text in _(MAIN_MENU_BUTTONS) or message.text in ['/form_order', '/contact_operator', '/get_rates',
                                                                            '/documents', '/refferal', '/feedback',
                                                                            '/change_language', '/help']:
                    FEEDBACK_FLAG = False
                else:
                    tel_id = message.from_user.id
                    if message.chat.username is not None:
                        tel_nick = '@' + message.chat.username
                    else:
                        tel_nick = 'no_username'
                    tel_name = message.from_user.first_name
                    date = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
                    # date = datetime.utcfromtimestamp(message.json['date']).strftime('%Y-%m-%d %H:%M:%S')
                    client_feedback = message.text
                    # TODO: Не надо переводить??
                    operator_mess = f'<em>Источник:</em> Alpha_TG_Bot\n' \
                                    f'<b>Оставлен отзыв:</b>\n' \
                                    f'<em>Имя клиента:</em> {tel_name}\n' \
                                    f'<em>ID клиента:</em> {tel_id}\n' \
                                    f'<em>Ник клиента:</em> {tel_nick}\n' \
                                    f'<em>Отзыв:</em> {client_feedback}\n' \
                                    f'<em>Время формирования заявки:</em> {date}'
                    a = types.ReplyKeyboardRemove()
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                    markup.add(*menu_buttons)
                    mess = _('Спасибо за Ваш отзыв!')
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                    # bot.send_message(GROUP_CHAT_ID, operator_mess, parse_mode='html', reply_markup=a)
                    write_feedback(date, tel_id, tel_nick, tel_name, client_feedback)
                    FEEDBACK_FLAG = False
            ###2.1.1 Выбор операции: Обмен РУБЛЕЙ на ЕВРО
            if (message.text == _('Обмен РУБЛЕЙ на ЕВРО') or message.text == _('Обмен ЕВРО на РУБЛИ') or message.text == _('Обмен РУБЛЕЙ на ТЕНГЕ')) and (data.get('FORM_ORDER_FLAG')):
                data['OPER_FLAG_EUR_RUB'] = True
                data['OPER_FLAG_USDT_EURO'] = False
                data['OPER_NAME_RE'] = str(message.text)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                b1 = types.KeyboardButton(_('Сбербанк'))
                b2 = types.KeyboardButton(_('Тинькофф'))
                b3 = types.KeyboardButton(_('Райффайзен'))
                b4 = types.KeyboardButton(_('Прочие'))
                b5 = types.KeyboardButton(_('Наличные'))
                if message.text == _('Обмен ЕВРО на РУБЛИ'):
                    mess = _('Выберите банк, на счета которого планируете получить рубли:\n' \
                        '1. Сбербанк\n' \
                        '2. Тинькофф\n' \
                        '3. Райффайзен\n' \
                        '4. Наличные\n' \
                        '5. Прочие\n')
                    markup.add(b1, b2, b3, b4, b5, mb)
                    data['OPER_FLAG_EUR_RUB_BACK'] = True
                elif message.text == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                    mess = _('Выберите банк, на счета которого планируете отправть рубли:\n' \
                        '1. Сбербанк\n' \
                        '2. Тинькофф\n' \
                        '3. Райффайзен\n' \
                        '4. Прочие\n')
                    markup.add(b1, b2, b3, b4, mb)
                else:
                    mess = _('Выберите банк, со счета которого планируете отправить рубли:\n' \
                            '1. Сбербанк\n' \
                            '2. Тинькофф\n' \
                            '3. Райффайзен\n' \
                            '4. Наличные\n' \
                            '5. Прочие\n')
                    markup.add(b1, b2, b3, b4, b5, mb)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # 2.1.2 Выбор города
            elif (message.text == _('Наличные')) and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (
                    not data.get('OPER_FLAG_USDT_EURO')) and (not data.get('BANK_FLAG')) and (not data.get('CASH_FLAG')):
                data['BANK_FLAG'] = True
                data['CASH_FLAG'] = True
                data['BANK_RE'] = message.text
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(*CITY_CASH_BUTTONS, mb)
                mess = _('Введите город внесения наличных денег') if data.get('OPER_NAME_RE')==_('Обмен РУБЛЕЙ на ЕВРО') else _('Введите город получения наличных денег')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif (message.text in CITY_CASH_BUTTONS) and (data.get('FORM_ORDER_FLAG')) and (
                    data.get('OPER_FLAG_EUR_RUB')) and (not data.get('OPER_FLAG_USDT_EURO')) and (data.get('BANK_FLAG')) and (data.get('CASH_FLAG')):
                data['CASH_CITY'] = message.text
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                order_city_buttons = form_order_city_buttons(_(CITY_BUTTONS))
                markup.add(*order_city_buttons, mb)
                mess = _('Выберите представленный в списке город, в котором планируете провести сделку')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif (message.text == _('Сбербанк') and not data.get('OPER_FLAG_EUR_RUB_BACK')) and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (
                    not data.get('OPER_FLAG_USDT_EURO')) and (not data.get('BANK_FLAG')):
                data['BANK_FLAG'] = True
                data['BANK_RE'] = message.text
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                order_city_buttons = form_order_city_buttons(_(CITY_BUTTONS)) if data.get('OPER_NAME_RE') != _('Обмен РУБЛЕЙ на ТЕНГЕ') else form_order_city_buttons(_(kzt_bank_names))
                markup.add(*order_city_buttons, mb)
                mess1 = _(SBER_TEXT)
                if data.get('OPER_FLAG_EUR_RUB_BACK'):
                    mess2 = _('Выберите представленный в списке город, в котором планируете отдать евро')
                elif data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                    mess2 = _('Выберите представленный в списке банк, на счет которого хотите получить тенге')
                else:
                    mess2 = _('Выберите представленный в списке город, в котором планируете провести сделку')
                bot.send_message(message.chat.id, mess1, parse_mode='html', reply_markup=markup)
                bot.send_message(message.chat.id, mess2, parse_mode='html', reply_markup=markup)
            elif (message.text in ru_bank_names) and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (
                    not data.get('OPER_FLAG_USDT_EURO')) and (not data.get('BANK_FLAG')):
                data['BANK_FLAG'] = True
                data['BANK_RE'] = message.text
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                order_city_buttons = form_order_city_buttons(_(CITY_BUTTONS)) if data.get('OPER_NAME_RE') != _('Обмен РУБЛЕЙ на ТЕНГЕ') else form_order_city_buttons(_(kzt_bank_names))
                markup.add(*order_city_buttons, mb)
                if data.get('OPER_FLAG_EUR_RUB_BACK'):
                    mess = _('Выберите представленный в списке город, в котором планируете отдать евро')
                elif data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                    mess = _('Выберите представленный в списке банк, на счет которого хотите получить тенге')
                else:
                    mess = _('Выберите представленный в списке город, в котором планируете провести сделку')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # 2.1.3 Обработка города (или банка, если это операция RUB=>KZT)
            elif (message.text == _('Другая локация')) and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (
                    not data.get('OPER_FLAG_USDT_EURO')) \
                    and (data.get('BANK_FLAG')) and (not data.get('CITY_RE_FLAG')) and (not data.get('ANOTHER_CITY_RE_FLAG')):
                data['ANOTHER_CITY_RE_FLAG'] = True
                mess = _('<b><em>Введите город сделки</em></b>')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # 2.1.4 Сумма сделки в евро
            elif (message.text in cities or message.text in kzt_bank_names or data.get('ANOTHER_CITY_RE_FLAG')) and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (
                    not data.get('OPER_FLAG_USDT_EURO')) \
                    and (data.get('BANK_FLAG')) and (not data.get('CITY_RE_FLAG')):
                a = types.ReplyKeyboardRemove()
                data['CITY_RE_FLAG'] = True
                data['CITY_RE'] = message.text #здесь может быть банк, если операция RUB=>KZT
                if data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                    mess = _(
                        '<b>Какую сумму в тенге хотите получить?</b>\n<em>(Введите целое число, разрядность которого не превышает 8 знаков)</em>\n\n' \
                        '<b>Минимальная сумма сделки 50000 тенге</b>\n')
                else:
                    if data.get('OPER_NAME_RE') == _('Обмен ЕВРО на РУБЛИ'):
                        currency = 'рублях'
                        currency2 = 'РУБЛЕЙ'
                        lim1 = '10000'
                        lim2 = '50000'
                    else:
                        currency = 'евро'
                        currency2 = 'ЕВРО'
                        lim1 = '100'
                        lim2 = '500'
                    mess = _(
                        '<b>Какую сумму в {currency} хотите получить?</b>\n<em>(Введите целое число, разрядность которого не превышает 8 знаков)</em>\n\n' \
                        '<b>Минимальная сумма сделки зависит от выбранного ранее города:</b>\n' \
                        'Херцег Нови, Бар, Будва, Тиват - {lim1} {currency2}\n' \
                        'Остальные города - {lim2} {currency2}').format(currency=currency,
                                                                        currency2=currency2,
                                                                        lim1=lim1,
                                                                        lim2=lim2)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=a)
            # 2.1.5 Обработка суммы сделки
            # Если ввели сумму не в том формате и с ограничение 500 евро
            elif ((not message.text.isdigit() or len(message.text) > 8) \
                or ((int(message.text) < 100 and data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ЕВРО') or int(message.text) < 10000 and data.get('OPER_NAME_RE') == _('Обмен ЕВРО на РУБЛИ') or int(message.text) < 50000 and data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ')) and (data.get('CITY_RE') in [_('Херцег Нови'), _('Бар'), _('Будва'), _('Тиват')] or data.get('CITY_RE') in kzt_bank_names)) \
                or ((int(message.text) < 500 and data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ЕВРО') or int(message.text) < 50000 and data.get('OPER_NAME_RE') == _('Обмен ЕВРО на РУБЛИ')) and data.get('CITY_RE') not in [_('Херцег Нови'), _('Бар'), _('Будва'), _('Тиват')])) \
                    and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (not data.get('OPER_FLAG_USDT_EURO')) and (data.get('BANK_FLAG')) \
                    and (data.get('CITY_RE_FLAG')) and (not data.get('SUM_RUB_FLAG')):
                a = types.ReplyKeyboardRemove()
                if data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                    mess = _(
                        'Вы ввели некорректную сумму.\nДля формирования заявки просим повторно ввести сумму, учитывая ограничения:\n' \
                        '<b><em>1.Целое число, разрядность которого не превышает 8 знаков</em></b>.\n' \
                        '<b><em>2.Минимальная сумма сделки 50000 тенге</em></b>\n\n'\
                        '<em>Если ввели/выбрали неверное значение на одном из этапов формирования заявки, перезапустите команду: /form_order</em>')
                else:
                    if data.get('OPER_NAME_RE') == _('Обмен ЕВРО на РУБЛИ'):
                        currency = 'рублях'
                        currency2 = 'РУБЛЕЙ'
                        lim1 = '10000'
                        lim2 = '50000'
                    else:
                        currency = 'евро'
                        currency2 = 'ЕВРО'
                        lim1 = '100'
                        lim2 = '500'
                    mess = _(
                        'Вы ввели некорректную сумму.\nДля формирования заявки просим повторно ввести сумму, учитывая ограничения:\n' \
                        '<b><em>1.Целое число, разрядность которого не превышает 8 знаков</em></b>.\n' \
                        '<b><em>2.Минимальная сумма сделки в Херцег Нови, Баре, Тивате и Будве - {lim1} {currency2}, в остальных городах - {lim2} {currency2}</em></b>.\n\n' \
                        '<em>Если ввели/выбрали неверное значение на одном из этапов формирования заявки, перезапустите команду: /form_order</em>').format(lim1=lim1,
                                                                                                                                                        lim2=lim2,
                                                                                                                                                        currency2=currency2)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=a)
            # 2.1.6 Предлагаем выбор временени
            elif ((message.text.isdigit() and len(message.text) <= 8) \
                and (((int(message.text) >= 100 and data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ЕВРО')) or (int(message.text) >= 10000 and data.get('OPER_NAME_RE') == _('Обмен ЕВРО на РУБЛИ')) or (int(message.text) >= 50000 and data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ')) and (data.get('CITY_RE') in [_('Херцег Нови'), _('Бар'), _('Будва'), _('Тиват')] or data.get('CITY_RE') in kzt_bank_names)) \
                or ((int(message.text) >= 500 and data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ЕВРО')) or (int(message.text) >= 50000 and data.get('OPER_NAME_RE') == _('Обмен ЕВРО на РУБЛИ')) and data.get('CITY_RE') not in [_('Херцег Нови'), _('Бар'), _('Будва'), _('Тиват')]))) \
                    and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (not data.get('OPER_FLAG_USDT_EURO')) and data.get('BANK_FLAG') \
                    and (data.get('CITY_RE_FLAG')) and (not data.get('SUM_RUB_FLAG')) and (not data.get('ORDER_TIME_FLAG_RE')) and (not data.get('ORDER_CONFIRM_RE_FLAG')):
                username = '@' + message.chat.username if message.chat.username is not None else message.chat.id
                eur_to_rub = int(message.text) * rates_funcs.get_fiat_rates_tradingview()['EUR_RUB']
                if (data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ЕВРО') and ((get_city_commission(city_name=data.get('CASH_CITY'), exch_sum=int(eur_to_rub), deal_type='Депозит', currency='RUB')[0] is not None and data.get('CASH_FLAG')) or not data.get('CASH_FLAG')))\
                    or (data.get('OPER_NAME_RE') == _('Обмен ЕВРО на РУБЛИ') and ((get_city_commission(city_name=data.get('CASH_CITY'), exch_sum=int(message.text), deal_type='Выдача', currency='RUB')[0] is not None and data.get('CASH_FLAG')) or not data.get('CASH_FLAG'))):
                    data['ORDER_TIME_FLAG_RE'] = True
                    data['SUM_RUB_FLAG'] = True
                    # Сохраним в глобальных переменных новые значения курсов
                    data['SUM_EUR_RE'] = int(message.text)
                    if data.get('OPER_FLAG_EUR_RUB_BACK'):
                        rub_info = rates_funcs.compute_to_rub_amount(currency_amount=data['SUM_EUR_RE'], currency_from='EUR_RUB', username=username, bank_name=data['BANK_RE'])
                    else:
                        rub_info = rates_funcs.compute_rub_euro_amount(euro_amount=data['SUM_EUR_RE'], username=username, cash_flag=data.get('CASH_FLAG'), bank_name=data['BANK_RE'])
                    data['RUB_INFO'] = dict(rub_info)  # переменная необходима для хранения данных о курсах при вызове команды RUB_EURO и используется для добавления записей в GSH
                    # в SUM_RUB_RE, RUB_EURO_RATE может быть и другая валюта, в зависимости от операции
                    data['SUM_RUB_RE'] = rub_info['rub_amount'] if data.get('OPER_NAME_RE')==_('Обмен РУБЛЕЙ на ЕВРО') else rub_info['currency_from_amount']
                    data['RUB_EURO_RATE'] = rub_info['currency_rate'] #if CITY_RE != _('Херцег Нови') else rub_info['currency_rate'] + 1
                    msk_current_time = datetime.now(tz)
                    msk_minutes = msk_current_time.hour * 60 + msk_current_time.minute
                    # предлагаем каждые полчаса: для этого переведем все границы в минуты
                    time_borders = {
                        0 * 60: '00:00 - 02:00',
                        2 * 60: '02:00 - 04:00',
                        4 * 60: '04:00 - 06:00',
                        6 * 60: '06:00 - 08:00',
                        8 * 60: '08:00 - 10:00',
                        10 * 60: '10:00 - 12:00',
                        12 * 60: '12:00 - 14:00',
                        14 * 60: '14:00 - 16:00',
                        16 * 60: '16:00 - 18:00',
                        18 * 60: '18:00 - 20:00',
                        20 * 60: '20:00 - 22:00'
                    }
                    time_buttons = [types.KeyboardButton(time_period) for high_board, time_period in time_borders.items() if
                                    msk_minutes < high_board]
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    markup.add(*time_buttons)
                    markup.add(types.KeyboardButton(_('Другой день')), mb)
                    mess = _('Выберите период времени, когда Вам было бы удобно осуществить сделку')  # Время по Черногории
                elif data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                    data['ORDER_TIME_FLAG_RE'] = True
                    data['SUM_RUB_FLAG'] = True
                    # Сохраним в глобальных переменных новые значения курсов
                    data['SUM_EUR_RE'] = int(message.text) # здесь сумма ТЕНГЕ
                    rub_info = rates_funcs.compute_rub_kzt_amount(kzt_amount=data['SUM_EUR_RE'], username=username, bank_name=data['BANK_RE'])
                    data['RUB_INFO'] = dict(rub_info)  # переменная необходима для хранения данных о курсах при вызове команды RUB_EURO и используется для добавления записей в GSH
                    # в SUM_RUB_RE, RUB_EURO_RATE может быть и другая валюта, в зависимости от операции
                    data['SUM_RUB_RE'] = rub_info['rub_amount']
                    data['RUB_EURO_RATE'] = rub_info['currency_rate'] #if CITY_RE != _('Херцег Нови') else rub_info['currency_rate'] + 1
                    msk_current_time = datetime.now(tz)
                    msk_minutes = msk_current_time.hour * 60 + msk_current_time.minute
                    # предлагаем каждые полчаса: для этого переведем все границы в минуты
                    time_borders = {
                         0 * 60: '00:00 - 02:00',
                        2 * 60: '02:00 - 04:00',
                        4 * 60: '04:00 - 06:00',
                        6 * 60: '06:00 - 08:00',
                        8 * 60: '08:00 - 10:00',
                        10 * 60: '10:00 - 12:00',
                        12 * 60: '12:00 - 14:00',
                        14 * 60: '14:00 - 16:00',
                        16 * 60: '16:00 - 18:00',
                        18 * 60: '18:00 - 20:00',
                        20 * 60: '20:00 - 22:00'
                    }
                    time_buttons = [types.KeyboardButton(time_period) for high_board, time_period in time_borders.items() if
                                    msk_minutes < high_board]
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    markup.add(*time_buttons)
                    markup.add(types.KeyboardButton(_('Другой день')), mb)
                    mess = _('Выберите период времени, когда Вам было бы удобно осуществить сделку')  # Время по Черногории
                else:
                    city_commission = get_city_commission(city_name=data['CASH_CITY'], exch_sum=int(message.text), deal_type='Депозит', currency='RUB') if\
                    data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ЕВРО') else get_city_commission(city_name=data['CASH_CITY'], exch_sum=int(message.text), deal_type='Выдача', currency='RUB')
                    if city_commission[1] is not None:
                        mess = _(
                        'Для депозита или выдачи рублей в выбранном городе действует ограничение по минимальной сумме в размере {city_commission} рублей.\nДля формирования заявки просим повторно ввести сумму, учитывая ограничения или начать заполнение заявки сначала.\n\n' \
                        '<em>Если ввели/выбрали неверное значение на одном из этапов формирования заявки, перезапустите команду: /form_order</em>').format(city_commission=int(city_commission[1]))
                    else:
                        mess = _(
                        'Депозит или выдача рублей в выбранном городе сейчас не осуществляется.\nДля формирования заявки просим начать заполнение заявки заново и выбрать другой город.\n\n' \
                        '<em>Если ввели/выбрали неверное значение на одном из этапов формирования заявки, перезапустите команду: /form_order</em>').format(city_commission=city_commission[1])
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                    markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # 2.1.7. Предлагаем ввести или согласиться со своим реферальным кодом
            elif (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (not data.get('OPER_FLAG_USDT_EURO')) and data.get('BANK_FLAG') \
                    and (data.get('CITY_RE_FLAG')) and (data.get('SUM_RUB_FLAG')) and (data.get('ORDER_TIME_FLAG_RE')) and (not data.get('FRIEND_REF_FLAG_RE')) and (
                    not data.get('ORDER_CONFIRM_RE_FLAG')):
                data['FRIEND_REF_FLAG_RE'] = True
                #ACTIVE_CONTACT_LIST = scrab_contact_list()
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                all_user_ids = [user_info['user_ID'] for user_info in ACTIVE_CONTACT_LIST.values()]
                data['ORDER_TIME_RE'] = message.text
                if (username not in ACTIVE_CONTACT_LIST) and (user_id not in all_user_ids):
                    existed_disc_codes = [one_doc['Discount_Number'] for one_doc in ACTIVE_CONTACT_LIST.values()]
                    existed_ref_codes = [one_doc['Referral_Number'] for one_doc in ACTIVE_CONTACT_LIST.values() if 'Referral_Number' in one_doc]
                    while True:
                        s = string.ascii_lowercase + string.ascii_uppercase + string.digits
                        disc_code = ''.join(random.sample(s, 4))
                        ref_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                        if disc_code not in existed_disc_codes and ref_code not in existed_ref_codes:
                            break
                    discount = '0%'
                    referal_mess = _('Вы впервые оформляете заявку.\n' \
                                    'Ваш код дисконтной программы: <b><em>{disc_code}</em></b>\n' \
                                    'Ваш код реферальной программы: <b><em>{ref_code}</em></b>\n' \
                                    'Ваша текущая скидка: {discount}\n\n' \
                                    '<b>Просьба выбрать в меню одну из опций:\n' \
                                    '1. Оставить свой дисконтный код\n' \
                                    '2. Ввести дисконтный (4 символа) или реферальный (6 символов) код друга</b>').format(
                        disc_code=disc_code,
                        ref_code=ref_code,
                        discount=discount)
                    write_contact(TG_Contact=username, user_ID=message.from_user.id, NameSurname=message.from_user.full_name,
                                AccTypeFROM=data['BANK_RE'], CurrFROM='RUB',
                                City=data.get('CITY_RE'), ContactType='Клиент', ContactDealer='Alpha_TG_Bot', CurrStatus='Активный',
                                Discount_Number=disc_code, Referral_Number=ref_code)
                else:
                    if username in ACTIVE_CONTACT_LIST:
                        disc_code = ACTIVE_CONTACT_LIST[username]['Discount_Number']
                        ref_code = ACTIVE_CONTACT_LIST[username]['Referral_Number']
                        discount = str(float(ACTIVE_CONTACT_LIST[username]['Discount'].replace(',','.'))*100) + '%'
                    else:
                        userids_names = {user_info['user_ID']: username for username, user_info in ACTIVE_CONTACT_LIST.items()}
                        disc_code = ACTIVE_CONTACT_LIST[userids_names[user_id]]['Discount_Number']
                        ref_code = ACTIVE_CONTACT_LIST[userids_names[user_id]]['Referral_Number']
                        discount = str(float(ACTIVE_CONTACT_LIST[userids_names[user_id]]['Discount'].replace(',','.'))*100) + '%'
                    referal_mess = _('Ваш код дисконтной программы: <b><em>{disc_code}</em></b>\n' \
                                    'Ваш код реферальной программы: <b><em>{ref_code}</em></b>\n' \
                                    'Ваша текущая скидка: <b><em>{discount}</em></b>\n\n' \
                                    '<b>Просьба выбрать в меню одну из опций:\n' \
                                    '1. Оставить свой дисконтный код\n' \
                                    '2. Ввести дисконтный <em>(4 символа)</em> или реферальный <em>(6 символов)</em> код друга</b>').format(
                        disc_code=disc_code,
                        ref_code=ref_code,
                        discount=discount)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                b1 = types.KeyboardButton(_('Оставить свой код'))
                b2 = types.KeyboardButton(_('Ввести код друга'))
                b3 = types.KeyboardButton(_('Поиск контакта'))
                markup.add(b1, b2, b3, mb) if username in ACTIVE_CONTACT_LIST and ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else markup.add(b1, b2, mb)
                bot.send_message(message.chat.id, referal_mess, parse_mode='html', reply_markup=markup)
            # 2.1.8.2 Если ввод промокода друга
            elif message.text == _('Ввести код друга') and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (
                    not data.get('OPER_FLAG_USDT_EURO')) and data.get('BANK_FLAG') \
                    and (data.get('CITY_RE_FLAG')) and (data.get('SUM_RUB_FLAG')) and (data.get('ORDER_TIME_FLAG_RE')) and (data.get('FRIEND_REF_FLAG_RE')) and (
                    not data.get('ORDER_CONFIRM_RE_FLAG')):
                a = types.ReplyKeyboardRemove()
                mess = _(
                    '<b>Введите дисконтный <em>(4 символа)</em> или реферальной <em>(6 символов)</em> программы Вашего друга</b>')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=a)
            elif (message.text == _('Оставить свой код') and data.get('FRIEND_REF_FLAG_RE')) or (data.get('FORM_ORDER_FLAG')) and not data.get('FIND_USER_FLAG') and message.text != _('Поиск контакта') and (
                    data.get('OPER_FLAG_EUR_RUB')) and (
                    not data.get('OPER_FLAG_USDT_EURO')) and data.get('BANK_FLAG') \
                    and (data.get('CITY_RE_FLAG')) and (data.get('SUM_RUB_FLAG')) and (data.get('ORDER_TIME_FLAG_RE')) and (data.get('FRIEND_REF_FLAG_RE')) and (
                    not data.get('RES_ORDER_FLAG_RE')) and (not data.get('ORDER_CONFIRM_RE_FLAG')):
                a = types.ReplyKeyboardRemove()
                data['RES_ORDER_FLAG_RE'] = True
                data['ORDER_CONFIRM_RE_FLAG'] = True
                DOCS_FLAG = True
                #ACTIVE_CONTACT_LIST = scrab_contact_list()  # необходимо заново считать контакты, так как в предыдущем шаге мы создаем нового клиента
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                all_user_ids = [user_info['user_ID'] for user_info in ACTIVE_CONTACT_LIST.values()]
                disc_values = {one_doc['Discount_Number']: one_doc['Discount'] for one_doc in ACTIVE_CONTACT_LIST.values() if
                            'Discount' in one_doc}
                disc_nicks = {one_doc['Discount_Number']: nick for nick, one_doc in ACTIVE_CONTACT_LIST.items() if 'Discount_Number' in one_doc}
                disc_ids = {one_doc['Discount_Number']: one_doc['user_ID'] for one_doc in ACTIVE_CONTACT_LIST.values() if 'Discount_Number' in one_doc}
                refs_nicks = {one_doc['Referral_Number']: nick for nick, one_doc in ACTIVE_CONTACT_LIST.items() if 'Referral_Number' in one_doc}
                refs_ids = {one_doc['Referral_Number']: one_doc['user_ID'] for one_doc in ACTIVE_CONTACT_LIST.values() if 'Referral_Number' in one_doc}
                if message.text == _('Оставить свой код'):
                    data['REF_CODE_RE'] = ACTIVE_CONTACT_LIST[username]['Discount_Number']
                else:
                    data['REF_CODE_RE'] = message.text
                if len(data.get('REF_CODE_RE')) == 4 and data.get('REF_CODE_RE').strip() in disc_values:
                    data['DISCOUNT_RE'] = disc_values[data['REF_CODE_RE']]
                    disc_status_mess = _('Дисконтный код <b><em>{REF_CODE_RE}</em></b> найден.\n' \
                                        'Дополнительные баллы будут начислены пользователю <b><em>{user_nick} (ID: {user_id})\n\n' \
                                        'Для получения подробной информации о реферальной программе воспользуйтесь командой /refferal</em></b>').format(
                        REF_CODE_RE=data['REF_CODE_RE'],
                        user_nick=disc_nicks[data['REF_CODE_RE']],
                        user_id=disc_ids[data['REF_CODE_RE']])
                elif len(data.get('REF_CODE_RE')) == 6 and data.get('REF_CODE_RE').strip() in refs_nicks and data.get('REF_CODE_RE') != ACTIVE_CONTACT_LIST[username]['Referral_Number']:
                    data['DISCOUNT_RE'] = ACTIVE_CONTACT_LIST[username]['Discount']
                    disc_status_mess = _('Реферальный код <b><em>{REF_CODE_RE}</em></b> найден.\n' \
                                        'Дополнительные баллы будут начислены пользователю <b><em>{user_nick} (ID: {user_id})</em></b>\n\n' \
                                        '<em>После совершения операции Вам также будут начислены дополнительные баллы, которые влияют на размер итоговой скидки!\n\n' \
                                        'Для получения подробной информации о бонусной программе воспользуйтесь командой /refferal</em>').format(
                        REF_CODE_RE=REF_CODE_RE,
                        user_nick=refs_nicks[REF_CODE_RE],
                        user_id=refs_ids[REF_CODE_RE])
                elif data.get('REF_CODE_RE') == ACTIVE_CONTACT_LIST[username]['Referral_Number']:
                    data['DISCOUNT_RE'] = ACTIVE_CONTACT_LIST[username]["Discount"]
                    disc_status_mess = _('Вы не можете использовать свой реферальный код <b><em>{REF_CODE_RE}</em></b> в своих сделках.\n' \
                                        'Для формирования итоговой заявки мы использовали Ваш дисконтный код <b>{disc_code}</b>,' \
                                        ' предоставляющий скидку <b>{disc}%.</b>\n\n' \
                                        '<em>После совершения операции Вам также будут начислены дополнительные баллы, которые влияют на размер итоговой скидки!\n\n' \
                                        'Для получения подробной информации о бонусной программе воспользуйтесь командой /refferal</em>').format(
                        REF_CODE_RE=data['REF_CODE_RE'],
                        disc_code=ACTIVE_CONTACT_LIST[username]["Discount_Number"],
                        disc=str(float(ACTIVE_CONTACT_LIST[username]["Discount"].replace(',','.'))*100))
                    data['REF_CODE_RE'] = ACTIVE_CONTACT_LIST[username]["Discount_Number"]
                else:
                    data['DISCOUNT_RE'] = ACTIVE_CONTACT_LIST[username]["Discount"]
                    disc_status_mess = _('Код <b><em>{REF_CODE_RE}</em></b> не найден в базе данных.\n' \
                                        'Для формирования итоговой заявки мы использовали Ваш дисконтный код <b>{disc_code}</b>,' \
                                        ' предоставляющий скидку <b>{disc}%.</b>\n\n' \
                                        '<em>После совершения операции Вам также будут начислены дополнительные баллы, которые влияют на размер итоговой скидки!\n\n' \
                                        'Для получения подробной информации о бонусной программе воспользуйтесь командой /refferal</em>').format(
                        REF_CODE_RE=data['REF_CODE_RE'],
                        disc_code=ACTIVE_CONTACT_LIST[username]["Discount_Number"],
                        disc=str(float(ACTIVE_CONTACT_LIST[username]["Discount"].replace(',','.'))*100))
                    data['REF_CODE_RE'] = ACTIVE_CONTACT_LIST[username]["Discount_Number"]
                if data.get('CASH_FLAG'):
                    city_commission = get_city_commission(city_name=data['CASH_CITY'], exch_sum=int(data['SUM_EUR_RE']), deal_type='Выдача', currency='RUB')[0]/100 if data.get('OPER_NAME_RE')==_('Обмен ЕВРО на РУБЛИ')\
                    else get_city_commission(city_name=data['CASH_CITY'], exch_sum=data['SUM_EUR_RE']*data['RUB_EURO_RATE'], deal_type='Депозит', currency='RUB')[0]/100
                else:
                    city_commission = 0
                if data.get('OPER_NAME_RE') in ['Обмен ЕВРО на РУБЛИ']:
                    discount = 1 + float(data['DISCOUNT_RE'].replace(',', '.')) / 100
                else:
                    discount = 1 - float(data['DISCOUNT_RE'].replace(',', '.')) / 100
                data['RUB_EURO_RATE'] = round(data['RUB_EURO_RATE'] * (1 - city_commission) * discount, 3)
                data['SUM_RUB_RE'] = round(data['SUM_EUR_RE'] / data['RUB_EURO_RATE']) if data.get('OPER_NAME_RE')==_('Обмен ЕВРО на РУБЛИ') else round(data['SUM_EUR_RE'] * data['RUB_EURO_RATE'])
                if data.get('CASH_FLAG') is True:
                    if data.get('OPER_FLAG_EUR_RUB_BACK'):
                        client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                        '<em>Валютная операция:</em> {OPER_NAME_RE}\n' \
                                        '<em>Ваш Банк-получатель:</em> {BANK_RE}\n' \
                                        '<em>Предлагаемый курс (EUR/RUB):</em> {RUB_EURO_RATE}\n' \
                                        '<b>Курс является индикативным и фиксируется в момент сделки</b>\n' \
                                        '<em>Сумма внесения в евро:</em> {SUM_RUB_RE}\n' \
                                        '<em>Сумма перевода в рублях:</em> {SUM_EUR_RE}\n' \
                                        '<em>Место внесения наличных:</em> {CASH_CITY}\n' \
                                        '<em>Город сделки:</em> {CITY_RE}\n' \
                                        '<em>Время сделки:</em> {ORDER_TIME_RE}\n\n' \
                                        '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(
                        OPER_NAME_RE=data.get('OPER_NAME_RE'),
                        BANK_RE=data['BANK_RE'],
                        RUB_EURO_RATE=data['RUB_EURO_RATE'],
                        SUM_EUR_RE=data['SUM_EUR_RE'],
                        SUM_RUB_RE=data['SUM_RUB_RE'],
                        CASH_CITY=data['CASH_CITY'],
                        CITY_RE=data.get('CITY_RE'),
                        ORDER_TIME_RE=data['ORDER_TIME_RE'])
                    else:
                        client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                            '<em>Валютная операция:</em> {OPER_NAME_RE}\n' \
                                            '<em>Способ оплаты:</em> {BANK_RE}\n' \
                                            '<em>Предлагаемый курс (EUR/RUB):</em> {RUB_EURO_RATE}\n' \
                                            '<b>Курс является индикативным и фиксируется в момент сделки</b>\n' \
                                            '<em>Сумма получения в евро:</em> {SUM_EUR_RE}\n' \
                                            '<em>Сумма перевода в рублях:</em> {SUM_RUB_RE}\n' \
                                            '<em>Место внесения наличных:</em> {CASH_CITY}\n' \
                                            '<em>Город сделки:</em> {CITY_RE}\n' \
                                            '<em>Время сделки:</em> {ORDER_TIME_RE}\n\n' \
                                            '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n\n').format(
                            OPER_NAME_RE=data.get('OPER_NAME_RE'),
                            BANK_RE=data['BANK_RE'],
                            RUB_EURO_RATE=data['RUB_EURO_RATE'],
                            SUM_EUR_RE=data['SUM_EUR_RE'],
                            SUM_RUB_RE=data['SUM_RUB_RE'],
                            CASH_CITY=data['CASH_CITY'],
                            CITY_RE=data.get('CITY_RE'),
                            ORDER_TIME_RE=data['ORDER_TIME_RE'])
                else:
                    if data.get('OPER_FLAG_EUR_RUB_BACK'):
                        client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                        '<em>Валютная операция:</em> {OPER_NAME_RE}\n' \
                                        '<em>Ваш Банк-получатель:</em> {BANK_RE}\n' \
                                        '<em>Предлагаемый курс (EUR/RUB):</em> {RUB_EURO_RATE}\n' \
                                        '<b>Курс является индикативным и фиксируется в момент сделки</b>\n' \
                                        '<em>Сумма внесения в евро:</em> {SUM_RUB_RE}\n' \
                                        '<em>Сумма перевода в рублях:</em> {SUM_EUR_RE}\n' \
                                        '<em>Город сделки:</em> {CITY_RE}\n' \
                                        '<em>Время сделки:</em> {ORDER_TIME_RE}\n\n' \
                                        '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(
                        OPER_NAME_RE=data.get('OPER_NAME_RE'),
                        BANK_RE=data['BANK_RE'],
                        RUB_EURO_RATE=data['RUB_EURO_RATE'],
                        SUM_EUR_RE=data['SUM_EUR_RE'],
                        SUM_RUB_RE=data['SUM_RUB_RE'],
                        CITY_RE=data.get('CITY_RE'),
                        ORDER_TIME_RE=data['ORDER_TIME_RE'])
                    else:
                        if data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                            currency = _('KZT')
                            currency1 = _('тенге')
                            city_or_bank = _('Банк получателя')
                        else:
                            currency = _('EUR')
                            currency1 = _('евро')
                            city_or_bank = _('Город сделки')
                        client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                            '<em>Валютная операция:</em> {OPER_NAME_RE}\n' \
                                            '<em>Ваш Банк-отправитель:</em> {BANK_RE}\n' \
                                            '<em>Предлагаемый курс ({currency}/RUB):</em> {RUB_EURO_RATE}\n' \
                                            '<b>Курс является индикативным и фиксируется в момент сделки</b>\n' \
                                            '<em>Сумма получения в {currency1}:</em> {SUM_EUR_RE}\n' \
                                            '<em>Сумма перевода в рублях:</em> {SUM_RUB_RE}\n' \
                                            '<em>{city_or_bank}:</em> {CITY_RE}\n' \
                                            '<em>Время сделки:</em> {ORDER_TIME_RE}\n\n' \
                                            '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(
                            OPER_NAME_RE=data.get('OPER_NAME_RE'),
                            BANK_RE=data['BANK_RE'],
                            RUB_EURO_RATE=data['RUB_EURO_RATE'],
                            SUM_EUR_RE=data['SUM_EUR_RE'],
                            SUM_RUB_RE=data['SUM_RUB_RE'],
                            CITY_RE=data.get('CITY_RE'),
                            ORDER_TIME_RE=data['ORDER_TIME_RE'],
                            currency=currency,
                            currency1=currency1,
                            city_or_bank=city_or_bank)
                client_warning_mess = _(
                    '<b>Регистрируя заявку, Вы подтверждаете, что ознакомились с документами, регулирующими правила совершения операций' \
                    ' по обмену валют в разделе <em>/documents</em></b>\n\n')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                b1 = types.KeyboardButton(_('Да'))
                b2 = types.KeyboardButton(_('Нет'))
                markup.add(b1, b2)
                bot.send_message(message.chat.id, disc_status_mess, parse_mode='html', reply_markup=a)
                bot.send_message(message.chat.id, client_order_mess, parse_mode='html', reply_markup=markup)
                bot.send_message(message.chat.id, client_warning_mess, parse_mode='html', reply_markup=markup)
            # 2.1.8.3 Если поиск контакта 
            elif message.text == _('Поиск контакта') and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (
                    not data.get('OPER_FLAG_USDT_EURO')) and data.get('BANK_FLAG') \
                    and (data.get('CITY_RE_FLAG')) and (data.get('SUM_RUB_FLAG')) and (data.get('ORDER_TIME_FLAG_RE')) and (data.get('FRIEND_REF_FLAG_RE')) and (
                    not data.get('ORDER_CONFIRM_RE_FLAG')):
                data['FIND_USER_FLAG'] = True
                mess = _('Введите никнейм пользователя с учетом регистра, начиная с "@"')
                markup = types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif data.get('FIND_USER_FLAG') and message.text in ACTIVE_CONTACT_LIST and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (
                    not data.get('OPER_FLAG_USDT_EURO')) and data.get('BANK_FLAG') \
                    and (data.get('CITY_RE_FLAG')) and (data.get('SUM_RUB_FLAG')) and (data.get('ORDER_TIME_FLAG_RE')) and (data.get('FRIEND_REF_FLAG_RE')) and (
                    not data.get('ORDER_CONFIRM_RE_FLAG')):
                data['RES_ORDER_FLAG_RE'] = True
                data['ORDER_CONFIRM_RE_FLAG'] = True
                add_username = message.text
                disc_code = ACTIVE_CONTACT_LIST[message.text]["Discount_Number"]
                disc_status_mess = _('Пользователь найден.\n' \
                                    'Дополнительные баллы будут начислены пользователю <b><em>{user_nick} (дисконтный код: {disc_code})\n\n' \
                                    'Для получения подробной информации о реферальной программе воспользуйтесь командой /refferal</em></b>').format(
                    user_nick=message.text,
                    disc_code=disc_code)
                if data.get('OPER_FLAG_EUR_RUB_BACK'):
                    client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                    '<em>Валютная операция:</em> {OPER_NAME_RE}\n' \
                                    '<em>Ваш Банк-отправитель:</em> {BANK_RE}\n' \
                                    '<em>Предлагаемый курс (EUR/RUB):</em> {RUB_EURO_RATE}\n' \
                                    '<b>Курс является индикативным и фиксируется в момент сделки</b>\n' \
                                    '<em>Сумма внесения в евро:</em> {SUM_EUR_RE}\n' \
                                    '<em>Сумма перевода в рублях:</em> {SUM_RUB_RE}\n' \
                                    '<em>Город сделки:</em> {CITY_RE}\n' \
                                    '<em>Время сделки:</em> {ORDER_TIME_RE}\n\n' \
                                    '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(
                    OPER_NAME_RE=data.get('OPER_NAME_RE'),
                    BANK_RE=data['BANK_RE'],
                    RUB_EURO_RATE=data['RUB_EURO_RATE'],
                    SUM_EUR_RE=data['SUM_EUR_RE'],
                    SUM_RUB_RE=data['SUM_RUB_RE'],
                    CITY_RE=data.get('CITY_RE'),
                    ORDER_TIME_RE=data['ORDER_TIME_RE'])
                else:
                    if data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                        currency = _('KZT')
                        currency1 = _('тенге')
                        city_or_bank = _('Банк получателя')
                    else:
                        currency = _('EUR')
                        currency1 = _('евро')
                        city_or_bank = _('Город сделки')
                    client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                        '<em>Валютная операция:</em> {OPER_NAME_RE}\n' \
                                        '<em>Ваш Банк-отправитель:</em> {BANK_RE}\n' \
                                        '<em>Предлагаемый курс ({currency}/RUB):</em> {RUB_EURO_RATE}\n' \
                                        '<b>Курс является индикативным и фиксируется в момент сделки</b>\n' \
                                        '<em>Сумма получения в {currency1}:</em> {SUM_EUR_RE}\n' \
                                        '<em>Сумма перевода в рублях:</em> {SUM_RUB_RE}\n' \
                                        '<em>{city_or_bank}:</em> {CITY_RE}\n' \
                                        '<em>Время сделки:</em> {ORDER_TIME_RE}\n\n' \
                                        '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(
                        OPER_NAME_RE=data.get('OPER_NAME_RE'),
                        BANK_RE=data['BANK_RE'],
                        RUB_EURO_RATE=data['RUB_EURO_RATE'],
                        SUM_EUR_RE=data['SUM_EUR_RE'],
                        SUM_RUB_RE=data['SUM_RUB_RE'],
                        CITY_RE=data.get('CITY_RE'),
                        ORDER_TIME_RE=data['ORDER_TIME_RE'],
                        currency=currency,
                        currency1=currency1,
                        city_or_bank=city_or_bank)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                b1 = types.KeyboardButton(_('Да'))
                b2 = types.KeyboardButton(_('Нет'))
                markup.add(b1, b2)
                client_warning_mess = _(
                    '<b>Регистрируя заявку, Вы подтверждаете, что ознакомились с документами, регулирующими правила совершения операций' \
                    ' по обмену валют в разделе <em>/documents</em></b>\n\n')
                bot.send_message(message.chat.id, disc_status_mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(message.chat.id, client_order_mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(message.chat.id, client_warning_mess, parse_mode='html', reply_markup=markup)
            elif data.get('FIND_USER_FLAG') and message.text not in ACTIVE_CONTACT_LIST and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_EUR_RUB')) and (
                    not data.get('OPER_FLAG_USDT_EURO')) and data.get('BANK_FLAG') \
                    and (data.get('CITY_RE_FLAG')) and (data.get('SUM_RUB_FLAG')) and (data.get('ORDER_TIME_FLAG_RE')) and (data.get('FRIEND_REF_FLAG_RE')) and (
                    not data.get('ORDER_CONFIRM_RE_FLAG')):
                if not data.get('NAME_FLAG'):
                    data['NAME_FLAG'] = True
                    add_username = message.text
                    mess = _('Пользователь не найден. Введите его имя, чтобы добавить клиента в контакты.')
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                elif data.get('NAME_FLAG'):
                    data['NAME_FLAG'] = False
                    data['RES_ORDER_FLAG_RE'] = True
                    data['ORDER_CONFIRM_RE_FLAG'] = True
                    username = '@' + message.chat.username if message.chat.username is not None else 'None'
                    existed_disc_codes = [one_doc['Discount_Number'] for one_doc in ACTIVE_CONTACT_LIST.values()]
                    existed_ref_codes = [one_doc['Referral_Number'] for one_doc in ACTIVE_CONTACT_LIST.values() if 'Referral_Number' in one_doc]
                    while True:
                        s = string.ascii_lowercase + string.ascii_uppercase + string.digits
                        disc_code = ''.join(random.sample(s, 4))
                        if disc_code not in existed_disc_codes:
                            break
                    while True:
                        ref_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                        if ref_code not in existed_ref_codes:
                            break
                    write_contact(TG_Contact=add_username, user_ID='', NameSurname=message.text, AccTypeFROM='', CurrFROM='USDT', 
                                  City=data.get('CITY_RE'), ContactType='Клиент', ContactDealer=username, CurrStatus='Активный',
                                  Discount_Number=disc_code, Referral_Number=ref_code)
                    disc_status_mess = _('Пользователь добавлен.\n' \
                                    'Дополнительные баллы будут начислены пользователю <b><em>{add_username}</em></b> (дисконтный код: {disc_code})').format(
                                                                                                                                            add_username=add_username,
                                                                                                                                            disc_code=disc_code)
                    if data.get('OPER_FLAG_EUR_RUB_BACK'):
                        client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                        '<em>Валютная операция:</em> {OPER_NAME_RE}\n' \
                                        '<em>Ваш Банк-получатель:</em> {BANK_RE}\n' \
                                        '<em>Предлагаемый курс (EUR/RUB):</em> {RUB_EURO_RATE}\n' \
                                        '<b>Курс является индикативным и фиксируется в момент сделки</b>\n' \
                                        '<em>Сумма внесения в евро:</em> {SUM_RUB_RE}\n' \
                                        '<em>Сумма перевода в рублях:</em> {SUM_EUR_RE}\n' \
                                        '<em>Город сделки:</em> {CITY_RE}\n' \
                                        '<em>Время сделки:</em> {ORDER_TIME_RE}\n\n' \
                                        '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(
                        OPER_NAME_RE=data.get('OPER_NAME_RE'),
                        BANK_RE=data['BANK_RE'],
                        RUB_EURO_RATE=data['RUB_EURO_RATE'],
                        SUM_EUR_RE=data['SUM_EUR_RE'],
                        SUM_RUB_RE=data['SUM_RUB_RE'],
                        CITY_RE=data.get('CITY_RE'),
                        ORDER_TIME_RE=data['ORDER_TIME_RE'])
                    else:
                        if data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                            currency = _('KZT')
                            currency1 = _('тенге')
                            city_or_bank = _('Банк получателя')
                        else:
                            currency = _('EUR')
                            currency1 = _('евро')
                            city_or_bank = _('Город сделки')
                        client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                            '<em>Валютная операция:</em> {OPER_NAME_RE}\n' \
                                            '<em>Ваш Банк-отправитель:</em> {BANK_RE}\n' \
                                            '<em>Предлагаемый курс ({currency}/RUB):</em> {RUB_EURO_RATE}\n' \
                                            '<b>Курс является индикативным и фиксируется в момент сделки</b>\n' \
                                            '<em>Сумма получения в {currency1}:</em> {SUM_EUR_RE}\n' \
                                            '<em>Сумма перевода в рублях:</em> {SUM_RUB_RE}\n' \
                                            '<em>{city_or_bank}:</em> {CITY_RE}\n' \
                                            '<em>Время сделки:</em> {ORDER_TIME_RE}\n\n' \
                                            '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(
                            OPER_NAME_RE=data.get('OPER_NAME_RE'),
                            BANK_RE=data['BANK_RE'],
                            RUB_EURO_RATE=data['RUB_EURO_RATE'],
                            SUM_EUR_RE=data['SUM_EUR_RE'],
                            SUM_RUB_RE=data['SUM_RUB_RE'],
                            CITY_RE=data.get('CITY_RE'),
                            ORDER_TIME_RE=data['ORDER_TIME_RE'],
                            currency=currency,
                            currency1=currency1,
                            city_or_bank=city_or_bank)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    b1 = types.KeyboardButton(_('Да'))
                    b2 = types.KeyboardButton(_('Нет'))
                    markup.add(b1, b2)
                    client_warning_mess = _(
                        '<b>Регистрируя заявку, Вы подтверждаете, что ознакомились с документами, регулирующими правила совершения операций' \
                        ' по обмену валют в разделе <em>/documents</em></b>\n\n')
                    bot.send_message(message.chat.id, disc_status_mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                    bot.send_message(message.chat.id, client_order_mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                    bot.send_message(message.chat.id, client_warning_mess, parse_mode='html', reply_markup=markup)
            # 2.1.7 Обрабатываем заявку
            # Да
            elif message.text == _('Да') and data.get('FORM_ORDER_FLAG') and data.get('OPER_FLAG_EUR_RUB') and (not data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('BANK_FLAG') and data.get('SUM_RUB_FLAG') and data.get('CITY_RE_FLAG') and data.get('ORDER_CONFIRM_RE_FLAG'):
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                a = types.ReplyKeyboardRemove()
                if add_username == '':
                    from_id = message.from_user.id
                    first_name = message.from_user.first_name
                    username = '@' + message.chat.username if message.chat.username is not None else '-'
                else:
                    if 'user_ID' in ACTIVE_CONTACT_LIST[add_username].keys():
                        from_id = ACTIVE_CONTACT_LIST[add_username]['user_ID']
                    else:
                        from_id = 'Нет информации'
                    first_name = ACTIVE_CONTACT_LIST[add_username]['NameSurname']
                    username = add_username
                    data['REF_CODE_RE'] = ACTIVE_CONTACT_LIST[username]['Discount_Number']
                dealer = ACTIVE_CONTACT_LIST[username]['ContactDealer']
                client_mess = _('Ваша заявка передана оператору. В ближайшее время с Вами свяжется наш сотрудник {ContactDealer}.').format(
                    ContactDealer=dealer)
                date = datetime.now(tz).strftime('%d.%m.%Y')
                with open('C:/Users/admin/PycharmProjects/BotMain_v4_Monex/app/deals_ids.json', 'r', encoding='utf8') as f:
                    DealID_num = json.load(f)
                    DealID_num["EX"] += 0.0000001
                    DealID = "EX" + (str(format(DealID_num["EX"], '.7f'))).replace('.','')
                with open('C:/Users/admin/PycharmProjects/BotMain_v4_Monex/app/deals_ids.json', 'w', encoding='utf8') as f:
                    json.dump(DealID_num, f, ensure_ascii=False, indent=2)
                # date = datetime.utcfromtimestamp(message.json['date']).strftime('%Y-%m-%d %H:%M:%S')
                # TODO: НЕ ПЕРЕВОДИТЬ
                if data.get('OPER_FLAG_EUR_RUB_BACK'):
                    operator_mess = '<em>Источник:</em> Alpha_TG_Bot\n' \
                                '<em>Номер ордера:</em> {DealID}\n' \
                                '<em>Город сделки:</em> <b>#{CITY_RE}</b>\n' \
                                '<em>Клиент отдаст в евро:</em> <b>{SUM_RUB_RE}</b>\n' \
                                '<em>Банк-получатель клиента/Наличные:</em> <b>{BANK_RE}</b>\n' \
                                '<em>Имя клиента:</em> {first_name}\n' \
                                '<em>ID клиента:</em> {from_id}\n' \
                                '<em>Код реферальной программы:</em> {REF_CODE_RE}\n' \
                                '<em>Ник клиента:</em> {username}\n' \
                                '<em>Валютная операция:</em> <b>{OPER_NAME_RE}</b>\n' \
                                '<em>Предлагаемый курс (RUB/EUR):</em> {RUB_EURO_RATE}\n' \
                                '<em>Сумма перевода в рублях:</em> {SUM_EUR_RE}\n' \
                                '<em>Город внесения наличных:</em> {CASH_CITY}\n' \
                                '<em>Время сделки:</em> {ORDER_TIME_RE}\n' \
                                '<em>Время формирования заявки:</em> {date}\n' \
                                '<em>Кто свяжется по обмену:</em> {dealer}'.format(DealID=DealID,
                                                                                    first_name=first_name,
                                                                                    from_id=from_id,
                                                                                    REF_CODE_RE=data['REF_CODE_RE'],
                                                                                    username=username,
                                                                                    OPER_NAME_RE=data.get('OPER_NAME_RE'),
                                                                                    BANK_RE=data['BANK_RE'],
                                                                                    RUB_EURO_RATE=data['RUB_EURO_RATE'],
                                                                                    SUM_EUR_RE=data['SUM_EUR_RE'],
                                                                                    SUM_RUB_RE=data['SUM_RUB_RE'],
                                                                                    CITY_RE=data.get('CITY_RE'),
                                                                                    ORDER_TIME_RE=data['ORDER_TIME_RE'],
                                                                                    date=date,
                                                                                    CASH_CITY=data['CASH_CITY'],
                                                                                    dealer=dealer)
                else:
                    if data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                        currency = _('KZT')
                        currency1 = _('тенге')
                        city_or_bank = _('Банк получателя')
                    else:
                        currency = _('EUR')
                        currency1 = _('евро')
                        city_or_bank = _('Город сделки')
                    operator_mess = '<em>Источник:</em> Alpha_TG_Bot\n' \
                                    '<em>Номер ордера:</em> {DealID}\n' \
                                    '<em>{city_or_bank}:</em> <b>#{CITY_RE}</b>\n' \
                                    '<em>Клиент получит в {currency1}:</em> <b>{SUM_EUR_RE}</b>\n' \
                                    '<em>Банк-отправитель клиента/Наличные:</em> <b>{BANK_RE}</b>\n' \
                                    '<em>Имя клиента:</em> {first_name}\n' \
                                    '<em>ID клиента:</em> {from_id}\n' \
                                    '<em>Код реферальной программы:</em> {REF_CODE_RE}\n' \
                                    '<em>Ник клиента:</em> {username}\n' \
                                    '<em>Валютная операция:</em> <b>{OPER_NAME_RE}</b>\n' \
                                    '<em>Предлагаемый курс ({currency}/RUB):</em> {RUB_EURO_RATE}\n' \
                                    '<em>Сумма перевода в рублях:</em> {SUM_RUB_RE}\n' \
                                    '<em>Город внесения наличных:</em> {CASH_CITY}\n' \
                                    '<em>Время сделки:</em> {ORDER_TIME_RE}\n' \
                                    '<em>Время формирования заявки:</em> {date}\n' \
                                    '<em>Кто свяжется по обмену:</em> {dealer}'.format(DealID=DealID,
                                                                                    first_name=first_name,
                                                                                        from_id=from_id,
                                                                                        REF_CODE_RE=data['REF_CODE_RE'],
                                                                                        username=username,
                                                                                        OPER_NAME_RE=data.get('OPER_NAME_RE'),
                                                                                        BANK_RE=data['BANK_RE'],
                                                                                        RUB_EURO_RATE=data['RUB_EURO_RATE'],
                                                                                        SUM_EUR_RE=data['SUM_EUR_RE'],
                                                                                        SUM_RUB_RE=data['SUM_RUB_RE'],
                                                                                        CASH_CITY=data['CASH_CITY'],
                                                                                        CITY_RE=data.get('CITY_RE'),
                                                                                        ORDER_TIME_RE=data['ORDER_TIME_RE'],
                                                                                        date=date,
                                                                                        city_or_bank=city_or_bank,
                                                                                        currency=currency,
                                                                                        currency1=currency1,
                                                                                        dealer=dealer)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, client_mess, parse_mode='html', reply_markup=markup)
                bot.send_message(GROUP_CHAT_ID, operator_mess, parse_mode='html', reply_markup=a)
                if data.get('OPER_NAME_RE') ==_('Обмен РУБЛЕЙ на ЕВРО') and int(data['SUM_EUR_RE']) < 1000 or data.get('OPER_NAME_RE') ==_('Обмен ЕВРО на РУБЛИ') and int(data['SUM_EUR_RE']) < 100000:
                    client_mess1 = _('В соответствии с Правилами совершения операций обмена для сумм обмена менее 1000 евро'
                                     ' бесплатная доставка куратором до клиента не осуществляется. Убедительная просьба согласовать'
                                     ' вопрос доставки денег куратором и/или места встречи в личной беседе в ТГ.')
                    bot.send_message(message.chat.id, client_mess1, parse_mode='html', reply_markup=markup)
                dealer = ACTIVE_CONTACT_LIST[username]['ContactDealer']
                if len(data['REF_CODE_RE']) != 6:
                    partner = ''
                    partner_flag = False
                else:
                    for tg_nick, values in ACTIVE_CONTACT_LIST.items():
                        if values['Referral_Number'] == data['REF_CODE_RE']:
                            partner = tg_nick
                            partner_flag = True
                            break
                usdt_eur_rate = rates_funcs.scrab_usdt_euro_rate(username, 1)
                if data.get('OPER_NAME_RE') == _('Обмен ЕВРО на РУБЛИ'):
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'EUR=>RUB', 'RUB=>EUR', 'RUB', data['SUM_EUR_RE'], data['BANK_RE'], '',
                            data['RUB_EURO_RATE'], '/',
                            'EUR', 'Наличные', '', username, data['REF_CODE_RE'], data.get('CITY_RE'), '', '', '', '', '', '', '', 'План', '',
                            '', '', '', True, usdt_eur_rate, 1/usdt_eur_rate)
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'EUR=>RUB', 'RUB=>USDT', 'USDT', data['SUM_EUR_RE'], 'Bybit', '',
                            data['RUB_INFO']['p2p_rub_usdt'], '/',
                            'RUB', 'Тинькофф', '', '', '', '', '', '', '', '', '', '', '', 'План', '', '', 'eurrub2', '', '', '', '')
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'EUR=>RUB', 'RUB=>EUR', 'EUR', data['SUM_EUR_RE'], 'Наличные', '',
                            data['RUB_INFO']['usdt_eur_rate'],
                            '*', 'EUR', 'Наличные', '', '', '', '', 'NEW', '', '', '', '', '',
                            '', 'РасчБонПлан', '', '', 'eurrub3', 'VPR in 3', '', '', '')
                    calculate_indexes(deal_type='ER', partner_flag=partner_flag, eur_rate='')
                elif data.get('OPER_NAME_RE') == _('Обмен РУБЛЕЙ на ТЕНГЕ'):
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'RUB=>KZT', 'KZT=>RUB', 'KZT', data['SUM_EUR_RE'], data.get('CITY_RE'), '', data['RUB_EURO_RATE'], '*',
                            'RUB', data['BANK_RE'], '', username, data['REF_CODE_RE'], 'offline', '', '', '', '', '', '', '', 'План', '', '', '', '', True, usdt_eur_rate, 1/usdt_eur_rate)
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'RUB=>KZT', 'RUB=>USDT', 'RUB', '', data['BANK_RE'], '', data['RUB_INFO']['p2p_rub_usdt'],
                            '/', 'USDT', 'Binance', '', '', '', '', '', '', '', '', '', '',
                            '', 'План', '', '', '', '', '', '', '')  # курс rub usdt #добавить Binance, добавить куратора(ов) + оставить только дату
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'RUB=>KZT', 'USDT=>KZT', 'USDT', data['SUM_EUR_RE'], 'Binance',
                            '', data['RUB_INFO']['usdt_euro_rate'], '/', 'KZT', data.get('CITY_RE'), '', '', '', '', '', '', '', '', '', '',
                            '', 'План', '', '', 'rubeur', '', '', '', '')  # добавить Binance, добавить куратора(ов) + оставить только дату
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'RUB=>KZT', 'USDT=>USDT', 'USDT', 'rubkzt4', 'Binance',
                            '', '', '/', 'USDT', 'Наличные', '', '', '', '', 'VPR', '', '', '', '', '',
                            '', 'РасчБонПлан', '', '', 'rubeur4', 'VPR in 4', '', '', '')
                    eur_rate = rates_funcs.get_fiat_rates_tradingview()['EUR_USD']
                    calculate_indexes(deal_type='RK', partner_flag=partner_flag, eur_rate=eur_rate)
                else:
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'RUB=>EUR', 'EUR=>RUB', 'EUR', data['SUM_EUR_RE'], 'Наличные', '', data['RUB_EURO_RATE'], '*',
                            'RUB', data['BANK_RE'], '', username, data['REF_CODE_RE'], data.get('CITY_RE'), '', '', '', '', '', '', '', 'План', '', '', '', '', True, usdt_eur_rate, 1/usdt_eur_rate)
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'RUB=>EUR', 'RUB=>USDT', 'RUB', '', data['BANK_RE'], '', data['RUB_INFO']['p2p_rub_usdt'],
                            '/', 'USDT', 'Binance', '', '', '', '', '', '', '', '', '', '',
                            '', 'План', '', '', '', '', '', '', '')  # курс rub usdt #добавить Binance, добавить куратора(ов) + оставить только дату
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'RUB=>EUR', 'USDT=>EUR', 'USDT', '', 'Binance',
                            '', data['RUB_INFO']['usdt_euro_rate'], '*', 'EUR', 'Наличные', '', '', '', '', 'VPR', '', '', '', '', '',
                            '', 'РасчБонПлан', '', '', '', 'VPR in 3', '', '', '')  # добавить Binance, добавить куратора(ов) + оставить только дату
                    calculate_indexes(deal_type='RE', partner_flag=partner_flag, eur_rate='')
                #update_contact(username=username, city=CITY_RE, acc_type_from=BANK_RE, curr_from='RUB')
                add_border()
            # Нет
            elif message.text == _('Нет') and data.get('FORM_ORDER_FLAG') and data.get('OPER_FLAG_EUR_RUB') and (not data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('BANK_FLAG') and data.get('SUM_RUB_FLAG') and data.get('ORDER_CONFIRM_RE_FLAG'):
                data['PENDING_ORDER_FLAG'] = True
                DOCS_FLAG = False
                a = types.ReplyKeyboardRemove()
                mess = _('<b>Вы можете создать отложенный ордер!</b>\n' \
                        'Укажите свой курс и, как только стоимость актива совпадет с указанной, мы отправим Вам уведомление!')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton(_('Создать отложенный ордер'))
                b2 = types.KeyboardButton(_('Главное меню'))
                markup.add(b1, b2)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # Отложенный ордер (отказ)
            elif message.text == _('Главное меню') and data.get('FORM_ORDER_FLAG') and data.get('OPER_FLAG_EUR_RUB') and (not data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('BANK_FLAG') and data.get('SUM_RUB_FLAG') and data.get('ORDER_CONFIRM_RE_FLAG') and data.get('PENDING_ORDER_FLAG'):
                data['PENDING_ORDER_FLAG'] = False
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, text=_('Выберите доступную команду из меню'), parse_mode='html',
                                reply_markup=markup)
            # Отложенный ордер
            elif message.text == _('Создать отложенный ордер') and data.get('FORM_ORDER_FLAG') and data.get('OPER_FLAG_EUR_RUB') and (
                    not data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('BANK_FLAG') and data.get('SUM_RUB_FLAG') and data.get('ORDER_CONFIRM_RE_FLAG') and data.get('PENDING_ORDER_FLAG'):
                a = types.ReplyKeyboardRemove()
                mess = _('Введите, пожалуйста, желаемый курс сделки.')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=a)
            # Ввод желаемого курса
            # Неверный формат
            elif not message.text.replace(".", "").replace(",", "").isnumeric() and data.get('FORM_ORDER_FLAG') and data.get('OPER_FLAG_EUR_RUB') and (
                    not data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('BANK_FLAG') and data.get('SUM_RUB_FLAG') and data.get('ORDER_CONFIRM_RE_FLAG') and data.get('PENDING_ORDER_FLAG'):
                a = types.ReplyKeyboardRemove()
                mess = _(
                    'Вы ввели некорректную сумму.\nДля формирования заявки просим повторно ввести курс, учитывая ограничения:\n' \
                    '<b><em>Вводимое значение должно быть числом, убедитесь в отсутствии букв в тексте сообщения</em></b>.\n' \
                    '<em>Если ввели/выбрали неверное значение на одном из этапов формирования заявки, перезапустите команду: /form_order</em>')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=a)
            # Курс введен
            elif message.text.replace(".", "").replace(",", "").isnumeric() and data.get('FORM_ORDER_FLAG') and data.get('OPER_FLAG_EUR_RUB') and (
                    not data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('BANK_FLAG') and data.get('SUM_RUB_FLAG') and data.get('ORDER_CONFIRM_RE_FLAG') and data.get('PENDING_ORDER_FLAG'):
                data['PENDING_ORDER_FLAG'] = False
                a = types.ReplyKeyboardRemove()
                client_mess = _('Ваш ордер создан. Мы уведомим Вас, как только курс достигнет указанного значения!')
                from_id = message.from_user.id
                first_name = message.from_user.first_name
                username = '@' + message.chat.username if message.chat.username is not None else '-'
                date = datetime.now(tz).strftime('%d.%m.%Y')
                # date = datetime.utcfromtimestamp(message.json['date']).strftime('%Y-%m-%d %H:%M:%S')
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                dealer = ACTIVE_CONTACT_LIST[username]['ContactDealer']
                deal_type = 'RUB=>EUR' if data.get('OPER_NAME_RE') ==_('Обмен РУБЛЕЙ на ЕВРО') else 'EUR=>RUB'
                write_pending_order(createDateTime=date, dealer=dealer, dealType=deal_type, exchFROM_Amount=data['SUM_EUR_RE'],
                                    orderRate=message.text.replace(".", ","), user_ID=message.from_user.id,
                                    tg_Contact=username, city=data.get('CITY_RE'), currStatus='Создан', chat_ID=message.chat.id, )
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, client_mess, parse_mode='html', reply_markup=markup)
            ###2.2.1 Обмен USDT на ЕВРО
            elif (message.text == _('Обмен USDT на ЕВРО') or message.text == _('Обмен USDT на РУБЛИ') or message.text == _('Обмен USDT на ГРИВНЫ') or message.text == _('Обмен USDT на ТЕНГЕ')) and data.get('FORM_ORDER_FLAG'):
                data['OPER_NAME_UE'] = str(message.text)
                data['OPER_FLAG_EUR_RUB'] = False
                data['OPER_FLAG_USDT_EURO'] = True
                if message.text == _('Обмен USDT на РУБЛИ'):
                    data['OPER_FLAG_USDT_EURO_BACK'] = True
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    b1 = types.KeyboardButton(_('Сбербанк'))
                    b2 = types.KeyboardButton(_('Тинькофф'))
                    b3 = types.KeyboardButton(_('Райффайзен'))
                    b4 = types.KeyboardButton(_('Прочие'))
                    b5 = types.KeyboardButton(_('Наличные'))
                    mess = _('Выберите банк, на счета которого планируете получить рубли:\n' \
                        '1. Сбербанк\n' \
                        '2. Тинькофф\n' \
                        '3. Райффайзен\n' \
                        '4. Наличные\n'
                        '5. Прочие\n')
                    markup.add(b1, b2, b3, b4, b5, mb)
                elif message.text == _('Обмен USDT на ГРИВНЫ'):
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    mess = _('Выберите банк, на счета которого планируете получить гривны:\n' \
                        '1. Monobank\n' \
                        '2. PUMB\n' \
                        '3. ПриватБанк\n' \
                        '4. A-Банк\n'
                        '5. Izibank\n')
                    markup.add(*ua_bank_names, mb)
                elif message.text == _('Обмен USDT на ТЕНГЕ'):
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    mess = _('Выберите банк, на счета которого планируете получить тенге:\n' \
                        '1. Kaspi Bank\n' \
                        '2. Halyk Bank\n' \
                        '3. ЦентрКредит Банк\n' \
                        '4. Jysan Bank\n'
                        '5. Forte Bank\n'
                        '6. Altyn Bank\n'
                        '7. Freedom Bank\n')
                    markup.add(*kzt_bank_names, mb)
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    order_city_buttons = form_order_city_buttons(_(CITY_BUTTONS))
                    markup.add(*order_city_buttons, mb)
                    mess = _('Выберите представленный в списке город, в котором планируете провести сделку')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # 2.2.2 Обработка города
            elif (message.text == _('Другая локация')) and (data.get('FORM_ORDER_FLAG')) and (not data.get('OPER_FLAG_EUR_RUB')) and (
                    data.get('OPER_FLAG_USDT_EURO')) \
                    and (not data.get('CITY_UE_FLAG')) and (not data.get('ANOTHER_CITY_UE_FLAG')) and not data.get('CASH_FLAG'):
                data['ANOTHER_CITY_UE_FLAG'] = True
                mess = _('<b><em>Введите город сделки</em></b>')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons, mb)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif (message.text == _('Наличные')) and (data.get('FORM_ORDER_FLAG')) and (not data.get('OPER_FLAG_EUR_RUB')) and (
                    data.get('OPER_FLAG_USDT_EURO')) and (not data.get('CITY_UE_FLAG')) and (not data.get('ANOTHER_CITY_UE_FLAG')):
                data['CASH_FLAG'] = True
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton(_('Москва'))
                b2 = types.KeyboardButton(_('Санкт-Петербург'))
                b3 = types.KeyboardButton(_('Черногория'))
                markup.add(b1, b2, b3, mb)
                mess = _('Введите город получения наличных денег')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # 2.2.3 Сумма сделки в евро
            # Здесь в CITY_UE записываем банк получателя, если сделка usdt=>rub или usdt=>uah
            elif ((message.text in [_('Москва'), _('Санкт-Петербург'), _('Черногория')] and data.get('CASH_FLAG')) or message.text in cities or message.text in ru_bank_names or message.text in ua_bank_names or message.text in kzt_bank_names or data.get('ANOTHER_CITY_UE_FLAG') or data.get('CASH_FLAG')) and (data.get('FORM_ORDER_FLAG')) and (not data.get('OPER_FLAG_EUR_RUB')) \
                    and (data.get('OPER_FLAG_USDT_EURO')) and (not data.get('CITY_UE_FLAG')):
                a = types.ReplyKeyboardRemove()
                data['CITY_UE_FLAG'] = True
                if message.text in [_('Москва'), _('Санкт-Петербург'), _('Черногория')]:
                    data['CITY_UE'] = 'Наличные'
                    data['CASH_CITY'] = message.text
                else:
                    data['CITY_UE'] = message.text
                    data['CASH_CITY'] = ''
                if data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ'):
                    mess = _('<b>Какую сумму в рублях хотите получить?</b>\n<em>(Введите целое число, разрядность которого не превышает 8 знаков)</em>\n\n'\
                             '<b>Минимальная сумма к обмену 10000 рублей</b>')
                elif data.get('OPER_NAME_UE') == _('Обмен USDT на ГРИВНЫ'):
                    mess = _('<b>Какую сумму в гривнах хотите получить?</b>\n<em>(Введите целое число, разрядность которого не превышает 8 знаков)</em>\n\n'\
                             '<b>Минимальная сумма к обмену 4000 гривен</b>')   
                elif data.get('OPER_NAME_UE') == _('Обмен USDT на ТЕНГЕ'):
                    mess = _('<b>Какую сумму в тенге хотите получить?</b>\n<em>(Введите целое число, разрядность которого не превышает 8 знаков)</em>\n\n'\
                             '<b>Минимальная сумма к обмену 50000 тенге</b>')   
                else:
                    currency = 'евро'
                    currency2 = 'ЕВРО'
                    lim1 = '100'
                    lim2 = '500'
                    mess = _(
                        '<b>Какую сумму в {currency} хотите получить?</b>\n<em>(Введите целое число, разрядность которого не превышает 8 знаков)</em>\n\n' \
                        '<b>Минимальная сумма сделки зависит от выбранного ранее города:</b>\n' \
                        'Херцег Нови, Бар, Будва, Тиват - {lim1} {currency2}\n' \
                        'Остальные города - {lim2} {currency2}').format(currency=currency,
                                                                        currency2=currency2,
                                                                        lim1=lim1,
                                                                        lim2=lim2)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons, mb)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=a)  # для теста
            # 2.2.4 Обработка суммы сделки
            # Если ввели сумму не в том формате и с ограничение 500 евро
            elif ((not message.text.isdigit() or len(message.text) > 8) \
                or ((int(message.text) < 100 and data.get('OPER_NAME_UE') == _('Обмен USDT на ЕВРО') or int(message.text) < 10000 and data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ') or int(message.text) < 4000 and data.get('OPER_NAME_UE') == _('Обмен USDT на ГРИВНЫ') or int(message.text) < 50000 and data.get('OPER_NAME_UE') == _('Обмен USDT на ТЕНГЕ')) and (data.get('CITY_UE') in [_('Херцег Нови'), _('Бар'), _('Будва'), _('Тиват')] or data.get('CITY_UE') in ru_bank_names or data.get('CITY_UE') in ua_bank_names or data.get('CITY_UE') in kzt_bank_names)) \
                or ((int(message.text) < 500 and data.get('OPER_NAME_UE') == _('Обмен USDT на ЕВРО') or int(message.text) < 50000 and data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ')) and data.get('CITY_UE') not in [_('Херцег Нови'), _('Бар'), _('Будва'), _('Тиват')] and data.get('CITY_UE') not in ru_bank_names and data.get('CITY_UE') not in ua_bank_names and data.get('CITY_UE') not in kzt_bank_names)) \
                    and (data.get('FORM_ORDER_FLAG')) and (not data.get('OPER_FLAG_EUR_RUB')) and (data.get('OPER_FLAG_USDT_EURO')) \
                    and (data.get('CITY_UE_FLAG')) and (not data.get('SUM_USDT_FLAG')):
                a = types.ReplyKeyboardRemove()
                if data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ'):
                    mess = _('Вы ввели некорректную сумму.\nДля формирования заявки просим повторно ввести сумму, учитывая ограничения:\n' \
                            '<b><em>1.Целое число, разрядность которого не превышает 8 знаков</em></b>.\n' \
                            '<b><em>2.Минимальная сумма сделки 10000 рублей</em></b>')
                elif data.get('OPER_NAME_UE') == _('Обмен USDT на ГРИВНЫ'):
                    mess = _('Вы ввели некорректную сумму.\nДля формирования заявки просим повторно ввести сумму, учитывая ограничения:\n' \
                            '<b><em>1.Целое число, разрядность которого не превышает 8 знаков</em></b>.\n' \
                            '<b><em>2.Минимальная сумма сделки 4000 гривен</em></b>')
                elif data.get('OPER_NAME_UE') == _('Обмен USDT на ТЕНГЕ'):
                    mess = _('Вы ввели некорректную сумму.\nДля формирования заявки просим повторно ввести сумму, учитывая ограничения:\n' \
                            '<b><em>1.Целое число, разрядность которого не превышает 8 знаков</em></b>.\n' \
                            '<b><em>2.Минимальная сумма сделки 50000 тенге</em></b>')
                else:
                    currency = 'евро'
                    currency2 = 'ЕВРО'
                    lim1 = '100'
                    lim2 = '500'
                    mess = _(
                        'Вы ввели некорректную сумму.\nДля формирования заявки просим повторно ввести сумму, учитывая ограничения:\n' \
                        '<b><em>1.Целое число, разрядность которого не превышает 8 знаков</em></b>.\n' \
                        '<b><em>2.Минимальная сумма сделки в Херцег Нови, Баре, Тивате и Будве - {lim1} {currency2}, в остальных городах - {lim2} {currency2}</em></b>.\n\n' \
                        '<em>Если ввели/выбрали неверное значение на одном из этапов формирования заявки, перезапустите команду: /form_order</em>').format(
                        lim1=lim1,
                        lim2=lim2,
                        currency2=currency2)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons, mb)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=a)
            # Если введенная сумма - корректная, то переходим к проверке блокчейна и кошелька
            elif ((message.text.isdigit() and len(message.text) <= 8) \
            and (((int(message.text) >= 100 and data.get('OPER_NAME_UE') == _('Обмен USDT на ЕВРО')) or (int(message.text) >= 10000 and data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ')) or (int(message.text) >= 4000 and data.get('OPER_NAME_UE') == _('Обмен USDT на ГРИВНЫ') or (int(message.text) >= 50000 and data.get('OPER_NAME_UE') == _('Обмен USDT на ТЕНГЕ'))) and (CITY_UE in [_('Херцег Нови'), _('Бар'), _('Будва'), _('Тиват')] or CITY_UE in ru_bank_names or CITY_UE in ua_bank_names or CITY_UE in kzt_bank_names)) \
            or ((int(message.text) >= 500 and data.get('OPER_NAME_UE') == _('Обмен USDT на ЕВРО')) or (int(message.text) >= 50000 and data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ')) and CITY_UE not in [_('Херцег Нови'), _('Бар'), _('Будва'), _('Тиват')]))) \
                and (data.get('FORM_ORDER_FLAG')) and (not data.get('OPER_FLAG_EUR_RUB')) and (data.get('OPER_FLAG_USDT_EURO')) \
                and (data.get('CITY_UE_FLAG')) and (not data.get('SUM_USDT_FLAG')) and (not data.get('ORDER_CONFIRM_UE_FLAG')) and not data.get('CHOOSE_BLOCKCHAIN') and not data.get('CHECK_ADDRESS'):
                data['CHOOSE_BLOCKCHAIN'] = True
                data['SUM_USDT_FLAG'] = True
                # Сохраним в глобальных переменных новые значения курсов
                data['SUM_EUR_UE'] = int(message.text)
                b1 = types.KeyboardButton(_('Tronchain'))
                b2 = types.KeyboardButton(_('Etherium'))
                b3 = types.KeyboardButton(_('Binance/BybitChain'))
                b4 = types.KeyboardButton(_('Binance/BybitID'))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(b1, b2, b3, b4, mb)
                mess = _('Выберите блокчейн, через который будете отправлять USDT')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                # Ввод адреса отправителя
            elif (message.text in ['Tronchain']) \
                    and (data.get('FORM_ORDER_FLAG')) and (not data.get('OPER_FLAG_EUR_RUB')) and (data.get('OPER_FLAG_USDT_EURO')) \
                    and (data.get('CITY_UE_FLAG')) and (data.get('SUM_USDT_FLAG')) and (not data.get('ORDER_CONFIRM_UE_FLAG')) and data.get('CHOOSE_BLOCKCHAIN') and not data.get('CHECK_ADDRESS'):
                data['BLOCKCHAIN'] = message.text
                data['CHECK_ADDRESS'] = True
                markup = types.ReplyKeyboardRemove()
                mess = _('Введите свой адрес кошелька, с которого планируется отправка')  # Время по Черногории
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif (message.text[0] != 'T' or len(message.text) < 32) and message.text not in ['Etherium', 'Binance/BybitChain',
                                                                                             'Binance/BybitID'] and (data.get('FORM_ORDER_FLAG')) and (not data.get('OPER_FLAG_EUR_RUB')) and (data.get('OPER_FLAG_USDT_EURO')) \
                    and (data.get('CITY_UE_FLAG')) and (data.get('SUM_USDT_FLAG')) and (not data.get('ORDER_TIME_FLAG_UE')) and (not data.get('ORDER_CONFIRM_UE_FLAG')) and data.get('CHECK_ADDRESS') and data.get('CHOOSE_BLOCKCHAIN'):
                mess = 'Вы ввели некорректный адрес, попробуйте еще раз'
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                # Если кошелек корректно введен, то переходим к расчету курса и формированию промежуточной заявки
            elif (message.text[0] == 'T' and len(message.text) > 32 or message.text in ['Etherium', 'Binance/BybitChain',
                                                                                        'Binance/BybitID']) and (data.get('FORM_ORDER_FLAG')) and (not data.get('OPER_FLAG_EUR_RUB')) and (data.get('OPER_FLAG_USDT_EURO')) \
                    and (data.get('CITY_UE_FLAG')) and (data.get('SUM_USDT_FLAG')) and (not data.get('ORDER_TIME_FLAG_UE')) and (not data.get('ORDER_CONFIRM_UE_FLAG')) and (data.get('CHECK_ADDRESS') and data.get('CHOOSE_BLOCKCHAIN') or message.text in ['Etherium', 'Binance/BybitChain', 'Binance/BybitID']):
                data['ORDER_TIME_FLAG_UE'] = True
                if message.text in ['Etherium', 'Binance/BybitChain', 'Binance/BybitID']:
                    data['BLOCKCHAIN'] = message.text
                    data['CHECK_ADDRESS'] = True
                    data['ADDRESS'] = 'Не введен'
                else:
                    mess = '<em>Пожалуйста, подождите... \nОбычно проверка занимает не более 30 секунд </em>'
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                    data['ADDRESS'] = message.text
                username = '@' + message.chat.username if message.chat.username is not None else message.chat.id
                # Сохраним в глобальных переменных новые значения курсов
                if data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ'):
                    usdt_info = rates_funcs.compute_usdt_rub_amount(data['SUM_EUR_UE'], username, data.get('CASH_FLAG'), data['CITY_UE']) #здесь в sum_eur_ue рубли
                    data['SUM_USDT_UE'] = usdt_info['usdt_amount']
                    data['USDT_EURO_RATE'] = usdt_info['high_rate'] if data['SUM_EUR_UE']>499999 else usdt_info['low_rate'] # здесь записана пара USDT_RUB_RATE (для упрощения)
                    data['USDT_EURO_RATE'] = data['USDT_EURO_RATE'] #if CITY_UE != _('Херцег Нови') else data['USDT_EURO_RATE'] - 0.005
                    data['SUM_USDT_UE'] = math.ceil(data['SUM_EUR_UE'] / data['USDT_EURO_RATE']) # Здесь сумма рублей, которые получит клиент
                    data['USDT_EURO_RATE_GS'] = usdt_info['usdt_rub_rate_bybit']  # без учета нормы рентабельности
                elif data.get('OPER_NAME_UE') == _('Обмен USDT на ГРИВНЫ'):
                    usdt_info = rates_funcs.compute_usdt_uah_amount(data['SUM_EUR_UE'], username, data['CITY_UE']) #здесь в sum_eur_ue гривны
                    data['SUM_USDT_UE'] = usdt_info['usdt_amount']
                    data['USDT_EURO_RATE'] = usdt_info['high_rate'] if data['SUM_EUR_UE']>200000 else usdt_info['low_rate'] # здесь записана пара USDT_RUB_RATE (для упрощения)
                    data['USDT_EURO_RATE'] = data['USDT_EURO_RATE'] #if CITY_UE != _('Херцег Нови') else data['USDT_EURO_RATE'] - 0.005
                    data['SUM_USDT_UE'] = math.ceil(data['SUM_EUR_UE'] / data['USDT_EURO_RATE']) # Здесь сумма рублей, которые получит клиент
                    data['USDT_EURO_RATE_GS'] = usdt_info['usdt_uah_rate_bybit']  # без учета нормы рентабельности
                elif data.get('OPER_NAME_UE') == _('Обмен USDT на ТЕНГЕ'):
                    usdt_info = rates_funcs.compute_usdt_kzt_amount(data['SUM_EUR_UE'], username, data['CITY_UE']) #здесь в sum_eur_ue тенге
                    data['SUM_USDT_UE'] = usdt_info['usdt_amount']
                    data['USDT_EURO_RATE'] = usdt_info['high_rate'] if data['SUM_EUR_UE']>250000 else usdt_info['low_rate'] # здесь записана пара USDT_RUB_RATE (для упрощения)
                    data['USDT_EURO_RATE'] = data['USDT_EURO_RATE'] #if CITY_UE != _('Херцег Нови') else data['USDT_EURO_RATE'] - 0.005
                    data['SUM_USDT_UE'] = math.ceil(data['SUM_EUR_UE'] * data['USDT_EURO_RATE']) # Здесь сумма рублей, которые получит клиент
                    data['USDT_EURO_RATE_GS'] = usdt_info['usdt_kzt_rate_bybit']  # без учета нормы рентабельности
                else:
                    usdt_info = rates_funcs.compute_usdt_euro_amount(data['SUM_EUR_UE'], username)
                    data['SUM_USDT_UE'] = usdt_info['usdt_amount']
                    data['USDT_EURO_RATE'] = usdt_info['high_rate'] if data['SUM_EUR_UE']>4999 else usdt_info['low_rate']
                    data['USDT_EURO_RATE'] = data['USDT_EURO_RATE'] #if CITY_UE != _('Херцег Нови') else data['USDT_EURO_RATE'] - 0.005
                    data['SUM_USDT_UE'] = math.ceil(data['SUM_EUR_UE'] / data['USDT_EURO_RATE'])
                    data['USDT_EURO_RATE_GS'] = usdt_info['usdt_eur_rate_gs']  # без учета нормы рентабельности
                if data.get('BLOCKCHAIN') == 'Tronchain':
                    try:
                        all_data_trc10 = get_trc_data('TRC-10', data['ADDRESS'])
                        all_data_trc20 = get_trc_data('TRC-20', data['ADDRESS'])
                        data['RISK_TRC'] = check_risk_trc(all_data_trc10, all_data_trc20)
                        if data['RISK_TRC']:
                            data['RISK_TRC'] = 'Обнаружены подозрительные транзакции'
                        else:
                            data['RISK_TRC'] = 'Подозрительные транзакции не обнаружены'
                    except Exception as e:
                        print('Exception: ' + str(e))
                        data['RISK_TRC'] = 'Не удалось проверить'
                else:
                    data['RISK_TRC'] = 'Без проверки'
                msk_current_time = datetime.now(tz)
                msk_minutes = msk_current_time.hour * 60 + msk_current_time.minute
                # предлагаем каждые полчаса: для этого переведем все границы в минуты
                time_borders = {
                    0 * 60: '00:00 - 02:00',
                    2 * 60: '02:00 - 04:00',
                    4 * 60: '04:00 - 06:00',
                    6 * 60: '06:00 - 08:00',
                    8 * 60: '08:00 - 10:00',
                    10 * 60: '10:00 - 12:00',
                    12 * 60: '12:00 - 14:00',
                    14 * 60: '14:00 - 16:00',
                    16 * 60: '16:00 - 18:00',
                    18 * 60: '18:00 - 20:00',
                    20 * 60: '20:00 - 22:00'
                }
                time_buttons = [types.KeyboardButton(time_period) for high_board, time_period in time_borders.items() if
                                msk_minutes < high_board]
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(*time_buttons)
                markup.add(types.KeyboardButton(_('Другой день')), mb)
                mess = _('Выберите период времени, когда Вам было бы удобно осуществить сделку')  # Время по Черногории
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
                # 2.1.7. Предлагаем ввести или согласиться со своим реферальным кодом
            elif (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_USDT_EURO')) and (not data.get('OPER_FLAG_EUR_RUB')) \
                    and (data.get('CITY_UE_FLAG')) and (data.get('SUM_USDT_FLAG')) and (data.get('ORDER_TIME_FLAG_UE')) and (not data.get('FRIEND_REF_FLAG_UE')) and (
                    not data.get('ORDER_CONFIRM_UE_FLAG')):
                data['FRIEND_REF_FLAG_UE'] = True
                #ACTIVE_CONTACT_LIST = scrab_contact_list()
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                all_user_ids = [user_info['user_ID'] for user_info in ACTIVE_CONTACT_LIST.values()]
                data['ORDER_TIME_UE'] = message.text
                if (username not in ACTIVE_CONTACT_LIST) and (user_id not in all_user_ids):
                    existed_disc_codes = [one_doc['Discount_Number'] for one_doc in ACTIVE_CONTACT_LIST.values()]
                    existed_ref_codes = [one_doc['Referral_Number'] for one_doc in ACTIVE_CONTACT_LIST.values() if 'Referral_Number' in one_doc]
                    while True:
                        s = string.ascii_lowercase + string.ascii_uppercase + string.digits
                        disc_code = ''.join(random.sample(s, 4))
                        ref_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                        if disc_code not in existed_disc_codes and ref_code not in existed_ref_codes:
                            break
                    discount = '0%'
                    referal_mess = _('Вы впервые оформляете заявку.\n' \
                                    'Ваш код дисконтной программы: <b><em>{disc_code}</em></b>\n' \
                                    'Ваш код реферальной программы: <b><em>{ref_code}</em></b>\n' \
                                    'Ваша текущая скидка: {discount}\n\n' \
                                    '<b>Просьба выбрать в меню одну из опций:\n' \
                                    '1. Оставить свой код\n' \
                                    '2. Ввести код друга</b>').format(disc_code=disc_code,
                                                                        ref_code=ref_code,
                                                                        discount=discount)
                    write_contact(TG_Contact=username, user_ID=message.from_user.id, NameSurname=message.from_user.full_name,
                                AccTypeFROM='', CurrFROM='USDT',
                                City=data['CITY_UE'], ContactType='Клиент', ContactDealer='Alpha_TG_Bot', CurrStatus='Активный',
                                Discount_Number=disc_code, Referral_Number=ref_code)
                else:
                    if username in ACTIVE_CONTACT_LIST:
                        disc_code = ACTIVE_CONTACT_LIST[username]['Discount_Number']
                        ref_code = ACTIVE_CONTACT_LIST[username]['Referral_Number']
                        discount = str(float(ACTIVE_CONTACT_LIST[username]['Discount'].replace(',','.'))*100) + '%'
                    else:
                        userids_names = {user_info['user_ID']: username for username, user_info in ACTIVE_CONTACT_LIST.items()}
                        disc_code = ACTIVE_CONTACT_LIST[userids_names[user_id]]['Discount_Number']
                        ref_code = ACTIVE_CONTACT_LIST[username]['Referral_Number']
                        discount = str(float(ACTIVE_CONTACT_LIST[username]['Discount'].replace(',','.'))*100) + '%'
                    referal_mess = _('Ваш код дисконтной программы: <b><em>{disc_code}</em></b>\n' \
                                    'Ваш код реферальной программы: <b><em>{ref_code}</em></b>\n' \
                                    'Ваша текущая скидка: <b><em>{discount}</em></b>\n\n' \
                                    '<b>Просьба выбрать в меню одну из опций:\n' \
                                    '1. Оставить свой код\n' \
                                    '2. Ввести код друга</b>').format(disc_code=disc_code,
                                                                    ref_code=ref_code,
                                                                    discount=discount)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                b1 = types.KeyboardButton(_('Оставить свой код'))
                b2 = types.KeyboardButton(_('Ввести код друга'))
                b3 = types.KeyboardButton(_('Поиск контакта'))
                markup.add(b1, b2, b3, mb) if ACTIVE_CONTACT_LIST[username]['ContactType'] in ['Куратор', 'Партнер'] else markup.add(b1, b2, mb)
                bot.send_message(message.chat.id, referal_mess, parse_mode='html', reply_markup=markup)
            # 2.1.8.2 Если ввод промокода друга
            elif message.text == _('Ввести код друга') and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_USDT_EURO')) and (
                    not data.get('OPER_FLAG_EUR_RUB')) \
                    and (data.get('CITY_UE_FLAG')) and (data.get('SUM_USDT_FLAG')) and (data.get('ORDER_TIME_FLAG_UE')) and (data.get('FRIEND_REF_FLAG_UE')) and (
                    not data.get('ORDER_CONFIRM_UE_FLAG')):
                a = types.ReplyKeyboardRemove()
                mess = _(
                    '<b>Введите дисконтный <em>(4 символа)</em> или реферальной <em>(6 символов)</em> программы Вашего друга</b>')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=a)
            elif (message.text == _('Оставить свой код') and data.get('FRIEND_REF_FLAG_UE')) or (data.get('FORM_ORDER_FLAG')) and not data.get('FIND_USER_FLAG') and message.text != _('Поиск контакта') and (
                    data.get('OPER_FLAG_USDT_EURO')) and \
                    (not data.get('OPER_FLAG_EUR_RUB')) and (data.get('CITY_UE_FLAG')) and (data.get('SUM_USDT_FLAG')) and (data.get('ORDER_TIME_FLAG_UE')) and (
                    data.get('FRIEND_REF_FLAG_UE')) and \
                    (not data.get('RES_ORDER_FLAG_UE')) and (not data.get('ORDER_CONFIRM_UE_FLAG')):
                a = types.ReplyKeyboardRemove()
                data['RES_ORDER_FLAG_UE'] = True
                data['ORDER_CONFIRM_UE_FLAG'] = True
                #ACTIVE_CONTACT_LIST = scrab_contact_list()  # необходимо заново считать контакты, так как в предыдущем шаге мы создаем нового клиента
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                username = '@' + message.chat.username if message.chat.username is not None else 'None'
                user_id = message.from_user.id
                all_user_ids = [user_info['user_ID'] for user_info in ACTIVE_CONTACT_LIST.values()]
                disc_values = {one_doc['Discount_Number']: one_doc['Discount'] for one_doc in ACTIVE_CONTACT_LIST.values() if
                            'Discount' in one_doc}
                disc_nicks = {one_doc['Discount_Number']: nick for nick, one_doc in ACTIVE_CONTACT_LIST.items() if 'Discount_Number' in one_doc}
                disc_ids = {one_doc['Discount_Number']: one_doc['user_ID'] for one_doc in ACTIVE_CONTACT_LIST.values() if 'Discount_Number' in one_doc}
                refs_nicks = {one_doc['Referral_Number']: nick for nick, one_doc in ACTIVE_CONTACT_LIST.items() if 'Referral_Number' in one_doc}
                refs_ids = {one_doc['Referral_Number']: one_doc['user_ID'] for one_doc in ACTIVE_CONTACT_LIST.values() if 'Referral_Number' in one_doc}
                if message.text == _('Оставить свой код'):
                    data['REF_CODE_UE'] = ACTIVE_CONTACT_LIST[username]['Discount_Number']
                else:
                    data['REF_CODE_UE'] = message.text
                if len(data.get('REF_CODE_UE')) == 4 and data.get('REF_CODE_UE').strip() in disc_values:
                    data['DISCOUNT_UE'] = disc_values[data['REF_CODE_UE']]
                    disc_status_mess = _('Дисконтный код <b><em>{REF_CODE_UE}</em></b> найден.\n' \
                                        'Дополнительные баллы будут начислены пользователю <b><em>{user_nick} (ID: {user_id})\n\n' \
                                        'Для получения подробной информации о реферальной программе воспользуйтесь командой /refferal</em></b>').format(
                        REF_CODE_UE=data['REF_CODE_UE'],
                        user_nick=disc_nicks[data['REF_CODE_UE']],
                        user_id=disc_ids[data['REF_CODE_UE']])
                elif len(data.get('REF_CODE_UE')) == 6 and data.get('REF_CODE_UE').strip() in refs_nicks and data.get('REF_CODE_UE') != ACTIVE_CONTACT_LIST[username]['Referral_Number']:
                    data['DISCOUNT_UE'] = ACTIVE_CONTACT_LIST[username]['Discount']
                    disc_status_mess = _('Реферальный код <b><em>{REF_CODE_UE}</em></b> найден.\n' \
                                        'Дополнительные баллы будут начислены пользователю <b><em>{user_nick} (ID: {user_id})</em></b>\n\n' \
                                        '<em>После совершения операции Вам также будут начислены дополнительные баллы, которые влияют на размер итоговой скидки!\n\n' \
                                        'Для получения подробной информации о бонусной программе воспользуйтесь командой /refferal</em>').format(
                        REF_CODE_UE=data['REF_CODE_UE'],
                        user_nick=refs_nicks[data['REF_CODE_UE']],
                        user_id=refs_ids[data['REF_CODE_UE']])
                elif data.get('REF_CODE_UE') == ACTIVE_CONTACT_LIST[username]['Referral_Number']:
                    data['DISCOUNT_UE'] = ACTIVE_CONTACT_LIST[username]["Discount"]
                    disc_status_mess = _('Вы не можете использовать свой реферальный код <b><em>{REF_CODE_UE}</em></b> в своих сделках.\n' \
                                        'Для формирования итоговой заявки мы использовали Ваш дисконтный код <b>{disc_code}</b>,' \
                                        ' предоставляющий скидку <b>{disc}%.</b>\n\n' \
                                        '<em>После совершения операции Вам также будут начислены дополнительные баллы, которые влияют на размер итоговой скидки!\n\n' \
                                        'Для получения подробной информации о бонусной программе воспользуйтесь командой /refferal</em>').format(
                        REF_CODE_UE=data['REF_CODE_UE'],
                        disc_code=ACTIVE_CONTACT_LIST[username]["Discount_Number"],
                        disc=str(float(ACTIVE_CONTACT_LIST[username]["Discount"].replace(',','.'))*100))
                    data['REF_CODE_UE'] = ACTIVE_CONTACT_LIST[username]["Discount_Number"]
                else:
                    data['DISCOUNT_UE'] = ACTIVE_CONTACT_LIST[username]["Discount"]
                    disc_status_mess = _('Код <b><em>{REF_CODE_UE}</em></b> не найден в базе данных.\n' \
                                        'Для формирования итоговой заявки мы использовали Ваш дисконтный код <b>{disc_code}</b>,' \
                                        ' предоставляющий скидку <b>{disc}%.</b>\n\n' \
                                        '<em>После совершения операции Вам также будут начислены дополнительные баллы, которые влияют на размер итоговой скидки!\n\n' \
                                        'Для получения подробной информации о бонусной программе воспользуйтесь командой /refferal</em>').format(
                        REF_CODE_UE=data['REF_CODE_UE'],
                        disc_code=ACTIVE_CONTACT_LIST[username]["Discount_Number"],
                        disc=str(float(ACTIVE_CONTACT_LIST[username]["Discount"].replace(',','.'))*100))
                    data['REF_CODE_UE'] = ACTIVE_CONTACT_LIST[username]["Discount_Number"]
                if data.get('OPER_NAME_RE') in ['Обмен USDT на ЕВРО', 'Обмен USDT на РУБЛИ', 'Обмен USDT на ГРИВНЫ', 'Обмен USDT на ТЕНГЕ']:
                    discount = 1 + float(data['DISCOUNT_UE'].replace(',', '.')) / 100
                else:
                    discount = 1 - float(data['DISCOUNT_UE'].replace(',', '.')) / 100
                data['USDT_EURO_RATE'] = round(data['USDT_EURO_RATE'] * discount, 4)
                data['SUM_USDT_UE'] = math.ceil(data['SUM_EUR_UE'] / data['USDT_EURO_RATE'])
                if data.get('BLOCKCHAIN') == 'Tronchain' and data['RISK_TRC'] == 'Обнаружены подозрительные транзакции':
                    data['SUM_USDT_UE'] +=5 
                elif data.get('BLOCKCHAIN') == 'Etherium':
                    data['SUM_USDT_UE'] +=10 
                if data.get('OPER_NAME_UE')==_('Обмен USDT на ЕВРО'):
                    currency = 'евро' 
                    currency1 = 'EUR' 
                elif data.get('OPER_NAME_UE')==_('Обмен USDT на ГРИВНЫ'):
                    currency = 'гривнах'
                    currency1 = 'UAH'
                elif data.get('OPER_NAME_UE')==_('Обмен USDT на ТЕНГЕ'):
                    currency = 'тенге'
                    currency1 = 'KZT' 
                else:
                    currency = 'рублях'
                    currency1 = 'RUB'
                city_or_bank = _('Банк получателя') if data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ') or data.get('OPER_NAME_UE') == _('Обмен USDT на ГРИВНЫ') or data.get('OPER_NAME_UE') == _('Обмен USDT на ТЕНГЕ') else _('Город сделки')
                if data.get('CASH_FLAG'):
                    client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                        '<em>Валютная операция:</em> {OPER_NAME_UE}\n' \
                                        '<em>Предлагаемый курс (USDT/{currency1}):</em> {USDT_EURO_RATE}\n' \
                                        '<em>Сумма получения в {currency}:</em> {SUM_EUR_UE}\n' \
                                        '<em>Сумма перевода в USDT:</em> {SUM_USDT_UE}\n' \
                                        '<em>{city_or_bank}:</em> {CITY_UE}\n' \
                                        '<em>Город получения наличных:</em> {CASH_CITY}\n' \
                                        '<em>Время сделки:</em> {ORDER_TIME_UE}\n\n' \
                                        '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(OPER_NAME_UE=data.get('OPER_NAME_UE'),
                                                                                                        USDT_EURO_RATE=data['USDT_EURO_RATE'],
                                                                                                        SUM_EUR_UE=data['SUM_EUR_UE'],
                                                                                                        SUM_USDT_UE=data['SUM_USDT_UE'],
                                                                                                        CITY_UE=data['CITY_UE'],
                                                                                                        ORDER_TIME_UE=data['ORDER_TIME_UE'],
                                                                                                        currency=currency,
                                                                                                        CASH_CITY=data['CASH_CITY'],
                                                                                                        city_or_bank=city_or_bank,
                                                                                                        currency1=currency1)
                else:
                    client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                        '<em>Валютная операция:</em> {OPER_NAME_UE}\n' \
                                        '<em>Предлагаемый курс (USDT/{currency1}):</em> {USDT_EURO_RATE}\n' \
                                        '<em>Сумма получения в {currency}:</em> {SUM_EUR_UE}\n' \
                                        '<em>Сумма перевода в USDT:</em> {SUM_USDT_UE}\n' \
                                        '<em>{city_or_bank}:</em> {CITY_UE}\n\n' \
                                        '<em>Время сделки:</em> {ORDER_TIME_UE}\n' \
                                        '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(OPER_NAME_UE=data.get('OPER_NAME_UE'),
                                                                                                        USDT_EURO_RATE=data['USDT_EURO_RATE'],
                                                                                                        SUM_EUR_UE=data['SUM_EUR_UE'],
                                                                                                        SUM_USDT_UE=data['SUM_USDT_UE'],
                                                                                                        CITY_UE=data['CITY_UE'],
                                                                                                        ORDER_TIME_UE=data['ORDER_TIME_UE'],
                                                                                                        currency=currency,
                                                                                                        city_or_bank=city_or_bank,
                                                                                                       currency1=currency1)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                b1 = types.KeyboardButton(_('Да'))
                b2 = types.KeyboardButton(_('Нет'))
                markup.add(b1, b2)
                client_warning_mess = _(
                    '<b>Регистрируя заявку, Вы подтверждаете, что ознакомились с документами, регулирующими правила совершения операций' \
                    ' по обмену валют в разделе <em>/documents</em></b>\n\n')
                bot.send_message(message.chat.id, disc_status_mess, parse_mode='html', reply_markup=a)
                bot.send_message(message.chat.id, client_order_mess, parse_mode='html', reply_markup=a)
                bot.send_message(message.chat.id, client_warning_mess, parse_mode='html', reply_markup=markup)
            # 2.1.8.3 Если поиск контакта 
            elif message.text == _('Поиск контакта') and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_USDT_EURO')) and (
                    not data.get('OPER_FLAG_EUR_RUB')) \
                    and (data.get('CITY_UE_FLAG')) and (data.get('SUM_USDT_FLAG')) and (data.get('ORDER_TIME_FLAG_UE')) and (data.get('FRIEND_REF_FLAG_UE')) and (
                    not data.get('ORDER_CONFIRM_UE_FLAG')):
                data['FIND_USER_FLAG'] = True
                mess = _('Введите никнейм пользователя с учетом регистра, начиная с "@"')
                markup = types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            elif data.get('FIND_USER_FLAG') and message.text in ACTIVE_CONTACT_LIST and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_USDT_EURO')) and (
                    not data.get('OPER_FLAG_EUR_RUB')) \
                    and (data.get('CITY_UE_FLAG')) and (data.get('SUM_USDT_FLAG')) and (data.get('ORDER_TIME_FLAG_UE')) and (data.get('FRIEND_REF_FLAG_UE')) and (
                    not data.get('ORDER_CONFIRM_UE_FLAG')):
                data['RES_ORDER_FLAG_UE'] = True
                data['ORDER_CONFIRM_UE_FLAG'] = True
                add_username = message.text
                disc_code = ACTIVE_CONTACT_LIST[message.text]["Discount_Number"]
                disc_status_mess = _('Пользователь найден.\n' \
                                    'Дополнительные баллы будут начислены пользователю <b><em>{user_nick} (дисконтный код: {disc_code})\n\n' \
                                    'Для получения подробной информации о реферальной программе воспользуйтесь командой /refferal</em></b>').format(
                    user_nick=message.text,
                    disc_code=disc_code)
                if data.get('OPER_NAME_UE')==_('Обмен USDT на ЕВРО'):
                    currency = 'евро' 
                    currency1 = 'EUR' 
                elif data.get('OPER_NAME_UE')==_('Обмен USDT на ГРИВНЫ'):
                    currency = 'гривнах'
                    currency1 = 'UAH' 
                elif data.get('OPER_NAME_UE')==_('Обмен USDT на ТЕНГЕ'):
                    currency = 'тенге'
                    currency1 = 'KZT' 
                else:
                    currency = 'рублях'
                    currency1 = 'RUB'
                city_or_bank = _('Банк получателя') if data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ') or data.get('OPER_NAME_UE') == _('Обмен USDT на ГРИВНЫ') or data.get('OPER_NAME_UE') == _('Обмен USDT на ТЕНГЕ') else _('Город сделки')
                if data.get('CASH_FLAG'):
                    client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                        '<em>Валютная операция:</em> {OPER_NAME_UE}\n' \
                                        '<em>Предлагаемый курс (USDT/{currency1}):</em> {USDT_EURO_RATE}\n' \
                                        '<em>Сумма получения в {currency}:</em> {SUM_EUR_UE}\n' \
                                        '<em>Сумма перевода в USDT:</em> {SUM_USDT_UE}\n' \
                                        '<em>{city_or_bank}:</em> {CITY_UE}\n' \
                                        '<em>Город получения наличных:</em> {CASH_CITY}\n' \
                                        '<em>Время сделки:</em> {ORDER_TIME_UE}\n\n' \
                                        '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(OPER_NAME_UE=data.get('OPER_NAME_UE'),
                                                                                                        USDT_EURO_RATE=data['USDT_EURO_RATE'],
                                                                                                        SUM_EUR_UE=data['SUM_EUR_UE'],
                                                                                                        SUM_USDT_UE=data['SUM_USDT_UE'],
                                                                                                        CITY_UE=data['CITY_UE'],
                                                                                                        ORDER_TIME_UE=data['ORDER_TIME_UE'],
                                                                                                        currency=currency,
                                                                                                        CASH_CITY=data['CASH_CITY'],
                                                                                                        city_or_bank=city_or_bank,
                                                                                                        currency1=currency1)
                else:
                    client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                        '<em>Валютная операция:</em> {OPER_NAME_UE}\n' \
                                        '<em>Предлагаемый курс (USDT/{currency1}):</em> {USDT_EURO_RATE}\n' \
                                        '<em>Сумма получения в {currency}:</em> {SUM_EUR_UE}\n' \
                                        '<em>Сумма перевода в USDT:</em> {SUM_USDT_UE}\n' \
                                        '<em>{city_or_bank}:</em> {CITY_UE}\n\n' \
                                        '<em>Время сделки:</em> {ORDER_TIME_UE}\n' \
                                        '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(OPER_NAME_UE=data.get('OPER_NAME_UE'),
                                                                                                        USDT_EURO_RATE=data['USDT_EURO_RATE'],
                                                                                                        SUM_EUR_UE=data['SUM_EUR_UE'],
                                                                                                        SUM_USDT_UE=data['SUM_USDT_UE'],
                                                                                                        CITY_UE=data['CITY_UE'],
                                                                                                        ORDER_TIME_UE=data['ORDER_TIME_UE'],
                                                                                                        currency=currency,
                                                                                                        city_or_bank=city_or_bank,
                                                                                                        currency1=currency1)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                b1 = types.KeyboardButton(_('Да'))
                b2 = types.KeyboardButton(_('Нет'))
                markup.add(b1, b2)
                client_warning_mess = _(
                    '<b>Регистрируя заявку, Вы подтверждаете, что ознакомились с документами, регулирующими правила совершения операций' \
                    ' по обмену валют в разделе <em>/documents</em></b>\n\n')
                bot.send_message(message.chat.id, disc_status_mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(message.chat.id, client_order_mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(message.chat.id, client_warning_mess, parse_mode='html', reply_markup=markup)
            elif data.get('FIND_USER_FLAG') and message.text not in ACTIVE_CONTACT_LIST and (data.get('FORM_ORDER_FLAG')) and (data.get('OPER_FLAG_USDT_EURO')) and (
                    not data.get('OPER_FLAG_EUR_RUB')) \
                    and (data.get('CITY_UE_FLAG')) and (data.get('SUM_USDT_FLAG')) and (data.get('ORDER_TIME_FLAG_UE')) and (data.get('FRIEND_REF_FLAG_UE')) and (
                    not data.get('ORDER_CONFIRM_UE_FLAG')):
                if not data.get('NAME_FLAG'):
                    data['NAME_FLAG'] = True
                    add_username = message.text
                    mess = _('Пользователь не найден. Введите его имя, чтобы добавить клиента в контакты.')
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                elif data.get('NAME_FLAG'):
                    data['NAME_FLAG'] = False
                    data['RES_ORDER_FLAG_UE'] = True
                    data['ORDER_CONFIRM_UE_FLAG'] = True
                    username = '@' + message.chat.username if message.chat.username is not None else 'None'
                    existed_disc_codes = [one_doc['Discount_Number'] for one_doc in ACTIVE_CONTACT_LIST.values()]
                    existed_ref_codes = [one_doc['Referral_Number'] for one_doc in ACTIVE_CONTACT_LIST.values() if 'Referral_Number' in one_doc]
                    while True:
                        s = string.ascii_lowercase + string.ascii_uppercase + string.digits
                        disc_code = ''.join(random.sample(s, 4))
                        if disc_code not in existed_disc_codes:
                            break
                    while True:
                        ref_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                        if ref_code not in existed_ref_codes:
                            break
                    write_contact(TG_Contact=add_username, user_ID='', NameSurname=message.text, AccTypeFROM='', CurrFROM='USDT', 
                                  City=data['CITY_UE'], ContactType='Клиент', ContactDealer=username, CurrStatus='Активный',
                                  Discount_Number=disc_code, Referral_Number=ref_code)
                    disc_status_mess = _('Пользователь добавлен.\n' \
                                    'Дополнительные баллы будут начислены пользователю <b><em>{add_username}</em></b> (дисконтный код: {disc_code})').format(
                                                                                                                                            add_username=add_username,
                                                                                                                                            disc_code=disc_code)
                    if data.get('OPER_NAME_UE')==_('Обмен USDT на ЕВРО'):
                        currency = 'евро' 
                        currency1 = 'EUR' 
                    elif data.get('OPER_NAME_UE')==_('Обмен USDT на ГРИВНЫ'):
                        currency = 'гривнах'
                        currency1 = 'UAH' 
                    elif data.get('OPER_NAME_UE')==_('Обмен USDT на ТЕНГЕ'):
                        currency = 'тенге'
                        currency1 = 'KZT' 
                    else:
                        currency = 'рублях'
                        currency1 = 'RUB'
                    city_or_bank = _('Банк получателя') if data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ') or data.get('OPER_NAME_UE') == _('Обмен USDT на ГРИВНЫ') or data.get('OPER_NAME_UE') == _('Обмен USDT на ТЕНГЕ') else _('Город сделки')
                    if data.get('CASH_FLAG'):
                        client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                            '<em>Валютная операция:</em> {OPER_NAME_UE}\n' \
                                            '<em>Предлагаемый курс (USDT/{currency1}):</em> {USDT_EURO_RATE}\n' \
                                            '<em>Сумма получения в {currency}:</em> {SUM_EUR_UE}\n' \
                                            '<em>Сумма перевода в USDT:</em> {SUM_USDT_UE}\n' \
                                            '<em>{city_or_bank}:</em> {CITY_UE}\n' \
                                            '<em>Город получения наличных:</em> {CASH_CITY}\n' \
                                            '<em>Время сделки:</em> {ORDER_TIME_UE}\n\n' \
                                            '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(OPER_NAME_UE=data.get('OPER_NAME_UE'),
                                                                                                            USDT_EURO_RATE=data['USDT_EURO_RATE'],
                                                                                                            SUM_EUR_UE=data['SUM_EUR_UE'],
                                                                                                            SUM_USDT_UE=data['SUM_USDT_UE'],
                                                                                                            CITY_UE=data['CITY_UE'],
                                                                                                            ORDER_TIME_UE=data['ORDER_TIME_UE'],
                                                                                                            currency=currency,
                                                                                                            CASH_CITY=data['CASH_CITY'],
                                                                                                            city_or_bank=city_or_bank,
                                                                                                            currency1=currency1 )
                    else:
                        client_order_mess = _('<b>Итоговая заявка с учетом скидки:</b>\n' \
                                            '<em>Валютная операция:</em> {OPER_NAME_UE}\n' \
                                            '<em>Предлагаемый курс (USDT/{currency1}):</em> {USDT_EURO_RATE}\n' \
                                            '<em>Сумма получения в {currency}:</em> {SUM_EUR_UE}\n' \
                                            '<em>Сумма перевода в USDT:</em> {SUM_USDT_UE}\n' \
                                            '<em>{city_or_bank}:</em> {CITY_UE}\n\n' \
                                            '<em>Время сделки:</em> {ORDER_TIME_UE}\n' \
                                            '<b>Вы подтверждаете заявку?</b>\n<em>(Да/Нет)</em>\n').format(OPER_NAME_UE=data.get('OPER_NAME_UE'),
                                                                                                            USDT_EURO_RATE=data['USDT_EURO_RATE'],
                                                                                                            SUM_EUR_UE=data['SUM_EUR_UE'],
                                                                                                            SUM_USDT_UE=data['SUM_USDT_UE'],
                                                                                                            CITY_UE=data['CITY_UE'],
                                                                                                            ORDER_TIME_UE=data['ORDER_TIME_UE'],
                                                                                                            currency=currency,
                                                                                                            city_or_bank=city_or_bank,
                                                                                                            currency1=currency1)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    b1 = types.KeyboardButton(_('Да'))
                    b2 = types.KeyboardButton(_('Нет'))
                    markup.add(b1, b2)
                    client_warning_mess = _(
                        '<b>Регистрируя заявку, Вы подтверждаете, что ознакомились с документами, регулирующими правила совершения операций' \
                        ' по обмену валют в разделе <em>/documents</em></b>\n\n')
                    bot.send_message(message.chat.id, disc_status_mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                    bot.send_message(message.chat.id, client_order_mess, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                    bot.send_message(message.chat.id, client_warning_mess, parse_mode='html', reply_markup=markup)
            # 2.2.5
            elif message.text == _('Да') and data.get('FORM_ORDER_FLAG') and (not data.get('OPER_FLAG_EUR_RUB')) and (data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('SUM_USDT_FLAG') and data.get('CITY_UE_FLAG') and data.get('ORDER_CONFIRM_UE_FLAG'):
                #ACTIVE_CONTACT_LIST = scrab_contact_list()
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                a = types.ReplyKeyboardRemove()
                if add_username == '':
                    from_id = message.from_user.id
                    first_name = message.from_user.first_name
                    username = '@' + message.chat.username if message.chat.username is not None else '-'
                else:
                    if 'user_ID' in ACTIVE_CONTACT_LIST[add_username].keys():
                        from_id = ACTIVE_CONTACT_LIST[add_username]['user_ID']
                    else:
                        from_id = 'Нет информации'
                    first_name = ACTIVE_CONTACT_LIST[add_username]['NameSurname']
                    username = add_username
                    data['REF_CODE_UE'] = ACTIVE_CONTACT_LIST[username]['Discount_Number']
                dealer = ACTIVE_CONTACT_LIST[username]['ContactDealer']
                client_mess = _('Ваша заявка передана оператору. В ближайшее время с Вами свяжется наш сотрудник {ContactDealer}.').format(
                    ContactDealer=dealer
                )
                date = datetime.now(tz).strftime('%d.%m.%Y')
                with open('C:/Users/admin/PycharmProjects/BotMain_v4_Monex/app/deals_ids.json', 'r', encoding='utf8') as f:
                    DealID_num = json.load(f)
                    DealID_num["EX"] += 0.0000001
                    DealID = "EX" + (str(format(DealID_num["EX"], '.7f'))).replace('.','')
                with open('C:/Users/admin/PycharmProjects/BotMain_v4_Monex/app/deals_ids.json', 'w', encoding='utf8') as f:
                    json.dump(DealID_num, f, ensure_ascii=False, indent=2)
                # date = datetime.utcfromtimestamp(message.json['date']).strftime('%Y-%m-%d %H:%M:%S')
                # TODO: НЕ ПЕРЕВОДИТЬ?
                if data.get('OPER_NAME_UE')==_('Обмен USDT на ЕВРО'):
                    currency = 'евро' 
                    currency1 = 'EUR' 
                elif data.get('OPER_NAME_UE')==_('Обмен USDT на ГРИВНЫ'):
                    currency = 'гривнах'
                    currency1 = 'UAH' 
                elif data.get('OPER_NAME_UE')==_('Обмен USDT на ТЕНГЕ'):
                    currency = 'тенге'
                    currency1 = 'KZT' 
                else:
                    currency = 'рублях'
                    currency1 = 'RUB'
                city_or_bank = _('Банк получателя') if data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ') or data.get('OPER_NAME_UE') == _('Обмен USDT на ГРИВНЫ') or data.get('OPER_NAME_UE') == _('Обмен USDT на ТЕНГЕ') else _('Город сделки')
                data['CASH_CITY'] = data['CASH_CITY'] if data.get('CASH_FLAG') else ''
                operator_mess = '<em>Источник:</em> Alpha_TG_Bot\n' \
                                f'<em>Номер ордера:</em> {DealID}\n' \
                                f'<em>{city_or_bank}:</em> <b>#{data["CITY_UE"]}</b>\n' \
                                f'<em>Клиент получит в {currency}:</em> <b>{data["SUM_EUR_UE"]}</b>\n' \
                                f'<em>Блокчейн:</em> <b>{data["BLOCKCHAIN"]}</b>\n' \
                                f'<em>Адрес кошелька:</em> {data["ADDRESS"]}\n' \
                                f'<em>Статус кошелька:</em> {data["RISK_TRC"]}\n' \
                                f'<em>Имя клиента:</em> {first_name}\n' \
                                f'<em>ID клиента:</em> {from_id}\n' \
                                f'<em>Код реферальной программы:</em> {data["REF_CODE_UE"]}\n' \
                                f'<em>Ник клиента:</em> {username}\n' \
                                f'<em>Валютная операция:</em> <b>{data.get("OPER_NAME_UE")}</b>\n' \
                                f'<em>Предлагаемый курс (USDT/{currency1}):</em> {data["USDT_EURO_RATE"]}\n' \
                                f'<em>Сумма перевода в USDT:</em> {data["SUM_USDT_UE"]}\n' \
                                f'<em>Город получения наличных:</em> {data["CASH_CITY"]}\n' \
                                f'<em>Время сделки:</em> {data["ORDER_TIME_UE"]}\n' \
                                f'<em>Время формирования заявки:</em> {date}\n' \
                                f'<em>Кто свяжется по обмену:</em> {dealer}'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, client_mess, parse_mode='html', reply_markup=markup)
                bot.send_message(GROUP_CHAT_ID, operator_mess, parse_mode='html', reply_markup=a)
                if data.get('OPER_NAME_UE') ==_('Обмен USDT на ЕВРО') and int(data['SUM_EUR_UE']) < 1000 or data.get('OPER_NAME_UE') ==_('Обмен USDT на РУБЛИ') and int(data['SUM_EUR_UE']) < 100000 or data.get('OPER_NAME_UE') ==_('Обмен USDT на РУБЛИ') and int(data['SUM_EUR_UE']) < 40000:
                    client_mess1 = _('В соответствии с Правилами совершения операций обмена для сумм обмена менее 1000 евро'
                                     ' бесплатная доставка куратором до клиента не осуществляется. Убедительная просьба согласовать'
                                     ' вопрос доставки денег куратором и/или места встречи в личной беседе в ТГ.')
                    bot.send_message(message.chat.id, client_mess1, parse_mode='html', reply_markup=markup)
                dealer = ACTIVE_CONTACT_LIST[username]['ContactDealer']
                if len(data.get('REF_CODE_UE')) != 6:
                    partner = ''
                    partner_flag = False
                else:
                    for tg_nick, values in ACTIVE_CONTACT_LIST.items():
                        if values['Referral_Number'] == data.get('REF_CODE_UE'):
                            partner = tg_nick
                            partner_flag = True
                            break
                usdt_eur_rate = rates_funcs.scrab_usdt_euro_rate(username, 1)
                if data.get('OPER_NAME_UE') == _('Обмен USDT на РУБЛИ'):
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>RUB', 'RUB=>USDT', 'RUB', data['SUM_EUR_UE'], data['CITY_UE'], '', data['USDT_EURO_RATE'], '/',
                            'USDT', 'Наличные', '', username, data['REF_CODE_UE'], '', '', '', '', '', '', '', '', 'План', '', '', '', '', True, usdt_eur_rate, 1/usdt_eur_rate)
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>RUB', 'RUB=>USDT', 'USDT', data['SUM_EUR_UE'], 'Наличные', '', data['USDT_EURO_RATE_GS'], '/',
                            'RUB', data['CITY_UE'], '', '', '', '', '', '', '', '', '', '', '', 'План', '', '', 'rubeur', '', '', '', '')
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>RUB', 'RUB=>USDT', 'USDT', data['SUM_EUR_UE'], 'Наличные', '', data['USDT_EURO_RATE_GS'],
                            '/', 'USDT', 'Наличные', '', '', '', '', 'NEW', '', '', '', '', '',
                            '', 'РасчБонПлан', '', '', 'rubeur3', 'VPR in 3', '', '', '')
                    eur_rate = rates_funcs.scrab_usdt_euro_rate(username, 1)
                    calculate_indexes(deal_type='EU', partner_flag=partner_flag, eur_rate=eur_rate)
                elif data.get('OPER_NAME_UE') == _('Обмен USDT на ГРИВНЫ'):
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>UAH', 'UAH=>USDT', 'UAH', data['SUM_EUR_UE'], 'Наличные', '',
                            data['USDT_EURO_RATE'], '/',
                            'USDT', 'Binance', '', username, data['REF_CODE_UE'], data['CITY_UE'], '', '', '', '', '', '',
                            '', 'План', '', '','', '', True, usdt_eur_rate, 1/usdt_eur_rate)
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>UAH', 'UAH=>USDT', 'USDT', data['SUM_EUR_UE'], 'Наличные', '', data['USDT_EURO_RATE_GS'], '/',
                            'UAH', data['CITY_UE'], '', '', '', '', '', '', '', '', '', '', '', 'План', '', '', 'rubeur', '', '', '', '')
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>UAH', 'UAH=>USDT', 'USDT', data['SUM_EUR_UE'], 'Наличные', '', data['USDT_EURO_RATE_GS'],
                            '/', 'USDT', 'Наличные', '', '', '', '', 'NEW', '', '', '', '', '',
                            '', 'РасчБонПлан', '', '', 'rubeur3', 'VPR in 3', '', '', '')
                    eur_rate = rates_funcs.scrab_usdt_euro_rate(username, 1)
                    calculate_indexes(deal_type='UU', partner_flag=partner_flag, eur_rate=eur_rate)
                elif data.get('OPER_NAME_UE') == _('Обмен USDT на ТЕНГЕ'):
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>KZT', 'KZT=>USDT', 'KZT', data['SUM_EUR_UE'], 'Наличные', '',
                            data['USDT_EURO_RATE'], '/',
                            'USDT', 'Binance', '', username, data['REF_CODE_UE'], data['CITY_UE'], '', '', '', '', '', '',
                            '', 'План', '', '','', '', True, usdt_eur_rate, 1/usdt_eur_rate)
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>KZT', 'KZT=>USDT', 'USDT', data['SUM_EUR_UE'], 'Наличные', '', data['USDT_EURO_RATE_GS'], '/',
                            'KZT', data['CITY_UE'], '', '', '', '', '', '', '', '', '', '', '', 'План', '', '', 'rubeur', '', '', '', '')
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>KZT', 'KZT=>USDT', 'USDT', data['SUM_EUR_UE'], 'Наличные', '', data['USDT_EURO_RATE_GS'],
                            '/', 'USDT', 'Наличные', '', '', '', '', 'NEW', '', '', '', '', '',
                            '', 'РасчБонПлан', '', '', 'rubeur3', 'VPR in 3', '', '', '')
                    eur_rate = rates_funcs.scrab_usdt_euro_rate(username, 1)
                    calculate_indexes(deal_type='UU', partner_flag=partner_flag, eur_rate=eur_rate)
                else:
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>EUR', 'EUR=>USDT', 'EUR', data['SUM_EUR_UE'], 'Наличные', '',
                            data['USDT_EURO_RATE'], '/',
                            'USDT', 'Binance', '', username, data['REF_CODE_UE'], data['CITY_UE'], '', '', '', '', '', '',
                            '', 'План', '', '','', '', True, usdt_eur_rate, 1/usdt_eur_rate)
                    #add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>EUR', 'EUR=>USDT', 'USDT', data['SUM_EUR_UE'], 'Наличные', '', data['USDT_EURO_RATE_GS'], '/',
                    #        'EUR', data['CITY_UE'], '', '', '', '', '', '', '', '', '', '', '', 'План', '', '', 'rubeur', '')
                    add_row(DealID, date, date, 'Alpha_TG_Bot', partner, 'USDT=>EUR', 'EUR=>USDT', 'USDT', data['SUM_EUR_UE'], 'Наличные', '', data['USDT_EURO_RATE_GS'],
                            '/', 'USDT', 'Наличные', '', '', '', '', 'VPR', '', '', '', '', '',
                            '', 'РасчБонПлан', '', '', 'rubeur2', 'VPR in 2', '', '', '')  # добавить Binance, добавить куратора(ов) + оставить только дату
                    eur_rate = rates_funcs.scrab_usdt_euro_rate(username, 1)
                    calculate_indexes(deal_type='UE', partner_flag=partner_flag, eur_rate=eur_rate)
                add_border()
                #update_contact(username=username, city=data['CITY_UE'], acc_type_from=BLOCKCHAIN, curr_from='USDT')
            # 2.2.6
            elif message.text == _('Нет') and data.get('FORM_ORDER_FLAG') and (not data.get('OPER_FLAG_EUR_RUB')) and (data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('SUM_USDT_FLAG') and data.get('CITY_UE_FLAG') and data.get('ORDER_CONFIRM_UE_FLAG'):
                data['PENDING_ORDER_FLAG'] = True
                a = types.ReplyKeyboardRemove()
                mess = _('<b>Вы можете создать отложенный ордер!</b>\n' \
                        'Укажите свой курс и, как только стоимость актива совпадет с указанной, мы отправим Вам уведомление!')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                b1 = types.KeyboardButton(_('Создать отложенный ордер'))
                b2 = types.KeyboardButton(_('Главное меню'))
                markup.add(b1, b2)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
            # Отложенный ордер (отказ)
            elif message.text == _('Главное меню') and data.get('FORM_ORDER_FLAG') and (not data.get('OPER_FLAG_EUR_RUB')) and (data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('SUM_USDT_FLAG') and data.get('CITY_UE_FLAG') and data.get('ORDER_CONFIRM_UE_FLAG') and data.get('PENDING_ORDER_FLAG'):
                data['PENDING_ORDER_FLAG'] = False
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, text=_('Выберите доступную команду из меню'), parse_mode='html',
                                reply_markup=markup)
            # Отложенный ордер
            elif message.text == _('Создать отложенный ордер') and data.get('FORM_ORDER_FLAG') and (not data.get('OPER_FLAG_EUR_RUB')) and (
                    data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('SUM_USDT_FLAG') and data.get('CITY_UE_FLAG') and data.get('ORDER_CONFIRM_UE_FLAG') and data.get('PENDING_ORDER_FLAG'):
                a = types.ReplyKeyboardRemove()
                mess = _('Введите, пожалуйста, желаемый курс сделки.')
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=a)
            # Ввод желаемого курса
            # Неверный формат
            elif not message.text.replace(".", "").replace(",", "").isnumeric() and data.get('FORM_ORDER_FLAG') and (
                    not data.get('OPER_FLAG_EUR_RUB')) and (data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('SUM_USDT_FLAG') and data.get('CITY_UE_FLAG') and data.get('ORDER_CONFIRM_UE_FLAG') and data.get('PENDING_ORDER_FLAG'):
                a = types.ReplyKeyboardRemove()
                mess = _(
                    'Вы ввели некорректную сумму.\nДля формирования заявки просим повторно ввести курс, учитывая ограничения:\n' \
                    '<b><em>Вводимое значение должно быть числом, убедитесь в отсутствии букв в тексте сообщения</em></b>.\n' \
                    '<em>Если ввели/выбрали неверное значение на одном из этапов формирования заявки, перезапустите команду: /form_order</em>')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=a)
            # Курс введен
            elif message.text.replace(".", "").replace(",", "").isnumeric() and data.get('FORM_ORDER_FLAG') and (
                    not data.get('OPER_FLAG_EUR_RUB')) and (data.get('OPER_FLAG_USDT_EURO')) \
                    and data.get('SUM_USDT_FLAG') and data.get('CITY_UE_FLAG') and data.get('ORDER_CONFIRM_UE_FLAG') and data.get('PENDING_ORDER_FLAG'):
                data['PENDING_ORDER_FLAG'] = False
                a = types.ReplyKeyboardRemove()
                client_mess = _('Ваш ордер создан. Мы уведомим Вас, как только курс достигнет указанного значения!')
                from_id = message.from_user.id
                first_name = message.from_user.first_name
                username = '@' + message.chat.username if message.chat.username is not None else '-'
                date = datetime.now(tz).strftime('%d.%m.%Y')
                # date = datetime.utcfromtimestamp(message.json['date']).strftime('%Y-%m-%d %H:%M:%S')
                with open('contacts.json', 'r', encoding='utf8') as f:
                    ACTIVE_CONTACT_LIST = json.load(f)
                dealer = ACTIVE_CONTACT_LIST[username]['ContactDealer']
                deal_type = 'USDT=>RUB' if data.get('OPER_NAME_UE') ==_('Обмен USDT на РУБЛИ') else 'USDT=>EUR'
                write_pending_order(createDateTime=date, dealer=dealer, dealType=deal_type, exchFROM_Amount=data['SUM_EUR_UE'],
                                    orderRate=message.text.replace(".", ","), user_ID=message.from_user.id,
                                    tg_Contact=username, city=data['CITY_UE'], currStatus='Создан', chat_ID=message.chat.id, )
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                markup.add(*menu_buttons)
                bot.send_message(message.chat.id, client_mess, parse_mode='html', reply_markup=markup)
            # else:
            #    a = types.ReplyKeyboardRemove()
            #    mess = 'Не удалось распознать команду. Воспользуйтесь меню для быстрого поиска команд или введите /help для получения полного перечня команд с подробным описанием.'
            #    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            #    menu_buttons = form_menu_buttons(MAIN_MENU_BUTTONS)
            #    markup.add(*menu_buttons)
            #    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
    def form_menu_buttons(MAIN_MENU_BUTTONS):
        button_list = []
        for button in MAIN_MENU_BUTTONS:
            b = types.KeyboardButton(button)
            button_list.append(b)
        return button_list
    def form_order_city_buttons(CITY_BUTTONS):
        '''
        Создание кнопок для выбора города сделки
        '''
        return [types.KeyboardButton(button) for button in CITY_BUTTONS]
    # Запуск бота на постояное выполнение
    # bot.polling(none_stop=True)
    # bot.infinity_polling(True)
    #except Exception as e:
        #print('Exception: ' + str(e))
        #os.system('python main copy.py')
    # Проверка отложенных ордеров (каждые 15 минут)
    def check_pending_orders(bot):
        def run_func():
            CREDENTIALS_FILE = r'files/cryptoproject-376121-0ee14403b31d.json'  # Имя файла с закрытым ключом, вы должны подставить свое
            # Читаем ключи из файла
            credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                        ['https://www.googleapis.com/auth/spreadsheets',
                                                                            'https://www.googleapis.com/auth/drive'])
            httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
            service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
            sheet_id = '1156rEolgYH-TmuXgR-yAI-URbme_ZkZyzyz9w_fcWFU'
            resp = service.spreadsheets().values().get(spreadsheetId=sheet_id,
                                                    range="Отложенные ордеры!C2:1000000").execute()
            rows = resp['values']
            headers = rows.pop(0)
            pending_orders = [dict(zip(headers, one_row)) for one_row in rows]
            currency_rate = rates_funcs.get_rates_data('username', '')
            currency_rate_buy = rates_funcs.get_rates_buy_eur_data(currency_from='EUR_RUB', bank_name='', username='username')
            usdt_eur_rate = rates_funcs.compute_usdt_euro_amount(1, 'username')
            usdt_rub_rate = rates_funcs.compute_usdt_rub_amount(1, 'username', False, '')
            for row_index, order in enumerate(pending_orders):
                if order['CurrStatus'] == 'Создан' and (order['City'] != 'Херцег Нови' and (
                        order['DealType'] == 'EUR=>RUB' and (
                        float(order['ExchFROM_Amount']) < 50000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate_buy[49999] or \
                        499 < float(order['ExchFROM_Amount']) < 100000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate_buy[99999] or \
                        999 < float(order['ExchFROM_Amount']) < 300000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate_buy[299999] or \
                        2999 < float(order['ExchFROM_Amount']) < 1000000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate_buy[999999] or \
                        9999 < float(order['ExchFROM_Amount']) and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate_buy[1000001]) or \
                        order['DealType'] == 'RUB=>EUR' and (
                        float(order['ExchFROM_Amount']) < 500 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate[499] or \
                        499 < float(order['ExchFROM_Amount']) < 1000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate[999] or \
                        999 < float(order['ExchFROM_Amount']) < 3000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate[2999] or \
                        2999 < float(order['ExchFROM_Amount']) < 10000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate[9999] or \
                        9999 < float(order['ExchFROM_Amount']) and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate[10001]) or \
                        order['DealType'] == 'RUB=>KZT' and (
                        float(order['ExchFROM_Amount']) < 250000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate[249999] or \
                        249999 < float(order['ExchFROM_Amount']) < 500000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate[499999] or \
                        499999 < float(order['ExchFROM_Amount']) < 1500000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate[1499999] or \
                        1499999 < float(order['ExchFROM_Amount']) < 5000000 and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate[4999999] or \
                        4999999 < float(order['ExchFROM_Amount']) and float(order['OrderRate'].replace(',', '.')) >=
                        currency_rate[5000000]) or \
                        order['DealType'] == 'USDT=>EUR' and (
                                float(order['ExchFROM_Amount']) < 5000 and float(order['OrderRate'].replace(',', '.')) <=
                                usdt_eur_rate['low_rate'] or \
                                float(order['ExchFROM_Amount']) > 4999 and float(order['OrderRate'].replace(',', '.')) <=
                                usdt_eur_rate['high_rate'])) or \
                        order['DealType'] == 'USDT=>RUB' and (
                                float(order['ExchFROM_Amount']) < 500000 and float(order['OrderRate'].replace(',', '.')) <=
                                usdt_rub_rate['low_rate'] or \
                                float(order['ExchFROM_Amount']) > 499999 and float(order['OrderRate'].replace(',', '.')) <=
                                usdt_rub_rate['high_rate']) or \
                        order['DealType'] == 'USDT=>UAH' and (
                                float(order['ExchFROM_Amount']) < 200000 and float(order['OrderRate'].replace(',', '.')) <=
                                usdt_rub_rate['low_rate'] or \
                                float(order['ExchFROM_Amount']) > 199999 and float(order['OrderRate'].replace(',', '.')) <=
                                usdt_rub_rate['high_rate']) or \
                        order['DealType'] == 'USDT=>KZT' and (
                                float(order['ExchFROM_Amount']) < 2500000 and float(order['OrderRate'].replace(',', '.')) <=
                                usdt_rub_rate['low_rate'] or \
                                float(order['ExchFROM_Amount']) > 2499999 and float(order['OrderRate'].replace(',', '.')) <=
                                usdt_rub_rate['high_rate']) or \
                                                        order['City'] == 'Херцег Нови' and (
                                                                order['DealType'] == 'RUB=>EUR' and (
                                                                float(order['ExchFROM_Amount']) < 500 and float(
                                                            order['OrderRate'].replace(',', '.')) >= currency_rate[
                                                                    499] + 1 or \
                                                                499 < float(order['ExchFROM_Amount']) < 1000 and float(
                                                            order['OrderRate'].replace(',', '.')) >= currency_rate[
                                                                    999] + 1 or \
                                                                999 < float(order['ExchFROM_Amount']) < 3000 and float(
                                                            order['OrderRate'].replace(',', '.')) >= currency_rate[
                                                                    2999] + 1 or \
                                                                2999 < float(order['ExchFROM_Amount']) < 10000 and float(
                                                            order['OrderRate'].replace(',', '.')) >= currency_rate[
                                                                    9999] + 1 or \
                                                                9999 < float(order['ExchFROM_Amount']) and float(
                                                            order['OrderRate'].replace(',', '.')) >= currency_rate[
                                                                    10001] + 1) or \
                                                                order['DealType'] == 'USDT=>EUR' and (
                                                                        float(order['ExchFROM_Amount']) < 5000 and float(
                                                                    order['OrderRate'].replace(',', '.')) <= usdt_eur_rate[
                                                                            'low_rate'] - 0.005 or \
                                                                        float(order['ExchFROM_Amount']) > 4999 and float(
                                                                    order['OrderRate'].replace(',', '.')) <= usdt_eur_rate[
                                                                            'high_rate'] - 0.005) or \
                                                                order['DealType'] == 'USDT=>EUR' and (
                                                                        float(order['ExchFROM_Amount']) < 500000 and float(
                                                                    order['OrderRate'].replace(',', '.')) <= usdt_rub_rate[
                                                                            'low_rate'] - 0.005 or \
                                                                        float(order['ExchFROM_Amount']) > 499999 and float(
                                                                    order['OrderRate'].replace(',', '.')) <= usdt_rub_rate[
                                                                            'high_rate'] - 0.005))):
                    # TODO: НЕ ПЕРЕВОДИТЬ?
                    mess = '<em>Источник:</em> Alpha_TG_Bot\n' \
                        f'<b>Отложенный ордер от {order["CreateDateTime"]} </b> \n' \
                        f'<em>Тип сделки:</em> {order["DealType"]}\n' \
                        f'<em>Указанный курс:</em> {order["OrderRate"]}\n' \
                        f'<em>Сумма сделки:</em> {order["ExchFROM_Amount"]}\n' \
                        f'<em>Имя пользователя:</em> {order["TG_Contact"]}\n' \
                        f'<em>ID чата:</em> {order["Chat_ID"]}\n'
                    bot.send_message(GROUP_CHAT_ID, text=mess, parse_mode='html')
                    # TODO: Изменить message.from_user.id
                    _ = get_user_translator(order['user_ID'])
                    client_mess = _('<b>Отложенный ордер от {CreateDateTime} </b> \n' \
                                    '<em>Тип сделки:</em> {DealType}\n' \
                                    '<em>Указанный курс:</em> {OrderRate}\n' \
                                    '<em>Сумма сделки:</em> {amount}\n\n' \
                                    'Для совершения сделки оставьте, пожалуйста, заявку в пункте меню:\n <em>🔁 Обмен по заявке. /form_order</em>').format(
                        CreateDateTime=order["CreateDateTime"],
                        DealType=order["DealType"],
                        OrderRate=order["OrderRate"],
                        amount=order["ExchFROM_Amount"])
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    menu_buttons = form_menu_buttons(_(MAIN_MENU_BUTTONS))
                    markup.add(*menu_buttons)
                    bot.send_message(order["Chat_ID"], client_mess, parse_mode='html', reply_markup=markup)
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": f"Отложенные ордеры!K{row_index + 3}:10000",
                            "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                            "values": [
                                ['Отправлен'],  # Заполняем первую строку
                            ]}
                        ]
                    }).execute()
        return run_func
    def write_usdrub_eurrub():
        rates = rates_funcs.get_fiat_rates_tradingview()
        USD_RUB, EUR_RUB, EUR_USD, EUR_UAH, USD_UAH, USD_KZT, EUR_KZT, RSD_USD, RSD_EUR, USD_EUR = rates['USD_RUB'], rates['EUR_RUB'], rates['EUR_USD'], rates['EUR_UAH'], rates['USD_UAH'], rates['USD_KZT'], rates['EUR_KZT'], rates['RSD_USD'], rates['RSD_EUR'], rates['USD_EUR']
        gs_write_usdrub_eurrub(USD_RUB, USD_UAH, 1/RSD_USD, USD_KZT, EUR_RUB, EUR_UAH, EUR_KZT, 1/RSD_EUR, EUR_USD, USD_EUR)
    my_func1 = write_usdrub_eurrub
    my_func2 = get_last_trans
    my_func3 = scrab_contact_list
    my_func5 = write_update_contacts
    # Запуск функции в новом потоке
    my_func = check_pending_orders(bot)
    scheduler = BackgroundScheduler({'apscheduler.job_defaults.max_instances': 3, 'apscheduler.timezone': 'Europe/Podgorica'})
    #scheduler = BlockingScheduler({'apscheduler.job_defaults.max_instances': 3})
    job1 = scheduler.add_job(my_func1, 'cron', hour=19, minute=58)
    job2 = scheduler.add_job(my_func2, 'interval', days=1)
    job3 = scheduler.add_job(my_func3, 'interval', minutes=3)
    #job5 = scheduler.add_job(my_func5, 'interval', hours=3.1)
    job = scheduler.add_job(my_func, 'interval', hours=12)
    scheduler.start()
    # Запуск бота на постояное выполнение
    bot.polling(none_stop=True)
    bot.infinity_polling(True)
except Exception as e:
    print('Exception: ' + str(e))
    traceback.print_exc()
    os.system(r'python C:\Users\admin\PycharmProjects\BotMain_v5_Alpha\app\main.py')