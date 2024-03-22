from telebot.handler_backends import State, StatesGroup

class RateStates(StatesGroup):
    RATES_FLAG = State()

class MainMenue(StatesGroup):
    main_menue = State()

class FormOrder(StatesGroup):
    FORM_ORDER_FLAG = State()
