from aiogram.fsm.state import State, StatesGroup


class AddStoreForm(StatesGroup):
    waiting_first_name = State()
    waiting_last_name = State()
    waiting_city = State()
    waiting_store_name = State()
    waiting_store_phone = State()


class IssuePointsForm(StatesGroup):
    """Выдать баллы — phone number first (existing customers need nothing else,
    their name is looked up), name/surname only asked if the phone is genuinely new."""

    waiting_phone = State()
    choosing_match = State()
    confirming_new = State()
    waiting_new_first_name = State()
    waiting_new_last_name = State()
    composing = State()


class AddClientForm(StatesGroup):
    """Добавить клиента — registers a CustomerCard only, no sale/points."""

    waiting_first_name = State()
    waiting_last_name = State()
    waiting_phone = State()
