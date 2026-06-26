from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚀 Новый расчет", callback_data="start_calc")],
    [InlineKeyboardButton(text="📋 История", callback_data="show_history")],
    [
        InlineKeyboardButton(text="ℹ️ О модели", callback_data="about_model"),
        InlineKeyboardButton(text="👨‍💻 О проекте", callback_data="about_project")
    ],
    [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
])

back_btn = InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back")
back_kb = InlineKeyboardMarkup(inline_keyboard=[[back_btn]])

# Клавиатура с кнопкой очистки истории
clear_history_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗑 Очистить историю", callback_data="clear_history")]
])

# Шаг 1: регион
region_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Москва (77)", callback_data="region_77"),
     InlineKeyboardButton(text="СПб (78)", callback_data="region_78")],
    [InlineKeyboardButton(text="Московская обл. (50)", callback_data="region_50"),
     InlineKeyboardButton(text="Ленинградская обл. (47)", callback_data="region_47")],
    [InlineKeyboardButton(text="Краснодарский край (23)", callback_data="region_23"),
     InlineKeyboardButton(text="Свердловская обл. (66)", callback_data="region_66")],
    [InlineKeyboardButton(text="Новосибирская обл. (54)", callback_data="region_54"),
     InlineKeyboardButton(text="Татарстан (16)", callback_data="region_16")],
    [InlineKeyboardButton(text="🖊 Другое (ввести код)", callback_data="region_manual")],
    [back_btn]
])

# Шаг 2: тип объекта
object_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏚 Вторичка", callback_data="obj_0"),
     InlineKeyboardButton(text="🏗 Новостройка", callback_data="obj_2")],
    [back_btn]
])

# Шаг 3: тип дома
building_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❓ Не знаю", callback_data="build_0"),
     InlineKeyboardButton(text="🔄 Другое", callback_data="build_1")],
    [InlineKeyboardButton(text="🏢 Панельный", callback_data="build_2"),
     InlineKeyboardButton(text="🏗 Монолитный", callback_data="build_3")],
    [InlineKeyboardButton(text="🧱 Кирпичный", callback_data="build_4"),
     InlineKeyboardButton(text="🧊 Блочный", callback_data="build_5")],
    [InlineKeyboardButton(text="🪵 Деревянный", callback_data="build_6")],
    [back_btn]
])

# Шаг 4: этажность
levels_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="5", callback_data="levels_5"),
     InlineKeyboardButton(text="9", callback_data="levels_9"),
     InlineKeyboardButton(text="12", callback_data="levels_12"),
     InlineKeyboardButton(text="16", callback_data="levels_16")],
    [InlineKeyboardButton(text="20", callback_data="levels_20"),
     InlineKeyboardButton(text="25", callback_data="levels_25"),
     InlineKeyboardButton(text="🖊 Другое", callback_data="levels_manual")],
    [back_btn]
])

# Шаг 6: комнаты
rooms_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1", callback_data="room_1"),
     InlineKeyboardButton(text="2", callback_data="room_2"),
     InlineKeyboardButton(text="3", callback_data="room_3"),
     InlineKeyboardButton(text="4", callback_data="room_4")],
    [InlineKeyboardButton(text="5 и более", callback_data="room_manual")],
    [back_btn]
])

# Шаг 9: месяц
month_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Январь", callback_data="month_1"),
     InlineKeyboardButton(text="Февраль", callback_data="month_2"),
     InlineKeyboardButton(text="Март", callback_data="month_3")],
    [InlineKeyboardButton(text="Апрель", callback_data="month_4"),
     InlineKeyboardButton(text="Май", callback_data="month_5"),
     InlineKeyboardButton(text="Июнь", callback_data="month_6")],
    [InlineKeyboardButton(text="Июль", callback_data="month_7"),
     InlineKeyboardButton(text="Август", callback_data="month_8"),
     InlineKeyboardButton(text="Сентябрь", callback_data="month_9")],
    [InlineKeyboardButton(text="Октябрь", callback_data="month_10"),
     InlineKeyboardButton(text="Ноябрь", callback_data="month_11"),
     InlineKeyboardButton(text="Декабрь", callback_data="month_12")],
    [back_btn]
])

# Результат
result_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔄 Новый расчет", callback_data="new_calc")],
    [InlineKeyboardButton(text="📋 История", callback_data="show_history"),
     InlineKeyboardButton(text="❌ Закрыть", callback_data="close")]
])