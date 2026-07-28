from aiogram.fsm.state import State, StatesGroup


class AddStoreForm(StatesGroup):
    waiting_first_name = State()
    waiting_last_name = State()
    waiting_city = State()
    waiting_store_name = State()


class AddClientForm(StatesGroup):
    waiting_phone = State()
    waiting_name = State()
    choosing_match = State()
    waiting_amount = State()


class BalanceLookupForm(StatesGroup):
    waiting_query = State()
    choosing_match = State()


class ExchangeForm(StatesGroup):
    waiting_query = State()
    choosing_match = State()
    listing = State()
