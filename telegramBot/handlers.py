from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from datetime import datetime
import asyncio
from collections import defaultdict

from states import FlatForm
from keyboards import (
    main_kb, region_kb, object_kb, building_kb, levels_kb,
    rooms_kb, month_kb, result_kb, back_kb, clear_history_kb
)
from predict import predict_price
from region_names import get_region_name

router = Router()

# Хранилище истории
history = defaultdict(list)

def get_time_features(day: int, month: int, year: int):
    dt = datetime(year, month, day)
    month_val = dt.month
    if month_val in [12, 1, 2]:
        season = 0
    elif month_val in [3, 4, 5]:
        season = 1
    elif month_val in [6, 7, 8]:
        season = 2
    else:
        season = 3
    quarter = (month_val - 1) // 3 + 1
    day_of_week = dt.weekday()
    return month_val, quarter, season, day_of_week

# Главное меню и команды
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "🏠 <b>FlatPriceBot</b>\n\n"
        "Определение стоимости квартиры\n"
        "с помощью машинного обучения\n\n"
        "Выберите действие:"
    )
    await message.answer(text, reply_markup=main_kb, parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "❓ <b>Как пользоваться ботом</b>\n\n"
        "1. Нажмите «🚀 Новый расчет».\n"
        "2. Последовательно отвечайте на вопросы.\n"
        "3. На любом шаге можно нажать «⬅️ Назад».\n"
        "4. После расчёта результат сохраняется в историю.",
        parse_mode="HTML"
    )

@router.message(Command("info"))
async def cmd_info(message: types.Message):
    await message.answer(
        "🧠 <b>Модель: Stacking Ensemble (бустинговый стек)</b>\n\n"
        "Ансамбль из трёх градиентных бустингов:\n"
        "• <b>CatBoost</b> — устойчив к категориальным признакам\n"
        "• <b>XGBoost</b> — классический бустинг с регуляризацией\n"
        "• <b>LightGBM</b> — быстрый и эффективный на больших данных\n\n"
        "Все три модели были предварительно обучены и оптимизированы. "
        "Стек объединяет их через мета-модель <b>Ridge</b>, которая находит "
        "оптимальные веса для каждого алгоритма.\n\n"
        "📊 <b>Ключевые метрики:</b>\n"
        "• MAPE: 22.17% (валидация) / 22.22% (тест)\n"
        "• R²: 0.06 (валидация) / 0.07 (тест)\n\n"
        "⚡️ <b>Скорость:</b>\n"
        "• Обучение: 5.6 минут (за счёт prefit)\n"
        "• Предсказание: 2.4 минуты на 7-8 млн строк",
        parse_mode="HTML"
    )

@router.message(Command("history"))
async def cmd_history(message: types.Message):
    user_id = message.from_user.id
    recs = history.get(user_id, [])
    if not recs:
        await message.answer("📋 У вас пока нет сохранённых расчетов.")
        return
    lines = ["📋 Последние расчеты:"]
    for i, rec in enumerate(recs[-5:], 1):
        lines.append(
            f"\n{i}. {rec['region_name']}\n"
            f"{rec['area']} м², {rec['rooms']} комн.\n"
            f"💰 {rec['price_formatted']} ₽\n"
            "──────────────"
        )
    await message.answer("\n".join(lines), reply_markup=clear_history_kb)

