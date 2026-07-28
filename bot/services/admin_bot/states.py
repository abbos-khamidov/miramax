from aiogram.fsm.state import State, StatesGroup


class AddUserForm(StatesGroup):
    """Shared flow for Admin / Supplier / Wholesaler — the target role is stashed in
    FSM data (`target`) rather than split into three near-identical StatesGroups."""

    waiting_first_name = State()
    waiting_last_name = State()
    waiting_phone = State()
    waiting_company_name = State()
    waiting_city = State()


class ViewUsersForm(StatesGroup):
    """listing: browsing/search-result buttons for one role (data: kind, entity_map).
    waiting_search_phone: entering a phone query to filter that same role (data: kind)."""

    listing = State()
    waiting_search_phone = State()


class PointsRateForm(StatesGroup):
    waiting_value = State()


class AddProductForm(StatesGroup):
    waiting_photo = State()
    waiting_category = State()
    waiting_name = State()
    waiting_points_cost = State()
