from aiogram.fsm.state import State, StatesGroup

class FlatForm(StatesGroup):
    id_region = State()
    id_region_manual = State()
    object_type = State()
    building_type = State()
    levels = State()
    levels_manual = State()
    level = State()
    rooms = State()
    rooms_manual = State()
    area = State()
    kitchen_area = State()
    announce_month = State()