# Обработчики кнопок меню
@router.callback_query(F.data == "show_history")
async def show_history(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    recs = history.get(user_id, [])
    if not recs:
        await callback.message.answer("📋 У вас пока нет сохранённых расчетов.")
    else:
        lines = ["📋 Последние расчеты:"]
        for i, rec in enumerate(recs[-5:], 1):
            lines.append(
                f"\n{i}. {rec['region_name']}\n"
                f"{rec['area']} м², {rec['rooms']} комн.\n"
                f"💰 {rec['price_formatted']} ₽\n"
                "──────────────"
            )
        await callback.message.answer("\n".join(lines), reply_markup=clear_history_kb)
    await callback.answer()

@router.callback_query(F.data == "clear_history")
async def clear_history(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    history[user_id] = []
    await callback.message.answer("🗑 История очищена.")
    await callback.answer()

@router.callback_query(F.data == "about_model")
async def about_model(callback: types.CallbackQuery):
    text = (
        "🧠 <b>Модель: Stacking Ensemble (бустинговый стек)</b>\n\n"
        "Ансамбль из трёх градиентных бустингов:\n"
        "• <b>CatBoost</b> — устойчив к категориальным признакам\n"
        "• <b>XGBoost</b> — классический бустинг с регуляризацией\n"
        "• <b>LightGBM</b> — быстрый и эффективный на больших данных\n\n"
        "Все три модели были предварительно обучены и оптимизированы. "
        "Стек объединяет их через мета-модель <b>Ridge</b>, которая находит "
        "оптимальные веса для каждого алгоритма.\n\n"
        "📊 <b>Ключевые метрики:</b>\n"
        "• MAPE: 22.17% (валидация) / 22.22% (тест)\n"
        "• R²: 0.06 (валидация) / 0.07 (тест)\n\n"
        "⚡️ <b>Скорость:</b>\n"
        "• Обучение: 5.6 минут (за счёт prefit)\n"
        "• Предсказание: 2.4 минуты на 7-8 млн строк"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "about_project")
async def about_project(callback: types.CallbackQuery):
    await callback.message.answer(
        "👨‍💻 <b>О проекте</b>\n\n"
        "Проект выполнен в рамках курса «Машинное обучение».\n"
        "Разработчики:\nКожевников Максим БПМ-243\nПадерин Артемий БПМ-241\nАртемьев Никита БПМ-244\n\n"
        "Бот демонстрирует интеграцию ML-модели в Telegram.",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "help")
async def help_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "❓ <b>Как пользоваться ботом</b>\n\n"
        "1. Нажмите «🚀 Новый расчет».\n"
        "2. Последовательно отвечайте на вопросы.\n"
        "3. На любом шаге можно нажать «⬅️ Назад».\n"
        "4. После расчёта результат сохраняется в историю.",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "close")
async def close_bot(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer("Чат закрыт. Для нового расчета нажмите /start")

# Старт опроса
@router.callback_query(F.data == "start_calc")
async def start_calculation(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(FlatForm.id_region)
    await callback.message.answer(
        "📍 Шаг 1/9: Регион\n\nВыберите из списка или нажмите «Другое» для ручного ввода кода.",
        reply_markup=region_kb
    )
    await callback.answer()

@router.callback_query(F.data == "new_calc")
async def new_calc_callback(callback: types.CallbackQuery, state: FSMContext):
    await start_calculation(callback, state)

# Назад
async def go_back_to_step(state: FSMContext, step: str, message: types.Message):
    await state.set_state(step)
    data = await state.get_data()
    if step == FlatForm.id_region.state:
        await message.answer("📍 Шаг 1/9: Регион", reply_markup=region_kb)
    elif step == FlatForm.object_type.state:
        await message.answer("🏠 Шаг 2/9: Тип объекта", reply_markup=object_kb)
    elif step == FlatForm.building_type.state:
        await message.answer("🏗️ Шаг 3/9: Тип дома", reply_markup=building_kb)
    elif step == FlatForm.levels.state:
        await message.answer("🏙️ Шаг 4/9: Этажность дома", reply_markup=levels_kb)
    elif step == FlatForm.level.state:
        levels = data.get("levels")
        txt = "🏢 Шаг 5/9: На каком этаже квартира?"
        if levels:
            txt += f" (от 1 до {levels})"
        await message.answer(txt, reply_markup=back_kb)
    elif step == FlatForm.rooms.state:
        await message.answer("🛏️ Шаг 6/9: Количество комнат", reply_markup=rooms_kb)
    elif step == FlatForm.area.state:
        await message.answer("📐 Шаг 7/9: Общая площадь (м²)", reply_markup=back_kb)
    elif step == FlatForm.kitchen_area.state:
        await message.answer("🍽️ Шаг 8/9: Площадь кухни (м²)", reply_markup=back_kb)
    elif step == FlatForm.announce_month.state:
        await message.answer("📅 Шаг 9/9: Месяц объявления", reply_markup=month_kb)

@router.callback_query(F.data == "go_back")
async def handle_go_back(callback: types.CallbackQuery, state: FSMContext):
    current = await state.get_state()
    prev_map = {
        FlatForm.id_region_manual.state: FlatForm.id_region.state,
        FlatForm.object_type.state: FlatForm.id_region.state,
        FlatForm.building_type.state: FlatForm.object_type.state,
        FlatForm.levels.state: FlatForm.building_type.state,
        FlatForm.levels_manual.state: FlatForm.building_type.state,
        FlatForm.level.state: FlatForm.levels.state,
        FlatForm.rooms.state: FlatForm.level.state,
        FlatForm.rooms_manual.state: FlatForm.level.state,
        FlatForm.area.state: FlatForm.rooms.state,
        FlatForm.kitchen_area.state: FlatForm.area.state,
        FlatForm.announce_month.state: FlatForm.kitchen_area.state,
    }
    prev = prev_map.get(current)
    if prev:
        await go_back_to_step(state, prev, callback.message)
    await callback.answer()

# Шаг 1: Регион
@router.callback_query(FlatForm.id_region, F.data.startswith("region_"))
async def process_region_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "region_manual":
        await state.set_state(FlatForm.id_region_manual)
        await callback.message.answer("Введите числовой код региона:")
        await callback.answer()
        return
    region_id = int(callback.data.split("_")[1])
    await state.update_data(id_region=region_id)
    region_str = get_region_name(region_id)
    await callback.message.answer(f"✅ Регион: {region_str}")
    await state.set_state(FlatForm.object_type)
    await callback.message.answer("🏠 Шаг 2/9: Тип объекта", reply_markup=object_kb)
    await callback.answer()

@router.message(FlatForm.id_region_manual)
async def process_region_manual(message: types.Message, state: FSMContext):
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("Пожалуйста, введите целое число.")
        return
    region_id = int(message.text.strip())
    await state.update_data(id_region=region_id)
    region_str = get_region_name(region_id)
    await message.answer(f"✅ Регион: {region_str}")
    await state.set_state(FlatForm.object_type)
    await message.answer("🏠 Шаг 2/9: Тип объекта", reply_markup=object_kb)

# Шаг 2: Тип объекта
@router.callback_query(FlatForm.object_type, F.data.startswith("obj_"))
async def process_object_type(callback: types.CallbackQuery, state: FSMContext):
    obj_code = int(callback.data.split("_")[1])
    await state.update_data(object_type=obj_code)
    names = {0: "Вторичка", 2: "Новостройка"}
    choice = names.get(obj_code, str(obj_code))
    await callback.message.answer(f"✅ Объект: {choice}")
    await state.set_state(FlatForm.building_type)
    await callback.message.answer("🏗️ Шаг 3/9: Тип дома", reply_markup=building_kb)
    await callback.answer()

# Шаг 3: Тип дома
@router.callback_query(FlatForm.building_type, F.data.startswith("build_"))
async def process_building_type(callback: types.CallbackQuery, state: FSMContext):
    build_code = int(callback.data.split("_")[1])
    await state.update_data(building_type=build_code)
    names = {0: "Не знаю", 1: "Другое", 2: "Панельный", 3: "Монолитный", 4: "Кирпичный", 5: "Блочный", 6: "Деревянный"}
    choice = names.get(build_code, str(build_code))
    await callback.message.answer(f"✅ Тип дома: {choice}")
    await state.set_state(FlatForm.levels)
    await callback.message.answer("🏙️ Шаг 4/9: Этажность дома", reply_markup=levels_kb)
    await callback.answer()

# Шаг 4: Этажность
@router.callback_query(FlatForm.levels, F.data.startswith("levels_"))
async def process_levels_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "levels_manual":
        await state.set_state(FlatForm.levels_manual)
        await callback.message.answer("Введите точное количество этажей (целое число ≥ 1):")
        await callback.answer()
        return
    levels = int(callback.data.split("_")[1])
    await state.update_data(levels=levels)
    await callback.message.answer(f"✅ Этажность: {levels} этажей")
    await state.set_state(FlatForm.level)
    await callback.message.answer(
        f"🏢 Шаг 5/9: На каком этаже квартира? (от 1 до {levels})",
        reply_markup=back_kb
    )
    await callback.answer()

@router.message(FlatForm.levels_manual)
async def process_levels_manual(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите целое число.")
        return
    levels = int(message.text)
    if levels < 1:
        await message.answer("Количество этажей должно быть ≥ 1.")
        return
    await state.update_data(levels=levels)
    await message.answer(f"✅ Этажность: {levels} этажей")
    await state.set_state(FlatForm.level)
    await message.answer(
        f"🏢 Шаг 5/9: На каком этаже квартира? (от 1 до {levels})",
        reply_markup=back_kb
    )

# Шаг 5: Этаж
@router.message(FlatForm.level)
async def process_level(message: types.Message, state: FSMContext):
    data = await state.get_data()
    levels = data.get("levels")
    if levels is None:
        await message.answer("Сначала укажите этажность дома.")
        return
    if not message.text.isdigit():
        await message.answer("Введите целое число.")
        return
    level = int(message.text)
    if level < 1 or level > levels:
        await message.answer(f"Некорректный этаж. Введите число от 1 до {levels}.")
        return
    await state.update_data(level=level)
    await message.answer(f"✅ Этаж: {level}")
    await state.set_state(FlatForm.rooms)
    await message.answer("🛏️ Шаг 6/9: Количество комнат", reply_markup=rooms_kb)

# Шаг 6: Комнаты
@router.callback_query(FlatForm.rooms, F.data.startswith("room_"))
async def process_rooms_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "room_manual":
        await state.set_state(FlatForm.rooms_manual)
        await callback.message.answer("Введите точное количество комнат (целое число ≥ 1):")
        await callback.answer()
        return
    rooms = int(callback.data.split("_")[1])
    await state.update_data(rooms=rooms)
    await callback.message.answer(f"✅ Комнат: {rooms}")
    await state.set_state(FlatForm.area)
    await callback.message.answer("📐 Шаг 7/9: Общая площадь (м²)", reply_markup=back_kb)
    await callback.answer()

@router.message(FlatForm.rooms_manual)
async def process_rooms_manual(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите целое число.")
        return
    rooms = int(message.text)
    if rooms < 1:
        await message.answer("Количество комнат должно быть ≥ 1.")
        return
    await state.update_data(rooms=rooms)
    await message.answer(f"✅ Комнат: {rooms}")
    await state.set_state(FlatForm.area)
    await message.answer("📐 Шаг 7/9: Общая площадь (м²)", reply_markup=back_kb)

# Шаг 7: Площадь
@router.message(FlatForm.area)
async def process_area(message: types.Message, state: FSMContext):
    try:
        area = float(message.text.replace(",", "."))
        if area <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите положительное число (например 54.5)")
        return
    if area < 5:
        await message.answer("⚠️ Площадь выглядит слишком маленькой. Проверьте данные.")
        return
    if area > 1000:
        await message.answer("⚠️ Площадь выглядит слишком большой. Проверьте данные.")
        return
    await state.update_data(area=area)
    await message.answer(f"✅ Площадь: {area} м²")
    await state.set_state(FlatForm.kitchen_area)
    await message.answer("🍽️ Шаг 8/9: Площадь кухни (м²)", reply_markup=back_kb)

# Шаг 8: Кухня
@router.message(FlatForm.kitchen_area)
async def process_kitchen_area(message: types.Message, state: FSMContext):
    data = await state.get_data()
    total_area = data.get("area")
    if total_area is None:
        await message.answer("Сначала укажите общую площадь.")
        return
    try:
        kitchen = float(message.text.replace(",", "."))
        if kitchen <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите положительное число.")
        return
    if kitchen > total_area:
        await message.answer(f"Площадь кухни не может быть больше общей площади ({total_area} м²).")
        return
    if kitchen < 2:
        await message.answer("⚠️ Площадь кухни выглядит слишком маленькой. Проверьте данные.")
        return
    if kitchen > 200:
        await message.answer("⚠️ Площадь кухни выглядит слишком большой. Проверьте данные.")
        return
    await state.update_data(kitchen_area=kitchen)
    await message.answer(f"✅ Кухня: {kitchen} м²")
    await state.set_state(FlatForm.announce_month)
    await message.answer("📅 Шаг 9/9: Месяц объявления", reply_markup=month_kb)

# Шаг 9: Месяц и финальный расчёт
@router.callback_query(FlatForm.announce_month, F.data.startswith("month_"))
async def process_month_callback(callback: types.CallbackQuery, state: FSMContext):
    month = int(callback.data.split("_")[1])
    await state.update_data(announce_month=month)
    month_names = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    await callback.message.answer(f"✅ Месяц: {month_names[month]}")

    data = await state.get_data()
    await state.clear()

    year = datetime.now().year
    day = 1
    month_val, quarter, season, day_of_week = get_time_features(day, month, year)

    level = data["level"]
    levels = data["levels"]
    floor_ratio = level / levels if levels != 0 else 0

    wait_msg = await callback.message.answer("⏳ Выполняю расчет")
    for dots in [" .", " ..", " ...", " ..", " ."]:
        await wait_msg.edit_text(f"⏳ Выполняю расчет{dots}")
        await asyncio.sleep(0.4)

    try:
        price = predict_price(
            area=data["area"],
            rooms=data["rooms"],
            kitchen_area=data["kitchen_area"],
            levels=levels,
            floor_ratio=floor_ratio,
            building_type=data["building_type"],
            object_type=data["object_type"],
            id_region=data["id_region"],
            month=month_val,
            quarter=quarter,
            season=season,
            day_of_week=day_of_week
        )
        price_per_m2 = price / data["area"] if data["area"] != 0 else 0
        price_formatted = f"≈ {int(price):,}".replace(",", " ")
        per_m2_formatted = f"≈ {int(price_per_m2):,}".replace(",", " ")

        building_names = {
            0: "Не знаю", 1: "Другое", 2: "Панельный",
            3: "Монолитный", 4: "Кирпичный", 5: "Блочный", 6: "Деревянный"
        }
        object_names = {0: "Вторичка", 2: "Новостройка"}
        season_names = {0: "зима", 1: "весна", 2: "лето", 3: "осень"}

        date_str = f"01.{month:02d}.{year}"
        season_word = season_names.get(season, "")

        region_name = get_region_name(data["id_region"])

        params = (
            f"📍 Регион: {region_name}\n"
            f"🏠 Объект: {object_names.get(data['object_type'], data['object_type'])}\n"
            f"🏗️ Тип дома: {building_names.get(data['building_type'], data['building_type'])}\n"
            f"🏙️ Этажность: {levels}\n"
            f"🏢 Этаж: {level}\n"
            f"🛏️ Комнат: {data['rooms']}\n"
            f"📐 Площадь: {data['area']} м²\n"
            f"🍽️ Кухня: {data['kitchen_area']} м²\n"
            f"📅 Дата объявления: {date_str} ({season_word})"
        )

        result_text = (
            "━━━━━━━━━━━━━━━━━━\n"
            "📊 Исходные данные:\n"
            f"{params}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💰 Стоимость квартиры\n"
            f"   {price_formatted} ₽\n"
            f"📐 Цена за 1 м²\n"
            f"   {per_m2_formatted} ₽\n"
            "━━━━━━━━━━━━━━━━━━\n"
        )
        await wait_msg.edit_text(result_text, reply_markup=result_kb)

        # Сохраняем в историю
        user_id = callback.from_user.id
        history[user_id].append({
            "region_name": region_name,
            "area": data["area"],
            "rooms": data["rooms"],
            "price_formatted": price_formatted
        })
        if len(history[user_id]) > 5:
            history[user_id] = history[user_id][-5:]

    except Exception as e:
        await wait_msg.edit_text(
            f"⚠️ Ошибка при расчете: {e}\nПопробуйте снова /start"
        )
    await callback.answer()