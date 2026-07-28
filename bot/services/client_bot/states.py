from aiogram.fsm.state import State, StatesGroup


class SearchProductForm(StatesGroup):
    waiting_query = State()
