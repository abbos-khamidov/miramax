from aiogram.fsm.state import State, StatesGroup


class AddStoreForm(StatesGroup):
    waiting_first_name = State()
    waiting_last_name = State()
    waiting_city = State()
    waiting_store_name = State()


class IssuePointsForm(StatesGroup):
    """Выдать баллы — find/register the customer, then pick the sale amount from
    the tier buttons (composing)."""

    waiting_first_name = State()
    waiting_last_name = State()
    waiting_phone = State()
    choosing_match = State()
    composing = State()


class AddClientForm(StatesGroup):
    """Добавить клиента — registers a CustomerCard only, no sale/points."""

    waiting_first_name = State()
    waiting_last_name = State()
    waiting_phone = State()
