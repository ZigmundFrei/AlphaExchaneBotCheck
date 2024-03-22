import collections
import gettext
import threading
from functools import wraps

from gs_write_funcs import get_language

# Количество пользователей, для которых будет кэшироваться значение языка
GET_USER_LANGUAGE_CACHE_SIZE = 50


### Блок для перевода текста
def _(text):
    '''
    Плейсхолдер для функции перевода
    '''
    return text


def inner_cache(func, maxsize = None):
    """
    Декоратор кэширования результатов выполнения функции.
    Есть метод clean(params), который убирает из кэша значение
    соответствующее params
    :param func: функция для декорации
    :param maxsize: Максимальный размер кэша в элементах. При переполнении будет удаляться первый сохраненный
    :return: функция
    """
    params = collections.OrderedDict()
    cache_lock = threading.RLock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs:
            raise AttributeError("Only for args params")

        # Если есть кэшированный элемент, то возвращаем
        with cache_lock:
            if args in params.keys():
                return params[args]

        # Иначе вычисляем значение и сохраняем
        result = func(*args)
        with cache_lock:
            # Если количество элементов равно или больше заданного - убираем самый старый
            if isinstance(maxsize, int) and len(params) >= maxsize:
                params.popitem(last=False)
            params[args] = result
        return result

    # Метод для очистки определенного кэша по аргументам
    def clean(*args, **kwargs):
        if kwargs:
            # Сейчас работает без параметров kwargs
            raise AttributeError("Only for args params")
        with cache_lock:
            if args in params.keys():
                params.pop(args)

    wrapper.clean = clean
    return wrapper


def my_cache(arg1=None, maxsize = None):
    if callable(arg1):
        return inner_cache(arg1, maxsize=maxsize)

    def other_wrapper(func):
        return inner_cache(func, maxsize=maxsize)

    return other_wrapper


def get_user_language(user_id: int) -> str:
    return get_language(user_id)


def get_translator(lang: str = "ru"):
    '''
    Получение переводчика для текстов
    :param lang: язык на который надо переводить
    :return:
    '''

    trans = gettext.translation("messages", localedir="C:/Users/admin/PycharmProjects/BotMain_v5_Alpha/app/translations", languages=(lang,))

    @wraps(trans.gettext)
    def my_gettext(message): 
        '''
        Получение перевода текста или массива в текст/массив нужного языка
        :param message: текст или массив с текстом
        :return:
        '''
        if isinstance(message, (list, set, tuple)):
            return [trans.gettext(item) for item in message]
        return trans.gettext(message)

    return my_gettext


def get_user_translator(user_id: int):
    user_language = get_user_language(user_id)
    return get_translator(user_language)


def construct_translator(maxsize: int = GET_USER_LANGUAGE_CACHE_SIZE):
    '''
    Создает функцию для получения переводчика.
    Прокидывает метод очистки кэша (clean) для функции get_user_language
    :param maxsize: Размер кэша для функции получение языка пользователя
    :return: Функция получения переводчика
    '''
    get_user_language_func = my_cache(get_user_language, maxsize=maxsize)

    @wraps(get_user_translator)
    def inner_get_user_translator(user_id: int):
        user_language = get_user_language_func(user_id)
        return get_translator(user_language)

    inner_get_user_translator.clean = get_user_language_func.clean
    return inner_get_user_translator
