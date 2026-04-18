import asyncio
import re

import aiohttp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SAVINGS_BUFFER = {}

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from middlewaresblock_conflict import LOCKED_USERS
from database import create_family

from config import TOKEN
from database import *
import keyboards
from states import *
USER_MODE = {}

bot = Bot(token=TOKEN)
dp = Dispatcher()

from big_categories import CATEGORIES_DB

from middlewaresblock_conflict import BlockConflictMiddleware

dp.message.middleware(BlockConflictMiddleware())
dp.callback_query.middleware(BlockConflictMiddleware())

import time
from middlewaresblock_conflict import USER_INPUT_LOCK



def add_family_shared_column():
    try:
        cur.execute("ALTER TABLE families ADD COLUMN shared_finance INTEGER DEFAULT 1")
    except:
        pass
    conn.commit()

add_family_shared_column()

def resolve_users_for_finance(user_id):
    """
    Работает ТОЛЬКО через shared_finance
    """
    try:
        # 🔥 нет семьи → только пользователь
        family_id = get_family_id(user_id)
        if not family_id:
            return [user_id]

        # 🔥 проверка режима
        if is_shared_finance(user_id):
            users = get_family_members(user_id)
            return users if users else [user_id]

        return [user_id]

    except Exception as e:
        print("resolve_users_for_finance error:", e)
        return [user_id]
        
@dp.callback_query(F.data.startswith("tz_"))
async def set_timezone(c: CallbackQuery, state: FSMContext):
    await c.answer()

    tz = int(c.data.split("_")[1])
    data = await state.get_data()

    # ========================
    # 🔥 СТАРТ (НЕ ТРОГАЕМ)
    # =========================
    if "name" in data:
        await state.update_data(timezone=tz)

        await state.set_state(StartStates.gender)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👤", callback_data="gender_male")],
            [InlineKeyboardButton(text="👩", callback_data="gender_female")]
        ])

        await c.message.edit_text(
            "Выбери пол:",
            reply_markup=kb
        )

    # =========================
    # 🔥 НАСТРОЙКИ (КАК COLOR)
    # =========================
    else:
        cur.execute(
            "UPDATE users SET timezone=? WHERE id=?",
            (tz, c.from_user.id)
        )
        conn.commit()

        await c.answer("Часовой пояс обновлён")

        try:
            await c.message.delete()
        except:
            pass

        await c.message.answer(
            "⚙️ Настройки",
            reply_markup=keyboards.settings_menu()
        )

@dp.callback_query(F.data == "toggle_tips")
async def toggle_tips_handler(c: CallbackQuery):
    current = get_tips(c.from_user.id)
    new_value = 0 if current else 1

    set_tips(c.from_user.id, new_value)

    text = "✅ Подсказки включены" if new_value else "❌ Подсказки выключены"

    await c.answer("Обновлено")

    try:
        await c.message.delete()
    except:
        pass

    await c.bot.send_message(
        chat_id=c.from_user.id,
        text=text,
        reply_markup=keyboards.settings_menu()
    )

class SettingsStates(StatesGroup):
    change_name = State()


@dp.callback_query(F.data == "set_name")
async def change_name(c: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.change_name)
    await c.message.answer("Введи новое имя")


@dp.message(SettingsStates.change_name)
async def set_name_settings(m: Message, state: FSMContext):
    profile = get_user_profile(m.from_user.id)

    gender = None
    if profile and len(profile) > 3:
        gender = profile[3]

    set_user_profile(
        m.from_user.id,
        m.text,
        get_user_color(m.from_user.id),
        gender
    )

    await state.clear()

    # ✅ уведомление
    await m.answer("✅ Имя обновлено")

    # ✅ ПОВЕДЕНИЕ КАК У COLOR
    await m.answer(
        "⚙️ Настройки",
        reply_markup=keyboards.settings_menu()
    )

def normalize_date(text):
    import re
    from datetime import datetime

    nums = re.findall(r"\d+", text)

    if len(nums) < 2:
        return None

    day = int(nums[0])
    month = int(nums[1])

    year = datetime.now().year
    if len(nums) >= 3:
        year = int(nums[2])

    try:
        dt = datetime(year, month, day)
        return dt.strftime("%Y-%m-%d")  # 🔥 ЕДИНЫЙ ФОРМАТ
    except:
        return None


def lock_user_input(user_id):
    USER_INPUT_LOCK[user_id] = time.time()


def unlock_user_input(user_id):
    USER_INPUT_LOCK.pop(user_id, None)

def get_user_color(user_id):
    profile = get_user_profile(user_id)
    if profile:
        return profile[2] or "🟩"
    return "🟩"

from datetime import datetime

def get_morning_progress(user_id):
    from datetime import datetime

    date = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        SELECT step FROM morning_logs
        WHERE user_id=? AND date=? AND status=1
    """, (user_id, date))

    rows = cur.fetchall()

    if not rows:
        return "❌ Сегодня ничего не выполнено"

    done_steps = sorted([r[0] for r in rows])

    text = ""

    for step in range(1, 7):
        if step in done_steps:
            text += f"{step}. ✅\n"
        else:
            text += f"{step}. ⬜\n"

    return text

@dp.callback_query(F.data == "open_savings")
async def open_savings(c: CallbackQuery, state: FSMContext):
    # ❗ ОБЯЗАТЕЛЬНО — иначе может "висеть"
    await c.answer()

    # ❗ СБРАСЫВАЕМ СТЕЙТ (часто из-за него не открывается)
    await state.clear()

    if not is_fin_enabled(c.from_user.id):
        await c.answer("Функция отключена", show_alert=True)
        return

    balance = get_savings_balance(c.from_user.id)

    # ❗ УДАЛЯЕМ СТАРОЕ МЕНЮ (как ты хочешь везде)
    try:
        await c.message.delete()
    except:
        pass

    await c.bot.send_message(
        chat_id=c.from_user.id,
        text=f"🏦 Накопления: {balance:,} ₽",
        reply_markup=keyboards.savings_menu()
    )

# ==========================
# РАСХОД
# ==========================
CATEGORIES = {
    "Еда": ["пятерочка","pyaterochka","магнит","magnit","ашан","auchan","еда","food","kfc","burger"],
    "Транспорт": ["такси","taxi","метро","автобус"],
    "Быт": ["ozon","wb","wildberries"],
    "Развлечения": ["кино","cinema","игра","game"],
    "Кредиты": ["кредит","loan"]
}

# =========================
# ДОХОД
# =========================
INCOME_CATEGORIES = {
    "ЗП": ["зарплата","salary","работа","job","др банк"],
    "Перевод": ["перевод","transfer"],
    "Кэшбэк": ["cashback"],
    "Инвестиции": ["дивиденды","инвестиции"],
}

# =========================
# ОБЩЕЕ
# =========================
def parse_amount(text):
    text = text.replace(",", ".")

    matches = re.findall(r"(\d+[.\d]*)\s?(₽|RUB|rub)", text)
    if matches:
        return int(float(matches[0][0]))

    nums = re.findall(r"\d+[.\d]*", text)
    nums = [float(n) for n in nums if float(n) > 10]

    if not nums:
        return None

    return int(nums[-1])  # БЕРЕМ ПОСЛЕДНЕЕ, а не max


# =========================
# РАСХОД
# =========================

def init_category_db():
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS category_keywords (
                keyword TEXT,
                category TEXT
            )
        """)
        conn.commit()
    except:
        pass


def seed_category_db():
    try:
        cur.execute("SELECT COUNT(*) FROM category_keywords")
        count = cur.fetchone()[0]

        if count > 0:
            return

        cur.executemany(
            "INSERT INTO category_keywords (keyword, category) VALUES (?, ?)",
            CATEGORIES_DB
        )

        conn.commit()

        print(f"🔥 Загружено ключей: {len(CATEGORIES_DB)}")

    except Exception as e:
        print("Ошибка seed:", e)

# =========================
# 🔥 ИНИЦИАЛИЗАЦИЯ БАЗЫ КАТЕГОРИЙ
# =========================
init_category_db()
seed_category_db()


def detect_category(text, user_id):
    import re

    # =========================
    # НОРМАЛИЗАЦИЯ
    # =========================
    text = text.lower().replace("ё", "е")

    replace_map = {
        "0": "o", "3": "e", "4": "a",
        "@": "a", "$": "s"
    }

    for k, v in replace_map.items():
        text = text.replace(k, v)

    # 🔥 сохраняем исходный текст (ВАЖНО для банков)
    raw_text = text

    # убираем цифры (НО оставляем копию raw_text)
    text = re.sub(r"\d+", " ", text)

    trash = [
        "покупка","oplata","pokupka","payment",
        "счет","счета","карты","карта",
        "доступно","balance","visa","mir","maestro",
        "sbp","sbbol"
    ]
    for t in trash:
        text = text.replace(t, "")

    for ch in [".", ",", ":", ";", "(", ")", "*"]:
        text = text.replace(ch, " ")

    words = [w for w in text.split() if len(w) > 2]

    # =========================
    # 1. USER RULES (НЕ ЛОМАЕМ)
    # =========================
    rules = get_rules(user_id)
    for keyword, cat in rules:
        if keyword.lower() in raw_text:
            return cat

    # =========================
    # 2. БД (ГЛАВНОЕ УЛУЧШЕНИЕ)
    # =========================
    try:
        cur.execute("SELECT keyword, category FROM category_keywords")
        rows = cur.fetchall()

        for keyword, category in rows:
            kw = keyword.lower()

            if kw in raw_text:
                return category

            for w in words:
                if len(w) > 4 and (kw[:4] in w or w[:4] in kw):
                    return category
    except:
        pass

    # =========================
    # 3. БАЗА (СИЛЬНО РАСШИРЕНА)
    # =========================
    CATEGORIES = {

        "Еда": [
            # супермаркеты
            "magnit","магнит","mgn","mgnt","magnit mm",
            "pyaterochka","пятерочка","5ka","5ка",
            "perekrestok","перекресток",
            "lenta","лента",
            "auchan","ашан",
            "okey","окей",
            "dixy","дикси",
            "spar","спар",
            "metro","метро",
            "globus","глобус",

            # доставки
            "samokat","самокат",
            "lavka","лавка",
            "yandex food","яндекс еда",
            "delivery","delivery club",

            # фастфуд
            "kfc","кфс",
            "burger king","бургер",
            "mcd","мак","mac",
            "вкусно",
            "шаурма","шаверма",

            # общие слова
            "еда","food","продукты","кафе","ресторан"
        ],

        "Транспорт": [
            "taxi","такси","uber","bolt","yandex go",
            "метро","автобус","bus",
            "бензин","fuel","азс","lukoil","лукойл",
            "газпром","роснефть",
            "парковка","parking",
            "delimobil","каршеринг"
        ],

        "Быт": [
            # маркетплейсы
            "ozon","озон","o3on","oz0n",
            "wildberries","wb","вб",
            "aliexpress","али",
            "market","маркет","megamarket",

            # техника
            "dns","днс",
            "mvideo","мвидео",
            "eldorado","эльдорадо",

            # дом
            "ikea","икеа",
            "leroy","леруа",
            "obi",

            # одежда
            "zara","hm","bershka","uniqlo",

            # общее
            "shop","заказ","товары"
        ],

        "Развлечения": [
            "netflix","ivi","okko",
            "steam","epic","game",
            "ps","xbox",
            "кино","игра",
            "бар","club","алкоголь"
        ],

        "Кредиты": [
            "кредит","loan","ипотека",
            "tinkoff","тинькофф",
            "sber","сбер",
            "альфа","alfabank",
            "втб","vtb"
        ]
    }

    for cat, keywords in CATEGORIES.items():
        for kw in keywords:

            if kw in raw_text:
                return cat

            for w in words:
                if len(w) > 4 and (kw[:4] in w or w[:4] in kw):
                    return cat

    # =========================
    # 4. САМООБУЧЕНИЕ (СОХРАНИЛИ)
    # =========================
    clean = []

    stop_words = ["руб","rub","rur","счет","карта","покупка"]

    for w in words:
        if w in stop_words:
            continue
        if len(w) < 4:
            continue
        clean.append(w)

    if clean:
        keyword = max(clean, key=len)

        if len(keyword) > 5:
            add_rule(user_id, keyword, "Другое")
        

    return "Другое"


# =========================
# ДОХОД
# =========================
def detect_income_category(text):
    text = text.lower()
    for cat, words in INCOME_CATEGORIES.items():
        for w in words:
            if w in text:
                return cat
    return "Другое"


# =========================
# КНОПКИ
# =========================
def confirm_kb(prefix="exp"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"{prefix}_confirm")],
        [InlineKeyboardButton(text="🔄 Изменить категорию", callback_data=f"{prefix}_change")]
    ])

def timezone_kb():
    kb = []
    row = []

    for i in range(-12, 13):
        if i == 0:
            text = "🕒 МСК"
        else:
            text = f"МСК {i:+d}"

        row.append(InlineKeyboardButton(
            text=text,
            callback_data=f"tz_{i+3}"
        ))

        if len(row) == 4:  # компактная сетка
            kb.append(row)
            row = []

    if row:
        kb.append(row)

    return InlineKeyboardMarkup(inline_keyboard=kb)



# ✅ ДОБАВЛЕНО (новое меню статистики)



# =========================
# СТАРТ
# =========================
@dp.message(F.text == "❓ FAQ")
async def open_faq_msg(m: Message):
    await m.answer(
        "❓ FAQ / Помощь\n\nВыбери раздел:",
        reply_markup=keyboards.faq_menu()
    )


@dp.callback_query(F.data == "faq")
async def open_faq(c: CallbackQuery):
    await c.message.edit_text(
        "❓ FAQ / Помощь\n\nВыбери раздел:",
        reply_markup=keyboards.faq_menu()
    )
    await c.answer()

# =========================
# МЕНЮ
# =========================
@dp.callback_query(F.data == "budget")
async def budget(c: CallbackQuery):
    text = "💵 Финансы"

    if get_tips(c.from_user.id):
        text += (
                "\n\n💡Подсказка<blockquote>"
                "Здесь ты можешь управлять своими средствами:\n"
                "1)💸Добавлять расходы — просто отправь сообщение из банка или напиши сумму и категорию (например: 500 еда)\n"
                "2)💰Добавлять доходы — укажи сумму и выбери категорию\n"
                "3)📊Строить графики и контролировать баланс в аналитике\n"
                "4)↩️Отменить последние 5 операций\n"
                "5)📜*Если активирована Premium функция* можно управлять накоплениями\n\n"
                "Фишки:\n"
                "—🗄️Огромная база распознавания категорий\n"
                "—🤖Бот обучается под Вас\n"
                "—📜*Если активирована Premium функция*Предлагает откладывать 1/10"
                "</blockquote>"
        )

    await c.message.edit_text(
        text,
        reply_markup=keyboards.budget_menu(
            fin_enabled=is_fin_enabled(c.from_user.id)
        ),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "back_main")
async def back_main(c: CallbackQuery):
    await c.message.answer("Главное меню", reply_markup=keyboards.get_main_menu())
        


# =========================
# РАСХОД (НЕ ТРОГАЕМ)
# =========================
@dp.callback_query(F.data == "expense")
async def expense(c: CallbackQuery, state: FSMContext):
    await state.set_state(AddTransaction.waiting_sum)
    await c.message.answer("Введите сумму или пришлите сообщение из банка")


@dp.message(AddTransaction.waiting_sum)
async def expense_sum(m: Message, state: FSMContext):
    amount = parse_amount(m.text)
    if not amount:
        await m.answer("❌ Не нашел сумму")
        return

    category = detect_category(m.text, m.from_user.id)

    await state.update_data(
        amount=amount,
        category=category,
        original_text=m.text
    )

    await m.answer(
        f"Сумма: {amount} ₽\nКатегория: {category}",
        reply_markup=confirm_kb("exp")
    )


@dp.callback_query(F.data == "exp_confirm")
async def exp_confirm(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    amount = data["amount"]
    category = data["category"]

    # 🔥 НАКОПЛЕНИЯ (расход → копилка)
    if category.lower() == "накопления":
        add_savings(c.from_user.id, amount)
        await state.clear()

        await c.message.answer(
            f"💰 {amount} ₽ → Накопления\n\n✔ Перемещено из баланса",
            reply_markup=keyboards.budget_menu(
                fin_enabled=is_fin_enabled(c.from_user.id)
            )
        )
        return

    add_transaction(c.from_user.id, amount, "expense", category)

    await state.clear()

    await c.message.answer(
        f"✅ {amount} ₽ → {category}",
        reply_markup=keyboards.budget_menu(
            fin_enabled=is_fin_enabled(c.from_user.id)
        )
    )


@dp.callback_query(F.data == "exp_change")
async def exp_change(c: CallbackQuery, state: FSMContext):
    await state.set_state(AddTransaction.waiting_category)
    await c.message.answer("Выбери категорию", reply_markup=keyboards.categories_menu())


@dp.callback_query(AddTransaction.waiting_category, F.data.startswith("cat_"))
async def exp_set_cat(c: CallbackQuery, state: FSMContext):
    if c.data == "cat_custom":
        await state.set_state(AddTransaction.waiting_custom_category)
        await c.message.answer("Введи свою категорию")
        return

    cat = c.data.replace("cat_", "")
    await state.update_data(category=cat)

    data = await state.get_data()

    await c.message.answer(
        f"Сумма: {data['amount']} ₽\nКатегория: {cat}",
        reply_markup=confirm_kb("exp")
    )


@dp.message(AddTransaction.waiting_custom_category)
async def exp_custom(m: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(category=m.text)

    text = data.get("original_text","").lower()
    words = text.split()

    stop_words = ["покупка","карта","баланс","доступно","счет","rub","₽"]

    clean = []
    for w in words:
        w = w.strip(".,:;()")
        if w.isdigit(): continue
        if any(c.isdigit() for c in w): continue
        if w in stop_words: continue
        if len(w) < 3: continue
        clean.append(w)

    if clean:
        keyword = max(clean, key=len)
        add_rule(m.from_user.id, keyword, m.text)

    await m.answer(
        f"Сумма: {data['amount']} ₽\nКатегория: {m.text}",
        reply_markup=confirm_kb("exp")
    )


# =========================
# ДОХОД (НЕ ТРОГАЕМ)
# =========================
from aiogram.fsm.state import StatesGroup, State

class AddIncome(StatesGroup):
    sum = State()
    custom = State()

class SavingsState(StatesGroup):
    add = State()
    remove = State()

@dp.callback_query(F.data == "sav_add")
async def sav_add(c: CallbackQuery, state: FSMContext):
    await state.set_state(SavingsState.add)
    await c.message.answer("Введите сумму для добавления:")

@dp.message(SavingsState.add)
async def sav_add_process(m: Message, state: FSMContext):
    amount = parse_amount(m.text)

    if not amount:
        await m.answer("❌ Ошибка суммы")
        return

    add_savings(m.from_user.id, amount)

    await state.clear()

    await m.answer(f"✅ Добавлено в накопления: {amount:,} ₽")

@dp.callback_query(F.data == "sav_remove")
async def remove_savings_start(c: CallbackQuery, state: FSMContext):
    await state.set_state("remove_savings")

    await c.message.answer("Введите сумму для списания")
    
@dp.message(F.text, StateFilter("remove_savings"))
async def remove_savings_finish(m: Message, state: FSMContext):
    amount = parse_amount(m.text)
    user_id = m.from_user.id

    if not amount:
        await m.answer("❌ Неверная сумма")
        return

    success = withdraw_savings(user_id, amount)

    if not success:
        await m.answer("❌ Недостаточно накоплений")
        return

    # 🔥 ДОБАВЛЯЕМ В ДОХОД
    add_transaction(user_id, amount, "income", "Накопления")

    await state.clear()

    await m.answer(
        f"➖ Списано: {amount:,} ₽",
        reply_markup=keyboards.budget_menu(is_fin_enabled(user_id))
    )    
    
@dp.message(SavingsState.remove)
async def sav_remove_process(m: Message, state: FSMContext):
    amount = parse_amount(m.text)

    if not amount:
        await m.answer("❌ Ошибка суммы")
        return

    success = withdraw_savings(m.from_user.id, amount)

    await state.clear()

    if success:
        await m.answer(f"💸 Списано: {amount:,} ₽")
    else:
        await m.answer("❌ Недостаточно средств")    
    

@dp.callback_query(F.data == "income")
async def income(c: CallbackQuery, state: FSMContext):
    await state.clear()  # 🔥 убираем мусор
    await state.set_state(AddIncome.sum)

    await c.message.answer("💰 Введите сумму дохода:")


@dp.message(AddIncome.sum)
async def income_sum(m: Message, state: FSMContext):
    amount = parse_amount(m.text)

    if not amount:
        await m.answer("❌ Не нашел сумму")
        return

    await state.update_data(amount=amount)

    await m.answer(
        "💰 Выбери категорию дохода:",
        reply_markup=keyboards.income_categories()
    )

@dp.callback_query(F.data == "save_income_part")
async def save_income_part(c: CallbackQuery, state: FSMContext):
    user_id = c.from_user.id
    data = SAVINGS_BUFFER.get(user_id)

    if not data:
        await c.answer("Ошибка")
        return

    income_part = data["amount"] - data["savings"]

    # доход (уже без 10%)
    add_transaction(user_id, income_part, "income", data["category"])

    # накопления
    add_savings(user_id, data["savings"])

    SAVINGS_BUFFER.pop(user_id, None)
    await state.clear()

    await c.message.answer(
        f"💰 Отложено: {data['savings']:,} ₽\n"
        f"💵 В доход учтено: {income_part:,} ₽",
        reply_markup=keyboards.budget_menu(is_fin_enabled(user_id))
    )


@dp.callback_query(F.data == "subscription")
async def subscription(c: CallbackQuery):
    await c.message.answer(
        "📦 Premium\n\nВыбери функцию:",
        reply_markup=keyboards.subscription_menu()
    )

@dp.callback_query(F.data == "toggle_fin_system")
async def toggle_fin_system_handler(c: CallbackQuery):
    user_id = c.from_user.id

    new_state = toggle_fin_enabled(user_id)

    await c.answer(
        "✅ Включено" if new_state else "❌ Выключено",
        show_alert=True
    )

    await fin_menu(c)
    
@dp.callback_query(F.data == "fin_menu")
async def fin_menu(c: CallbackQuery):
    user_id = c.from_user.id
    enabled = is_fin_enabled(user_id)

    status = "✅ Включено" if enabled else "❌ Выключено"
    btn_text = "🔴 Выключить" if enabled else "🟢 Включить"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_text, callback_data="toggle_fin_system")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_sub")]
    ])

    await c.message.answer(
        "💰 Финансовая система\n"
        "«Самый богатый человек в Вавилоне»\n"
        "Джордж С. Клейсон\n\n"

        "1. Платите себе первым — откладывай минимум 10% дохода сразу\n"
        "2. Контролируй расходы — понимай куда уходят деньги\n"
        "3. Создавай накопления — формируй финансовую подушку\n"
        "4. Увеличивай доход — развивай навыки и ищи новые источники\n"
        "5. Инвестируй — заставь деньги работать на тебя\n"
        "6. Не влезай в долги — кредиты убивают рост\n"
        "7. Защищай капитал — избегай рискованных решений\n"
        "8. Думай самостоятельно — не следуй слепо чужим советам\n"
        "9. Учись на ошибках — своих и чужих\n"
        "10. Используй ресурсы разумно — время, энергия, деньги\n\n"

        "Дополнительно:\n"
        "— Создай финансовую подушку (3–6 месяцев жизни)\n"
        "— Инвестируй только в то, что понимаешь\n"
        "— Деньги = инструмент, а не цель\n\n"

        "🔓 После активации открывается доступ к системе накоплений —\n"
        "инструменту, который помогает автоматически внедрить ключевые принципы:\n"
        "платить себе первым, контролировать расходы и стабильно наращивать капитал.\n\n"

        f"Статус: {status}",
        reply_markup=kb
    )


  

@dp.callback_query(F.data == "back_fin")
async def back_fin(c: CallbackQuery):
    await c.message.edit_text(
        "💵 Финансы",
        reply_markup=keyboards.budget_menu(is_fin_enabled(c.from_user.id))
    )



@dp.callback_query(F.data == "skip_income_part")
async def skip_income_part(c: CallbackQuery, state: FSMContext):
    user_id = c.from_user.id
    data = SAVINGS_BUFFER.get(user_id)

    if not data:
        await c.answer("Ошибка")
        return

    add_transaction(user_id, data["amount"], "income", data["category"])

    SAVINGS_BUFFER.pop(user_id, None)
    await state.clear()

    await c.message.answer(
        f"✅ Доход добавлен: {data['amount']:,} ₽",
        reply_markup=keyboards.budget_menu(is_fin_enabled(user_id))
    )
    
    
@dp.callback_query(F.data == "withdraw_no")
async def withdraw_no(c: CallbackQuery):
    await c.message.answer("❌ Отменено")    


@dp.callback_query(F.data.startswith("withdraw_yes_"))
async def withdraw_yes(c: CallbackQuery):
    amount = int(c.data.split("_")[2])

    success = withdraw_savings(c.from_user.id, amount)

    if not success:
        await c.message.answer("❌ Недостаточно накоплений")
        return

    await c.message.answer(f"✅ Снято: {amount:,} ₽")


@dp.message(AddIncome.custom)
async def inc_custom(m: Message, state: FSMContext):
    data = await state.get_data()

    # 🔥 НОРМАЛИЗАЦИЯ КАК В РАСХОДАХ
    name = m.text.strip()

    if len(name) > 1 and not name[0].isalnum():
        name = name[0] + name[1:].lower()
    else:
        name = name.capitalize()

    await state.update_data(category=name)

    # 🔥 САМООБУЧЕНИЕ (КАК В EXPENSE)
    text = data.get("original_text", "").lower()
    words = text.split()

    stop_words = ["покупка","карта","баланс","доступно","счет","rub","₽"]

    clean = []
    for w in words:
        w = w.strip(".,:;()")
        if w.isdigit(): continue
        if any(c.isdigit() for c in w): continue
        if w in stop_words: continue
        if len(w) < 3: continue
        clean.append(w)

    if clean:
        keyword = max(clean, key=len)
        add_rule(m.from_user.id, keyword, name)

    await m.answer(
        f"Сумма: {data['amount']} ₽\nКатегория: {name}",
        reply_markup=confirm_kb("inc")
    )


@dp.callback_query(F.data == "inc_confirm")
async def inc_confirm(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    amount = data["amount"]
    category = data["category"]

    # 🔥 СНЯТИЕ С КОПИЛКИ
    if category.lower() == "накопления":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"withdraw_yes_{amount}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="withdraw_no")
            ]
        ])

        await c.message.answer(
            f"💰 Снять из накоплений: {amount:,} ₽?",
            reply_markup=kb
        )
        return

    add_transaction(c.from_user.id, amount, "income", category)

    await state.clear()

    await c.message.answer(
        f"✅ {amount} ₽ → {category}",
        reply_markup=keyboards.budget_menu(
            fin_enabled=is_fin_enabled(c.from_user.id)
        )
    )

# =========================
# 📊 СТАТИСТИКА (ИСПРАВЛЕНА)
# =========================
@dp.callback_query(F.data == "finance_stats")
async def stats(c: CallbackQuery):
    user_id = c.from_user.id
    users = resolve_users_for_analytics(user_id)

    print("\n===== ANALYTICS START =====")
    print(f"[DEBUG] user_id={user_id}")
    print(f"[DEBUG] active_users={users}")

    text = "📊 Аналитика\n\n"

    total_income_map = {}
    total_expense_map = {}
    user_income_map = {}
    user_expense_map = {}

    for uid in users:
        cur.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE user_id=? AND type='income'
            GROUP BY category
        """, (uid,))
        income = cur.fetchall()

        cur.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE user_id=? AND type='expense'
            GROUP BY category
        """, (uid,))
        expense = cur.fetchall()

        user_income_map[uid] = dict(income)
        user_expense_map[uid] = dict(expense)

        for cat, amount in income:
            total_income_map[cat] = total_income_map.get(cat, 0) + amount

        for cat, amount in expense:
            total_expense_map[cat] = total_expense_map.get(cat, 0) + amount

    total_income = sum(total_income_map.values())
    total_expense = sum(total_expense_map.values())

    # ===== ДОХОДЫ =====
    text += "💰 Доходы:\n"

    if total_income_map:
        for cat, amount in total_income_map.items():
            percent = int(amount / total_income * 100) if total_income else 0
            text += f"{cat} — {amount} ₽ ({percent}%)\n"

            contributors = []
            for uid in users:
                val = user_income_map.get(uid, {}).get(cat, 0)
                if val > 0:
                    profile = get_user_profile(uid)
                    name = profile[0] if profile and profile[0] else f"id:{uid}"
                    contributors.append((uid, name, val))

            if len(contributors) > 1:
                for uid2, name, val in contributors:
                    profile = get_user_profile(uid2)
                    gender = "male"

                    if profile and len(profile) > 3 and profile[3]:
                        gender = str(profile[3]).lower()

                    emoji = "👩" if gender in ["female", "f", "ж"] else "👤"
                    text += f"   {emoji}{name} — {val} ₽\n"
    else:
        text += "нет данных\n"

    # ===== РАСХОДЫ =====
    text += "\n💸 Расходы:\n"

    if total_expense_map:
        for cat, amount in total_expense_map.items():
            percent = int(amount / total_expense * 100) if total_expense else 0
            text += f"{cat} — {amount} ₽ ({percent}%)\n"

            contributors = []
            for uid in users:
                val = user_expense_map.get(uid, {}).get(cat, 0)
                if val > 0:
                    profile = get_user_profile(uid)
                    name = profile[0] if profile and profile[0] else f"id:{uid}"
                    contributors.append((uid, name, val))

            if len(contributors) > 1:
                for uid2, name, val in contributors:
                    profile = get_user_profile(uid2)
                    gender = "male"

                    if profile and len(profile) > 3 and profile[3]:
                        gender = str(profile[3]).lower()

                    emoji = "👩" if gender in ["female", "f", "ж"] else "👤"
                    text += f"   {emoji}{name} — {val} ₽\n"
    else:
        text += "нет данных\n"

    balance = total_income - total_expense

    text += (
        "\n───────────────\n"
        f"📈 Баланс: {balance} ₽\n"
        f"Доход: {total_income} ₽ | Расход: {total_expense} ₽\n"
        "───────────────\n"
    )

    # 🔥 ВАЖНО: ЕСЛИ ВЫКЛЮЧЕНО — ВООБЩЕ НЕ ПОКАЗЫВАЕМ НАКОПЛЕНИЯ
    if is_fin_enabled(user_id):
        savings = get_savings(user_id)
        percent = int((savings / total_income) * 100) if total_income else 0

        if percent == 0:
            status = "❌"
            text_status = "Ты пока не платишь себе первым"
        elif percent < 10:
            status = "⚠️"
            text_status = "Ниже нормы (10%)"
        elif percent < 20:
            status = "👍"
            text_status = "Хороший уровень"
        else:
            status = "🔥"
            text_status = "Отлично"

        text += (
            f"💰 Накопления — {savings} ₽\n"
            f"📊 Ты откладываешь: {percent}% {status} {text_status}\n"
        )

        text += "\n\n" + get_motivation_text()

    try:
        await c.message.edit_text(text, reply_markup=stats_menu())
    except:
        await c.message.answer(text, reply_markup=stats_menu())

def stats_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Расходы", callback_data="graph_expense"),
            InlineKeyboardButton(text="📉 Доходы", callback_data="graph_income")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="budget_menu")
        ]
    ])

@dp.callback_query(F.data == "budget_menu")
async def open_budget_menu(c: CallbackQuery):
    await c.answer()

    try:
        await c.message.edit_text(
            "💰 Финансы",
            reply_markup=keyboards.budget_menu(
                fin_enabled=is_fin_enabled(c.from_user.id)
            )
        )
    except:
        await c.message.answer(
            "💰 Финансы",
            reply_markup=keyboards.budget_menu(
                fin_enabled=is_fin_enabled(c.from_user.id)
            )
        )
    


   


@dp.callback_query(F.data.startswith("inc_cat_"))
async def income_category(c: CallbackQuery, state: FSMContext):
    category = c.data.split("_")[2]

    if category == "custom":
        await state.set_state(AddIncome.custom)
        await c.message.answer("Введи категорию")
        return

    data = await state.get_data()
    amount = data.get("amount")

    if amount is None:
        await c.message.answer("❌ Сначала введи сумму")
        return

    user_id = c.from_user.id

    # ===== ЕСЛИ ВАВИЛОН ВЫКЛЮЧЕН =====
    if not is_fin_enabled(user_id):
        add_transaction(user_id, amount, "income", category)

        await state.clear()

        await c.message.answer(
            f"✅ Доход добавлен: {amount:,} ₽ → {category}",
            reply_markup=keyboards.budget_menu(is_fin_enabled(user_id))
        )
        return

    # ===== ВОССТАНОВЛЕННАЯ ЛОГИКА ВАВИЛОНА =====
    percent = get_savings_percent(user_id)
    if percent <= 0:
        percent = 10

    savings_part = int(amount * percent / 100)

    SAVINGS_BUFFER[user_id] = {
        "amount": amount,
        "category": category,
        "savings": savings_part
    }

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"💰 Отложить {savings_part} ₽ ({percent}%)",
                callback_data="save_income_part"
            ),
            InlineKeyboardButton(
                text="❌ Пропустить",
                callback_data="skip_income_part"
            )
        ]
    ])

    await c.message.answer(
        f"💰 Доход: {amount:,} ₽ → {category}\n\n"
        f"📌 Отложить {percent}%?\n👉 {savings_part:,} ₽",
        reply_markup=kb
    )

# =========================
# 📉 ГРАФИК РАСХОДОВ
# =========================
@dp.callback_query(F.data == "graph_expense")
async def graph_expense(c: CallbackQuery):
    user_id = c.from_user.id
    users = resolve_users_for_analytics(user_id)  # ✅ ВОТ ЕДИНСТВЕННЫЙ ФИКС

    all_data = {}

    for uid in users:
        data = get_expense_stats(uid)
        for cat, amount in data:
            all_data[cat] = all_data.get(cat, 0) + amount

    if not all_data:
        await c.message.answer("Нет данных", reply_markup=keyboards.budget_menu(is_fin_enabled(user_id)))
        return

    cats = list(all_data.keys())
    vals = list(all_data.values())

    total = sum(vals)

    def autopct(pct):
        val = int(pct * total / 100)
        return f"{val} ₽\n({int(pct)}%)"

    plt.figure(figsize=(7, 7), facecolor="#1e1e2f")

    colors = ["#00c896", "#ff6b6b", "#4dabf7", "#ffd43b", "#845ef7"]

    plt.pie(
        vals,
        labels=cats,
        autopct=autopct,
        startangle=140,
        colors=colors,
        textprops={"color": "white", "fontsize": 14},
        wedgeprops={"edgecolor": "#1e1e2f", "linewidth": 2}
    )

    title = "Расходы"
    if len(users) > 1:
        title += " (вся семья)"

    plt.title(title, fontsize=20, color="white")

    file_name = "expense.png"
    plt.savefig(file_name, facecolor="#1e1e2f")
    plt.close()

    await c.message.answer_photo(FSInputFile(file_name))

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="finance_stats")]
    ])

    await c.message.answer("📊 Готово", reply_markup=kb)


# ========================
# 💰 ГРАФИК ДОХОДОВ
# ========================
@dp.callback_query(F.data == "graph_income")
async def graph_income(c: CallbackQuery):
    user_id = c.from_user.id
    users = resolve_users_for_analytics(user_id)  # ✅ ФИКС

    all_data = {}

    for uid in users:
        data = get_income_stats(uid)
        for cat, amount in data:
            all_data[cat] = all_data.get(cat, 0) + amount

    if not all_data:
        await c.message.answer("Нет данных", reply_markup=keyboards.budget_menu(is_fin_enabled(user_id)))
        return

    cats = list(all_data.keys())
    vals = list(all_data.values())

    total = sum(vals)

    def autopct(pct):
        val = int(pct * total / 100)
        return f"{val} ₽\n({int(pct)}%)"

    plt.figure(figsize=(7, 7), facecolor="#1e1e2f")

    colors = ["#51cf66", "#339af0", "#fcc419", "#ff922b", "#f06595"]

    plt.pie(
        vals,
        labels=cats,
        autopct=autopct,
        startangle=140,
        colors=colors,
        textprops={"color": "white", "fontsize": 14},
        wedgeprops={"edgecolor": "#1e1e2f", "linewidth": 2}
    )

    title = "Доходы"
    if len(users) > 1:
        title += " (вся семья)"

    plt.title(title, fontsize=20, color="white")

    file_name = "income.png"
    plt.savefig(file_name, facecolor="#1e1e2f")
    plt.close()

    await c.message.answer_photo(FSInputFile(file_name))

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="finance_stats")]
    ])

    await c.message.answer("📊 Готово", reply_markup=kb)

  
  

def enable_fin(user_id):
    cur.execute("UPDATE users SET fin_enabled=1 WHERE id=?", (user_id,))
    conn.commit()


def disable_fin(user_id):
    cur.execute("UPDATE users SET fin_enabled=0 WHERE id=?", (user_id,))
    conn.commit()  
      
    

# =========================
# Отмена операций
# =========================   
    
def get_last_transactions(user_id, limit=5):
    users = get_family_members(user_id)

    cur.execute(f"""
        SELECT rowid, amount, type, category
        FROM transactions
        WHERE user_id IN ({",".join("?"*len(users))})
        ORDER BY rowid DESC
        LIMIT ?
    """, (*users, limit))

    return cur.fetchall()
    
def build_undo_kb(transactions):
    kb = []

    for t in transactions:
        row_id, amount, t_type, category = t

        if t_type == "income":
            type_text = "📈 Доход"
        else:
            type_text = "📉 Расход"

        text = f"{amount} ₽ | {type_text} | {category}"

        kb.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"del_{row_id}"
            )
        ])

    kb.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="del_back")
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb)    
    
@dp.callback_query(F.data == "undo_menu")
async def undo_menu_open(c: CallbackQuery):
    await c.answer()

    transactions = get_last_transactions(c.from_user.id)

    if not transactions:
        await c.answer("Нет операций", show_alert=True)
        return

    await c.message.answer(
        "Последние операции:",
        reply_markup=build_undo_kb(transactions)
    )    

@dp.callback_query(F.data.startswith("del_") & ~F.data.startswith("del_yes_") & (F.data != "del_back"))
async def confirm_delete(c: CallbackQuery):
    await c.answer()

    row_id = int(c.data.split("_")[1])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del_yes_{row_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="undo_menu")
        ]
    ])

    await c.message.answer(
        "Удалить операцию?",
        reply_markup=kb
    )
 
@dp.callback_query(F.data.startswith("del_yes_"))
async def delete_op(c: CallbackQuery):
    await c.answer("Удалено")

    row_id = int(c.data.split("_")[2])

    cur.execute("DELETE FROM transactions WHERE rowid=?", (row_id,))
    conn.commit()

    await c.message.delete()

    # 🔥 ОБНОВЛЯЕМ СПИСОК
    transactions = get_last_transactions(c.from_user.id)

    if not transactions:
        await c.message.answer(
            "Нет операций",
            reply_markup=keyboards.budget_menu(is_fin_enabled(c.from_user.id))
        )
        return

    await c.message.answer(
        "Обновлённый список:",
        reply_markup=build_undo_kb(transactions)
    ) 
 
@dp.callback_query(F.data == "del_back")
async def back_fin(c: CallbackQuery):
    await c.answer()

    await c.message.answer(
        "Меню финансов",
        reply_markup=keyboards.budget_menu(is_fin_enabled(c.from_user.id))
    ) 
# =========================
# 🏋️ ПРИВЫЧКИ
# =========================

from datetime import datetime

DAYS = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]


@dp.callback_query(F.data == "habits")
async def habits_menu_handler(c: CallbackQuery):
    text = "📋 Привычки/Задачи"

    if get_tips(c.from_user.id):
        text += (
            "\n\n💡Подсказка<blockquote>"
            "Создавай привычки и задачи:\n"
            "• Личные и общие\n"
            "• Настраивай дни и время\n"
            "• Добавляй напоминания\n\n"
            "Затем:\n"
            "— Отмечай выполнение, нажав на название в меню управление\n"
            "— Смотри весь список за нелелю/месяц/все время в меню прогресс\n"
            "— Есть система Стрика 🔥"
            "</blockquote>"
        )

    await c.message.edit_text(
        text,
        reply_markup=keyboards.habits_menu(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "tips_on")
async def tips_on(c: CallbackQuery):
    set_tips(c.from_user.id, 1)
    await c.message.answer("🏠 Главное меню", reply_markup=keyboards.get_main_menu())

@dp.message(F.text == "💡 Подсказки")
async def tips_settings(message: Message):
    enabled = get_tips(message.from_user.id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔴 Выключить" if enabled else "🟢 Включить",
            callback_data="toggle_tips"
        )]
    ])

    await message.answer(
        f"Подсказки: {'включены' if enabled else 'выключены'}",
        reply_markup=kb
    )
@dp.callback_query(F.data == "tips_off")
async def tips_off(c: CallbackQuery):
    set_tips(c.from_user.id, 0)
    await c.message.answer(
        "🏠 Главное меню",
        reply_markup=keyboards.get_main_menu()
    )



@dp.callback_query(F.data == "habit_add")
async def habit_add_start(c: CallbackQuery, state: FSMContext):
    await c.answer()

    await state.set_state(AddHabit.name)
    await c.message.answer("Введите название привычки")


@dp.message(AddHabit.name)
async def habit_name(m: Message, state: FSMContext):
    name = m.text.strip()

    # если первый символ не буква/цифра (эмодзи)
    if len(name) > 1 and not name[0].isalnum():
        name = name[0] + name[1:].upper()
    else:
        name = name.upper()

    await state.update_data(name=name)
    await state.set_state(AddHabit.type)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Личная", callback_data="habit_type_personal")],
        [InlineKeyboardButton(text="👥 Общая", callback_data="habit_type_family")]
    ])

    await m.answer("Выбери тип", reply_markup=kb)


def get_days_kb(selected):
    kb = []
    row = []

    for d in DAYS:
        if d in selected:
            text = f"•{d}"
        else:
            text = f" {d}"

        row.append(InlineKeyboardButton(
            text=text,
            callback_data=f"day_{d}"
        ))

    kb.append(row)
    kb.append([InlineKeyboardButton(text="✅ Готово", callback_data="days_done")])

    return InlineKeyboardMarkup(inline_keyboard=kb)


@dp.callback_query(AddHabit.type, F.data.startswith("habit_type"))
async def habit_type(c: CallbackQuery, state: FSMContext):
    await c.answer()

    h_type = "personal" if "personal" in c.data else "family"
    await state.update_data(type=h_type, days=[])

    await state.set_state(AddHabit.task_type)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Цикличная", callback_data="task_cycle")],
        [InlineKeyboardButton(text="🎯 Разовая", callback_data="task_once")]
    ])

    await c.message.edit_text("Тип задачи", reply_markup=kb)


@dp.callback_query(F.data.startswith("day_"))
async def toggle_days(c: CallbackQuery, state: FSMContext):
    await c.answer()

    data = await state.get_data()
    days = data.get("days", [])

    d = c.data.replace("day_", "")

    if data.get("task_type") == "once":
        days = [d]
    else:
        if d in days:
            days.remove(d)
        else:
            days.append(d)

    # 🔥 ВАЖНО — СОРТИРОВКА
    order = {day: i for i, day in enumerate(DAYS)}
    days = sorted(days, key=lambda x: order[x])

    await state.update_data(days=days)

    await c.message.edit_reply_markup(
        reply_markup=get_days_kb(days)
    )


def get_hours_kb():
    kb = []
    row = []

    for h in range(0, 24):
        row.append(InlineKeyboardButton(
            text=f"{h:02d}",
            callback_data=f"hour_{h:02d}"
        ))
        if len(row) == 6:
            kb.append(row)
            row = []

    if row:
        kb.append(row)

    kb.append([
        InlineKeyboardButton(text="❌ Без времени", callback_data="skip_time")
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_minutes_kb(hour):
    kb = []
    row = []

    for m in range(0, 60, 5):
        label = f"{m:02d}"

        if m % 15 == 0:
            label = f"🔥{label}"

        row.append(InlineKeyboardButton(
            text=label,
            callback_data=f"min_{hour}_{m:02d}"
        ))

        if len(row) == 6:
            kb.append(row)
            row = []

    if row:
        kb.append(row)

    return InlineKeyboardMarkup(inline_keyboard=kb)


@dp.callback_query(F.data == "days_done")
async def days_done(c: CallbackQuery, state: FSMContext):
    await c.answer()

    data = await state.get_data()

    if not data.get("days"):
        await c.answer("Выбери хотя бы 1 день", show_alert=True)
        return

    await state.set_state(AddHabit.time)

    await c.message.edit_text(
        "Выбери час",
        reply_markup=get_hours_kb()
    )


@dp.callback_query(AddHabit.time, F.data.startswith("hour_"))
async def select_hour(c: CallbackQuery, state: FSMContext):
    await c.answer()

    hour = c.data.split("_")[1]

    await c.message.edit_text(
        "Выбери минуты",
        reply_markup=get_minutes_kb(hour)
    )


@dp.callback_query(AddHabit.time, F.data == "skip_time")
async def skip_time(c: CallbackQuery, state: FSMContext):
    await c.answer()

    await state.update_data(time=None, reminder=None)

    await finish_habit_creation(c, state)
    
    


@dp.callback_query(AddHabit.time, F.data.startswith("min_"))
async def select_minute(c: CallbackQuery, state: FSMContext):
    await c.answer()

    _, hour, minute = c.data.split("_")
    time = f"{hour}:{minute}"

    await state.update_data(time=time)

    # 🔥 ВАЖНО — меняем состояние
    await state.set_state(AddHabit.reminder)

    await c.message.edit_text(
        "Включить напоминание?",
        reply_markup=reminder_kb()
    )

@dp.callback_query(AddHabit.reminder, F.data.startswith("rem_"))
async def set_reminder(c: CallbackQuery, state: FSMContext):
    await c.answer()

    if c.data == "rem_skip":
        reminder = None
    else:
        reminder = int(c.data.split("_")[1])

    await state.update_data(reminder=reminder)

    await finish_habit_creation(c, state)

@dp.message(AddHabit.time)
async def set_time(m: Message, state: FSMContext):
    import re

    data = await state.get_data()

    # =========================
    # 🏋️ ПРИВЫЧКА (КАК БЫЛО)
    # =========================
    if not re.match(r"^\d{2}:\d{2}$", m.text):
        await m.answer("Формат времени: 12:30")
        return

    await state.update_data(time=m.text)

    await state.set_state(AddHabit.reminder)

    await m.answer(
        "Включить напоминание?",
        reply_markup=reminder_kb()
    )

    
async def finish_habit_creation(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user_id = c.from_user.id

    name = data.get("name")
    days = data.get("days")
    h_type = data.get("type")
    time = data.get("time")
    task_type = data.get("task_type")
    reminder = data.get("reminder")

    # =========================
    # 🎯 ЕСЛИ ЗАДАЧА
    # =========================
    if task_type == "task":
        h_type = "personal"   # ❗ без семьи
        time = None           # ❗ убираем время привычки

    # =========================
    # 🏋️ ПРИВЫЧКА
    # =========================
    else:
        if isinstance(days, list):
            days = ",".join(days)

    tz = get_user_timezone(user_id)

    add_habit(
        user_id,
        name,
        days,
        h_type,
        time,
        task_type,
        family_id=None,
        reminder=reminder,
        tz=tz
    )

    await state.clear()

    try:
        await c.message.delete()
    except:
        pass

    await c.message.answer(
        "✅ Создано",
        reply_markup=keyboards.habits_menu()
    )

    await c.answer()


@dp.callback_query(AddHabit.task_type)
async def set_task_type(c: CallbackQuery, state: FSMContext):
    await c.answer()

    # ❌ УБРАЛИ ВСЮ ЛОГИКУ once
    task_type = "cycle"

    await state.update_data(task_type=task_type, days=[])

    # ✅ ВСЕГДА ИДЁМ В ДНИ
    await state.set_state(AddHabit.days)
    await c.message.edit_text(
        "Выбери дни",
        reply_markup=get_days_kb([])
    )

# -------------------------
# МОИ ПРИВЫЧКИ
# -------------------------

async def render_habits(user_id):
    habits = get_habits(user_id)

    if not habits:
        text = "Нет привычек\n"
    else:
        text = "📋 <b>Мои привычки и задачи</b>\n\n"

    kb = []

    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    week_dates = get_current_week_dates()

    # =========================
    # 🏋️ ПРИВЫЧКИ
    # =========================
    for h in habits:
        hid, name, days, h_type, time, task_type, reminder = h

        if task_type == "task":
            continue

        order = {day: i for i, day in enumerate(DAYS)}

        days_list = [d for d in days.split(",") if d]
        days_list = sorted(days_list, key=lambda x: order[x])

        logs = get_habit_logs(hid, user_id)
        log_map = {l[0]: l[1] for l in logs}

        bar = ""
        for d in days_list:
            date_index = DAYS.index(d)
            date = week_dates[date_index]

            key = date + "_" + d

            if key in log_map:
                if log_map[key] == "done":
                    bar += get_user_color(user_id)
                elif log_map[key] == "skip":
                    bar += "🟥"
            else:
                bar += "⬜"

            bar += " "

        bar = bar.strip()

        labels = ""
        for i, d in enumerate(days_list):
            labels += d + " "
            if i == 2:
                labels += " "
        labels = labels.strip()

        title = f"{name} ({time})" if time else name

        text += (
            f"🔹 <b><i>{title}</i></b>\n"
            f"<code>{labels}</code>\n"
            f"<code>{bar}</code>\n"
            f"───────────────\n"
        )

        if "⬜" in bar:
            kb.append([
                InlineKeyboardButton(text=name, callback_data=f"open_{hid}")
            ])

    # =========================
    # 🎯 ЗАДАЧИ (ФИКС ДАТЫ + ВРЕМЕНИ)
    # =========================
    cur.execute("""
        SELECT rowid, name, days, time
        FROM habits
        WHERE user_id=? AND task_type='task'
    """, (user_id,))

    tasks = cur.fetchall()

    if tasks:
        text += "\n🎯 <b>Задачи</b>\n\n"

    for tid, name, date, time in tasks:

        # ===== ДАТА =====
        date_str = ""
        if date:
            try:
                dt = datetime.strptime(date, "%Y-%m-%d")

                if dt.year == datetime.now().year:
                    date_str = dt.strftime("%d.%m")
                else:
                    date_str = dt.strftime("%d.%m.%Y")
            except:
                date_str = date

        # ===== СКРЫВАЕМ ПРОСРОЧЕННЫЕ =====
        if date:
            try:
                if datetime.strptime(date, "%Y-%m-%d") < datetime.now():
                    continue
            except:
                pass

        # ===== СТАТУС =====
        cur.execute("""
            SELECT 1 FROM habit_logs
            WHERE habit_id=? AND user_id=? AND status='done'
        """, (tid, user_id))

        done = cur.fetchone()

        # ===== TITLE =====
        title = name

        if time:
            title += f" ({time})"

        if date_str:
            title += f" [{date_str}]"

        # ===== ВЫВОД =====
        if done:
            text += f"<s>• {title}</s>\n"
        else:
            text += f"• {title}\n"
            kb.append([
                InlineKeyboardButton(text=name, callback_data=f"task_open_{tid}")
            ])

    # =========================
    # 🌅 МАГИЯ УТРА
    # =========================
    cur.execute("SELECT morning_enabled FROM users WHERE id=?", (user_id,))
    res = cur.fetchone()

    if res and res[0] == 1:
        progress = get_morning_progress(user_id)

        text += (
            f"\n🌅 <b>Магия утра</b>\n"
            f"<code>{progress}</code>\n"
            f"───────────────\n"
        )

    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="habits")])

    return text, InlineKeyboardMarkup(inline_keyboard=kb)


async def show_my_habits(c: CallbackQuery, mode="personal"):
    USER_MODE[c.from_user.id] = mode

    habits = get_habits(c.from_user.id)
    users = get_family_members(c.from_user.id)

    from datetime import datetime
    week_dates = get_current_week_dates()

    text = "📋 <b>Мои привычки</b>\n\n"
    kb = []

    for h in habits:
        hid, name, days, h_type, time, task_type, reminder = h

        if task_type == "task":
            continue

        if mode == "personal" and h_type != "personal":
            continue
        if mode == "family" and h_type != "family":
            continue

        order = {day: i for i, day in enumerate(DAYS)}

        days_list = [d for d in days.split(",") if d]
        days_list = sorted(days_list, key=lambda x: order[x])

        active_users = [c.from_user.id] if h_type == "personal" else users

        user_logs = {}
        for uid in active_users:
            logs = get_habit_logs(hid, uid)
            user_logs[uid] = {l[0]: l[1] for l in logs}

        labels_line = ""
        for i, d in enumerate(days_list):
            labels_line += d + " "
            if i == 2:
                labels_line += " "
        labels_line = labels_line.strip()

        if h_type == "personal":
            bar_line = ""

            for d in days_list:
                date_index = DAYS.index(d)
                date = week_dates[date_index]

                key = date + "_" + d
                log_map = user_logs.get(c.from_user.id, {})

                if key in log_map:
                    if log_map[key] == "done":
                        block = get_user_color(c.from_user.id)
                    elif log_map[key] == "skip":
                        block = "🟥"
                else:
                    block = "⬜"

                bar_line += block + " "

            bar_line = bar_line.strip()

        else:
            rows = []

            for uid in active_users:
                row = ""
                log_map = user_logs.get(uid, {})

                for d in days_list:
                    date_index = DAYS.index(d)
                    date = week_dates[date_index]

                    key = date + "_" + d

                    if key in log_map:
                        if log_map[key] == "done":
                            block = get_user_color(uid)
                        elif log_map[key] == "skip":
                            block = "🟥"
                    else:
                        block = "⬜"

                    row += block + " "

                rows.append(row.strip())

            bar_line = "\n".join(rows)

        title = f"{name} ({time})" if time else name

        text += (
            f"🔹 <b><i>{title}</i></b>\n"
            f"<code>{labels_line}</code>\n"
            f"<code>{bar_line}</code>\n"
            f"───────────────\n"
        )

        if "⬜" in bar_line:
            kb.append([
                InlineKeyboardButton(text=name, callback_data=f"open_{hid}")
            ])

    if mode == "personal":
        kb.append([InlineKeyboardButton(text="👥 Общие", callback_data="my_family")])
    else:
        kb.append([InlineKeyboardButton(text="👤 Личные", callback_data="my_personal")])

    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="habits")])

    await c.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "habit_list")
async def habit_list(c: CallbackQuery):
    await show_my_habits(c)
 
@dp.callback_query(F.data == "my_family")
async def my_family(c: CallbackQuery):
    await show_my_habits(c, mode="family")

@dp.callback_query(F.data == "my_personal")
async def my_personal(c: CallbackQuery):
    await show_my_habits(c, mode="personal") 
 
@dp.callback_query(F.data.startswith("open_"))
async def open_habit(c: CallbackQuery):
    hid = int(c.data.split("_")[1])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнить", callback_data=f"choose_done_{hid}")],
        [InlineKeyboardButton(text="❌ Пропустить", callback_data=f"choose_skip_{hid}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del_{hid}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="habit_list")]
    ])

    await c.message.edit_text("Выбери действие:", reply_markup=kb)
    
def get_streak(habit_id, user_id):
    habits = get_habits(user_id)

    habit = None
    for h in habits:
        if h[0] == habit_id:
            habit = h
            break

    if not habit:
        return 0

    hid, name, days, h_type, time, task_type, reminder = habit

    if task_type == "once":
        return 0

    users = [user_id]

    if h_type == "family":
        users = get_family_members(user_id)

    total_done = 0

    for uid in users:
        logs = get_habit_logs(habit_id, uid)

        for log_date, status in logs:
            if status == "done":
                total_done += 1

    # 🔥 для семейной — делим на участников
    if h_type == "family" and users:
        total_done = total_done // len(users)

    return total_done    
    
@dp.callback_query(F.data.startswith("choose_"))
async def choose_action(c: CallbackQuery):
    _, action, hid = c.data.split("_")
    hid = int(hid)

    users = get_family_members(c.from_user.id)

    habit = None

    for uid in users:
        habits = get_habits(uid)
        for h in habits:
            if h[0] == hid:
                habit = h
                break
        if habit:
            break

    if not habit:
        return

    days = [d for d in habit[2].split(",") if d]

    from datetime import datetime
    week_dates = get_current_week_dates()

    if len(days) == 1:
        d = days[0]

        date_index = DAYS.index(d)
        date = week_dates[date_index]

        key = date + "_" + d

        logs = get_habit_logs(hid, c.from_user.id)

        for l in logs:
            if l[0] == key:
                await c.answer("Уже отмечено", show_alert=True)
                return

        if action == "done":
            add_habit_log(hid, c.from_user.id, key, "done")
            await c.answer("✅ Выполнено")
        else:
            add_habit_log(hid, c.from_user.id, key, "skip")
            await c.answer("❌ Пропущено")

        mode = USER_MODE.get(c.from_user.id, "personal")
        await show_my_habits(c, mode=mode)
        return

    logs = get_habit_logs(hid, c.from_user.id)

    used_days = set()
    for log_date, status in logs:
        for d in days:
            date_index = DAYS.index(d)
            date = week_dates[date_index]
            if log_date == date + "_" + d:
                used_days.add(d)

    kb = []

    for d in days:
        if d not in used_days:
            kb.append([
                InlineKeyboardButton(
                    text=d,
                    callback_data=f"{action}_{hid}_{d}"
                )
            ])

    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="habit_list")])

    await c.message.edit_text("Выбери день:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


# -------------------------
# Задачи
# -------------------------
 
@dp.callback_query(F.data == "task_add")
async def task_add(c: CallbackQuery, state: FSMContext):
    await state.set_state(AddTask.name)
    await c.message.answer("📝 Введи задачу:")


@dp.message(AddTask.name)
async def task_name(m: Message, state: FSMContext):
    name = m.text.strip()

    if not name:
        return await m.answer("Пусто")

    await state.update_data(name=name)
    await state.set_state(AddTask.date)

    await m.answer("📅 Введи дату (пример: 14.02 / 14 02 / 14/02 / 14.02.2026)")

@dp.message(AddTask.date)
async def task_date(m: Message, state: FSMContext):
    date = normalize_date(m.text)

    if not date:
        return await m.answer("❌ Неверный формат даты\nПример: 14.02 / 14 02 / 14/02")

    await state.update_data(date=date)
    await state.set_state(AddTask.time)

    await m.answer("⏰ Выбери время:", reply_markup=get_hours_kb())

@dp.callback_query(AddTask.time, F.data.startswith("hour_"))
async def task_select_hour(c: CallbackQuery, state: FSMContext):
    hour = c.data.split("_")[1]

    await state.update_data(hour=hour)

    await c.message.edit_text(
        "Выбери минуты",
        reply_markup=get_minutes_kb(hour)
    )


@dp.callback_query(AddTask.time, F.data.startswith("min_"))
async def task_select_minute(c: CallbackQuery, state: FSMContext):
    _, hour, minute = c.data.split("_")

    time = f"{hour}:{minute}"

    await state.update_data(time=time)
    await state.set_state(AddTask.reminder)

    await c.message.edit_text(
        "🔔 Напоминание?",
        reply_markup=reminder_kb()
    )


@dp.callback_query(AddTask.time, F.data == "skip_time")
async def task_skip_time(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    add_habit(
        user_id=c.from_user.id,
        name=data["name"],
        days=data["date"],
        h_type="personal",
        time=None,
        task_type="task",
        reminder=None
    )

    await state.clear()

    await c.message.edit_text(
        "✅ Задача создана",
        reply_markup=keyboards.habits_menu()
    )


@dp.callback_query(AddTask.reminder, F.data.startswith("rem_"))
async def task_set_reminder(c: CallbackQuery, state: FSMContext):
    if c.data == "rem_skip":
        reminder = None
    else:
        reminder = int(c.data.split("_")[1])

    data = await state.get_data()

    add_habit(
        user_id=c.from_user.id,
        name=data["name"],
        days=data.get("date"),  # 🔥 ТЕПЕРЬ YYYY-MM-DD
        h_type="personal",
        time=data.get("time"),
        task_type="task",
        reminder=reminder
    )

    await state.clear()

    await c.message.edit_text(
        "✅ Задача создана",
        reply_markup=keyboards.habits_menu()  # ✅ FIX
    )

 

@dp.callback_query(F.data == "task_list")
async def task_list(c: CallbackQuery):
    habits = get_habits(c.from_user.id)
    tasks = [h for h in habits if h[5] == "task"]

    if not tasks:
        return await c.answer("Нет задач", show_alert=True)

    text = "🗂 Задачи\n\n"
    kb = []

    from datetime import datetime

    for i, h in enumerate(tasks, start=1):
        hid, name, date, h_type, time, *_ = h

        # ===== ДАТА =====
        date_str = ""
        if date:
            try:
                dt = datetime.strptime(date, "%Y-%m-%d")

                if dt.year == datetime.now().year:
                    date_str = dt.strftime("%d.%m")
                else:
                    date_str = dt.strftime("%d.%m.%Y")
            except:
                date_str = date

        # ===== ЗАГОЛОВОК =====
        title = name

        if time:
            title += f" ({time})"

        if date_str:
            title += f" • {date_str}"

        kb.append([
            InlineKeyboardButton(
                text=f"{i}) {title}",
                callback_data=f"task_open_{hid}"
            )
        ])

    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="habits")])

    await c.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )





@dp.callback_query(F.data.startswith("task_open_"))
async def task_open(c: CallbackQuery):
    hid = int(c.data.split("_")[2])

    cur.execute("""
        SELECT name, days, time FROM habits WHERE rowid=?
    """, (hid,))
    res = cur.fetchone()

    if not res:
        return

    name, date, time = res

    from datetime import datetime

    date_str = ""
    if date:
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            if dt.year == datetime.now().year:
                date_str = dt.strftime("%d.%m")
            else:
                date_str = dt.strftime("%d.%m.%Y")
        except:
            date_str = date

    title = name
    if time:
        title += f" ({time})"
    if date_str:
        title += f" • {date_str}"

    # ===== настройки пользователя =====
    cur.execute("""
        SELECT productivity_main, productivity_plan, productivity_priority
        FROM users WHERE id=?
    """, (c.from_user.id,))
    main, plan, priority = cur.fetchone()

    kb = []

    # 🔥 ФОКУС (всегда)
    kb.append([InlineKeyboardButton(
        text="▶️ Начать (фокус)",
        callback_data=f"task_focus_{hid}"
    )])

    # ===== ЕСЛИ ВКЛЮЧЕНЫ ФИЧИ =====
    if main:
        kb.append([InlineKeyboardButton(
            text="🏆 Сделать главной",
            callback_data=f"task_make_main_{hid}"
        )])

    if priority:
        kb.append([
            InlineKeyboardButton(text="A", callback_data=f"task_prio_A_{hid}"),
            InlineKeyboardButton(text="B", callback_data=f"task_prio_B_{hid}"),
            InlineKeyboardButton(text="C", callback_data=f"task_prio_C_{hid}")
        ])

    # стандарт
    kb.append([
        InlineKeyboardButton(text="✅ Выполнить", callback_data=f"task_done_{hid}")
    ])

    kb.append([
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"task_del_{hid}")
    ])

    kb.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="task_list")
    ])

    await c.message.edit_text(
        f"📝 Задача\n\n<b>{title}</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )

FOCUS = {}

@dp.callback_query(F.data.startswith("task_focus_stop_"))
async def task_focus_stop(c: CallbackQuery):
    hid = int(c.data.split("_")[3])

    import time
    start = FOCUS.get(c.from_user.id)

    if start:
        duration = int(time.time() - start)
    else:
        duration = 0

    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")

    add_habit_log(hid, c.from_user.id, date, "done")

    await c.message.edit_text(
        f"✅ Выполнено\n⏱ {duration//60} мин",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="task_list")]
        ])
    )

@dp.callback_query(F.data.startswith("task_done_"))
async def task_done(c: CallbackQuery):
    hid = int(c.data.split("_")[2])
    user_id = c.from_user.id

    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")

    logs = get_habit_logs(hid, user_id)

    already_done = any(l[0] == date and l[1] == "done" for l in logs)

    if already_done:
        return await c.answer("Уже выполнено", show_alert=True)

    add_habit_log(hid, user_id, date, "done")

    await c.answer("✅ Выполнено")
    await task_open(c)


@dp.callback_query(F.data.startswith("task_del_"))
async def task_delete(c: CallbackQuery):
    habit_id = int(c.data.split("_")[2])

    delete_habit(habit_id)

    await c.answer("❌ Удалено")
    await task_list(c)





# -------------------------
# ПРОГРЕСС
# -------------------------
@dp.callback_query(F.data == "habit_progress")
async def habit_progress(c: CallbackQuery):
    try:
        await show_progress(c, mode="personal")
    except:
        await c.message.answer("Ошибка открытия прогресса")


def get_current_week_dates():
    from datetime import datetime, timedelta

    today = datetime.now()
    start = today - timedelta(days=today.weekday())  # понедельник

    week = []
    for i in range(7):
        d = start + timedelta(days=i)
        week.append(d.strftime("%Y-%m-%d"))

    return week

def parse_date(text: str):
    from datetime import datetime

    text = text.strip().replace("/", ".").replace(" ", ".")

    parts = text.split(".")

    try:
        if len(parts) == 2:
            day, month = parts
            year = datetime.now().year
        elif len(parts) == 3:
            day, month, year = parts
        else:
            return None

        date = datetime(int(year), int(month), int(day))
        return date.strftime("%Y-%m-%d")

    except:
        return None
# -------------------------
# ACTIONS (done / skip / delete)
# -------------------------

@dp.callback_query(F.data == "done_plan")
async def done_plan(c: CallbackQuery):
    from datetime import datetime

    date = datetime.now().strftime("%Y-%m-%d")

    # 🔥 ПРОВЕРКА
    cur.execute("""
        SELECT 1 FROM morning_logs
        WHERE user_id=? AND step=6 AND date=? AND status=1
    """, (c.from_user.id, date))
    exists = cur.fetchone()

    if exists:
        await c.answer("Уже выполнено", show_alert=True)
        return

    complete_morning_step(c.from_user.id, 6, date)

    try:
        await c.answer("✅ Выполнено")
    except:
        pass

    try:
        await open_morning_menu(c)
    except:
        try:
            await c.message.edit_text(
                "🏠 Главное меню",
                reply_markup=morning_menu_kb(True)
            )
        except:
            await c.message.answer(
                "🏠 Главное меню",
                reply_markup=morning_menu_kb(True)
            )

def get_family_members(user_id):
    try:
        cur.execute("""
            SELECT m2.user_id
            FROM family_members m1
            JOIN family_members m2 ON m1.family_id = m2.family_id
            WHERE m1.user_id=?
        """, (user_id,))

        users = [row[0] for row in cur.fetchall()]

        if not users:
            return [user_id]

        return list(set(users))  # 🔥 УБРАЛИ ДУБЛИ

    except Exception as e:
        print("Ошибка get_family_members:", e)
        return [user_id]

@dp.callback_query(F.data.startswith("done_"))
async def habit_done(c: CallbackQuery):

    if c.data == "done_plan":
        return

    parts = c.data.split("_")
    if len(parts) != 3:
        return

    _, hid, day = parts

    try:
        hid = int(hid)
    except:
        return

    week_dates = get_current_week_dates()

    date_index = DAYS.index(day)
    date = week_dates[date_index]

    key = date + "_" + day

    logs = get_habit_logs(hid, c.from_user.id)

    for l in logs:
        if l[0] == key:
            await c.answer("Уже отмечено", show_alert=True)
            return

    add_habit_log(hid, c.from_user.id, key, "done")

    await c.answer("✅ Выполнено")

    mode = USER_MODE.get(c.from_user.id, "personal")
    await show_my_habits(c, mode=mode)

async def show_progress(c: CallbackQuery, mode="personal", period="week"):
    USER_MODE[c.from_user.id] = mode

    habits = get_habits(c.from_user.id)
    users = get_family_members(c.from_user.id)

    from datetime import datetime, timedelta
    now = datetime.now()

    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = datetime(2000, 1, 1)

    text = f"📊 <b>Прогресс</b>\n\n"
    kb = []

    today = now.strftime("%Y-%m-%d")

    # =========================
    # 🔁 ПРИВЫЧКИ
    # =========================
    for h in habits:
        hid, name, days, h_type, time, task_type, reminder = h

        if task_type == "task":
            continue

        if mode == "personal" and h_type != "personal":
            continue
        if mode == "family" and h_type != "family":
            continue

        order = {day: i for i, day in enumerate(DAYS)}

        days_list = [d for d in days.split(",") if d]
        days_list = sorted(days_list, key=lambda x: order[x])

        active_users = [c.from_user.id] if h_type == "personal" else users

        user_logs = {}
        for uid in active_users:
            logs = get_habit_logs(hid, uid)

            log_map = {}
            for l in logs:
                date_str = l[0].split("_")[0]
                date = datetime.strptime(date_str, "%Y-%m-%d")

                if date >= start_date:
                    log_map[l[0]] = l[1]

            user_logs[uid] = log_map

        labels_line = ""
        for i, d in enumerate(days_list):
            labels_line += d + " "
            if i == 2:
                labels_line += " "
        labels_line = labels_line.strip()

        if h_type == "personal":
            bar_line = ""

            for d in days_list:
                key = today + "_" + d
                log_map = user_logs.get(c.from_user.id, {})

                if key in log_map:
                    if log_map[key] == "done":
                        block = get_user_color(c.from_user.id)
                    elif log_map[key] == "skip":
                        block = "🟥"
                else:
                    block = "⬜"

                bar_line += block + " "

            bar_line = bar_line.strip()

        else:
            rows = []

            for uid in active_users:
                row = ""
                log_map = user_logs.get(uid, {})

                for d in days_list:
                    key = today + "_" + d

                    if key in log_map:
                        if log_map[key] == "done":
                            block = get_user_color(uid)
                        elif log_map[key] == "skip":
                            block = "🟥"
                    else:
                        block = "⬜"

                    row += block + " "

                rows.append(row.strip())

            bar_line = "\n".join(rows)

        title = f"{name} ({time})" if time else name

        text += (
            f"🔹 <b><i>{title}</i></b>\n"
            f"<code>{labels_line}</code>\n"
            f"<code>{bar_line}</code>\n"
            f"───────────────\n"
        )

    # =========================
    # 📝 ЗАДАЧИ (ФИКС)
    # =========================
    tasks = [h for h in habits if h[5] == "task"]

    if tasks:
        text += "\n📝 <b>Задачи:</b>\n\n"

        for h in tasks:
            hid, name, date, h_type, time, task_type, reminder = h

            logs = get_habit_logs(hid, c.from_user.id)

            filtered = []
            for d, s in logs:
                try:
                    dt = datetime.strptime(d, "%Y-%m-%d")
                    if dt >= start_date:
                        filtered.append((d, s))
                except:
                    continue

            done = any(s == "done" for _, s in filtered)

            # ===== ДАТА =====
            date_str = ""
            if date:
                try:
                    dt = datetime.strptime(date, "%Y-%m-%d")

                    if dt.year == datetime.now().year:
                        date_str = dt.strftime("%d.%m")
                    else:
                        date_str = dt.strftime("%d.%m.%Y")
                except:
                    date_str = date

            title = name

            if time:
                title += f" ({time})"

            if date_str:
                title += f" [{date_str}]"

            status = "✅" if done else "⏳"

            text += f"{title} {status}\n"

    # =========================
    # КНОПКИ
    # =========================
    if mode == "personal":
        kb.append([InlineKeyboardButton(text="👥 Общие", callback_data="progress_family")])
    else:
        kb.append([InlineKeyboardButton(text="👤 Личные", callback_data="progress_personal")])

    kb.append([
        InlineKeyboardButton(text="📅 Неделя", callback_data="prog_week"),
        InlineKeyboardButton(text="🗓 Месяц", callback_data="prog_month"),
        InlineKeyboardButton(text="📊 Всё", callback_data="prog_all")
    ])

    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="habits")])

    await c.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )
    
@dp.callback_query(F.data == "prog_week")
async def prog_week(c: CallbackQuery):
    mode = USER_MODE.get(c.from_user.id, "personal")
    await show_progress(c, mode=mode, period="week")


@dp.callback_query(F.data == "prog_month")
async def prog_month(c: CallbackQuery):
    mode = USER_MODE.get(c.from_user.id, "personal")
    await show_progress(c, mode=mode, period="month")


@dp.callback_query(F.data == "prog_all")
async def prog_all(c: CallbackQuery):
    mode = USER_MODE.get(c.from_user.id, "personal")
    await show_progress(c, mode=mode, period="all")   

@dp.callback_query(F.data == "progress_family")
async def progress_family(c: CallbackQuery):
    await show_progress(c, mode="family")


@dp.callback_query(F.data == "progress_personal")
async def progress_personal(c: CallbackQuery):
    await show_progress(c, mode="personal")

@dp.callback_query(F.data.startswith("skip_"))
async def habit_skip(c: CallbackQuery):
    _, hid, day = c.data.split("_")
    hid = int(hid)

    week_dates = get_current_week_dates()

    date_index = DAYS.index(day)
    date = week_dates[date_index]

    key = date + "_" + day

    logs = get_habit_logs(hid, c.from_user.id)

    for l in logs:
        if l[0] == key:
            await c.answer("Уже отмечено", show_alert=True)
            return

    add_habit_log(hid, c.from_user.id, key, "skip")

    await c.answer("❌ Пропущено")

    mode = USER_MODE.get(c.from_user.id, "personal")
    await show_my_habits(c, mode=mode)

@dp.callback_query(F.data.startswith("del_affirm_"))
async def delete_affirm(c: CallbackQuery):
    rowid = int(c.data.split("_")[2])

    cur.execute("DELETE FROM morning_affirmations WHERE rowid=?", (rowid,))
    conn.commit()

    await c.answer("Удалено")

    await delete_affirm_menu(c)

@dp.callback_query(F.data.startswith("del_visual_"))
async def delete_visual(c: CallbackQuery):
    pos = int(c.data.split("_")[2])

    # удаляем выбранную
    cur.execute("""
        DELETE FROM morning_visualization
        WHERE user_id=? AND position=?
    """, (c.from_user.id, pos))

    # 🔥 ПЕРЕНУМЕРАЦИЯ
    cur.execute("""
        SELECT rowid, position FROM morning_visualization
        WHERE user_id=?
        ORDER BY position
    """, (c.from_user.id,))
    rows = cur.fetchall()

    for new_pos, (rowid, _) in enumerate(rows, start=1):
        cur.execute("""
            UPDATE morning_visualization
            SET position=?
            WHERE rowid=?
        """, (new_pos, rowid))

    conn.commit()

    await c.answer("Удалено")

    await delete_visual_menu(c)

@dp.callback_query(F.data.startswith("del_"))
async def habit_delete(c: CallbackQuery):

    # ❗ ЖЕСТКО ПРОПУСКАЕМ НАШИ КЕЙСЫ
    if c.data.startswith("del_affirm_") or c.data.startswith("del_visual_"):
        return

    parts = c.data.split("_")

    if len(parts) < 2:
        return

    try:
        hid = int(parts[1])
    except:
        return

    delete_habit(hid)

    try:
        await c.answer("🗑 Удалено")
    except:
        pass

    mode = USER_MODE.get(c.from_user.id, "personal")
    await show_my_habits(c, mode=mode)

        
def reminder_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ За 10 мин", callback_data="rem_10")],
        [InlineKeyboardButton(text="⏰ За 15 мин", callback_data="rem_15")],
        [InlineKeyboardButton(text="⏰ За 30 мин", callback_data="rem_30")],
        [InlineKeyboardButton(text="⏰ За 1 час", callback_data="rem_60")],
        [InlineKeyboardButton(text="⏰ За 3 часа", callback_data="rem_180")],
        [InlineKeyboardButton(text="❌ Без напоминаний", callback_data="rem_skip")]
    ])
    
from datetime import datetime, timedelta

from database import cur

async def reminder_worker(bot: Bot):
    TIME_FIX = -60  # поправка сервера (в секундах)

    while True:
        try:
            cur.execute("""
                SELECT rowid, user_id, name, days, time, reminder, tz
                FROM habits
                WHERE time IS NOT NULL
            """)
            habits = cur.fetchall()

            for habit in habits:
                try:
                    rowid, user_id, name, days, time_str, reminder, tz = habit

                    if not time_str:
                        continue

                    # текущее время пользователя
                    user_now = datetime.utcnow() + timedelta(hours=tz)

                    # день недели
                    weekday_map = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                    today = weekday_map[user_now.weekday()]

                    if days:
                        if today not in days.split(","):
                            continue

                    # время привычки
                    hour, minute = map(int, time_str.split(":"))

                    habit_time = user_now.replace(
                        hour=hour,
                        minute=minute,
                        second=0,
                        microsecond=0
                    )

                    # время напоминания
                    if reminder is not None:
                        remind_time = habit_time - timedelta(minutes=reminder)
                    else:
                        remind_time = habit_time

                    diff = (user_now - remind_time).total_seconds() + TIME_FIX

                    day_key = remind_time.strftime("%Y-%m-%d_%H:%M")

                    if 0 <= diff <= 30 and not was_reminded_today(rowid, user_id, day_key):
                        await bot.send_message(
                            user_id,
                            f"⏰ Напоминание: {name}"
                        )

                        mark_reminded(rowid, user_id, day_key)

                except Exception as e:
                    print("REMINDER ERROR:", e)

        except Exception as e:
            print("WORKER ERROR:", e)

        await asyncio.sleep(1)  # ✅ ЭТО ПРАВИЛЬНО



        
@dp.callback_query(F.data.startswith("gender_"))
async def set_gender(c: CallbackQuery, state: FSMContext):
    await c.answer()

    gender = c.data.split("_")[1]
    await state.update_data(gender=gender)

    await state.set_state(StartStates.color)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟩", callback_data="color_🟩"),
            InlineKeyboardButton(text="🟦", callback_data="color_🟦"),
            InlineKeyboardButton(text="🟪", callback_data="color_🟪"),
            InlineKeyboardButton(text="🟧", callback_data="color_🟧"),
        ]
    ])

    text = (
        "🎨 Выбери цвет привычек:\n\n"
        "Пример как это будет выглядеть:\n\n"
        "🔹 СПОРТ ЗАЛ\n"
        "Пн Ср Пт\n"
        "🟩🟩⬜️"
    )

    try:
        await c.message.edit_text(text, reply_markup=kb)
    except:
        # 🔥 ЕСЛИ ТЕЛЕГРАМ РУГАЕТСЯ — ПРОСТО ШЛЁМ НОВОЕ
        await c.message.answer(text, reply_markup=kb)      

@dp.message(F.text == "⚙️ Settings")
async def settings_menu(m: Message):
    await m.answer(
        "⚙️ Settings",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🌍 Часовой пояс", callback_data="settings_tz"),
            ],
            [
                InlineKeyboardButton(text="🎨 Цвет", callback_data="set_color"),
                InlineKeyboardButton(text="✏️ Имя", callback_data="set_name"),
            ],
            # 🔥 НОВОЕ
            [
                InlineKeyboardButton(text="💡 Подсказки", callback_data="tips_settings")
            ]
        ])
    )

@dp.callback_query(F.data == "tips_settings")
async def tips_settings(c: CallbackQuery):
    cur.execute("SELECT tips FROM users WHERE id=?", (c.from_user.id,))
    res = cur.fetchone()
    enabled = res[0] if res else 1

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔴 Выключить" if enabled else "🟢 Включить",
            callback_data="toggle_tips"
        )]
    ])

    await c.message.edit_text(
        f"Подсказки: {'включены' if enabled else 'выключены'}",
        reply_markup=kb
    )




@dp.callback_query(F.data == "set_color")
async def change_color(c: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟩", callback_data="color_🟩"),
            InlineKeyboardButton(text="🟦", callback_data="color_🟦"),
            InlineKeyboardButton(text="🟪", callback_data="color_🟪"),
            InlineKeyboardButton(text="🟧", callback_data="color_🟧"),
        ]
    ])

    await c.message.answer("🎨 Выбери цвет:", reply_markup=kb)

@dp.callback_query(F.data == "settings_tz")
async def settings_timezone(c: CallbackQuery):
    await c.answer()

    await c.message.edit_text(
        "Выбери новый часовой пояс:",
        reply_markup=timezone_kb()
    )
   
@dp.message(F.text == "💎 Premium")
async def subscription_handler(m: Message):
    await m.answer(
        "Выбери функцию:",
        reply_markup=keyboards.subscription_menu()
    )

def productivity_settings_menu(user_id):
    cur.execute("""
        SELECT productivity_main, productivity_plan, productivity_priority
        FROM users WHERE id=?
    """, (user_id,))
    main, plan, priority = cur.fetchone()

    def mark(x):
        return "✅" if x else "❌"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"🏆 Главная задача {mark(main)}",
            callback_data="prod_toggle_main"
        )],
        [InlineKeyboardButton(
            text=f"📋 План дня {mark(plan)}",
            callback_data="prod_toggle_plan"
        )],
        [InlineKeyboardButton(
            text=f"⚡ Приоритеты {mark(priority)}",
            callback_data="prod_toggle_priority"
        )],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_sub")]
    ])

@dp.callback_query(F.data == "productivity_settings")
async def open_productivity_settings(c: CallbackQuery):
    await c.answer()

    try:
        await c.message.edit_text(
            "🎯 <b>Продуктивность</b>\n\nВключи нужные функции:",
            reply_markup=productivity_settings_menu(c.from_user.id),
            parse_mode="HTML"
        )
    except:
        await c.message.answer(
            "🎯 <b>Продуктивность</b>\n\nВключи нужные функции:",
            reply_markup=productivity_settings_menu(c.from_user.id),
            parse_mode="HTML"
        )

@dp.callback_query(F.data.startswith("prod_toggle_"))
async def toggle_productivity(c: CallbackQuery):
    field = c.data.replace("prod_toggle_", "")

    column = {
        "main": "productivity_main",
        "plan": "productivity_plan",
        "priority": "productivity_priority"
    }[field]

    cur.execute(f"""
        UPDATE users
        SET {column} = CASE WHEN {column}=1 THEN 0 ELSE 1 END
        WHERE id=?
    """, (c.from_user.id,))
    conn.commit()

    await c.message.edit_reply_markup(
        reply_markup=productivity_settings_menu(c.from_user.id)
    )

@dp.callback_query(F.data == "back_sub")
async def back_subscription(c: CallbackQuery):
    await c.message.answer(
        "Выбери функцию:",
        reply_markup=keyboards.subscription_menu()
    )


    
    
@dp.message(F.text == "💵 Финансы")
async def budget_menu_handler(message: Message):
    text = "💵 Финансы"

    if get_tips(message.from_user.id):
        text += (
            "\n\n💡Подсказка<blockquote>"
                "Здесь ты можешь управлять своими средствами:\n"
                "1)💸Добавлять расходы — просто отправь сообщение из банка или напиши сумму и категорию (например: 500 еда)\n"
                "2)💰Добавлять доходы — укажи сумму и выбери категорию\n"
                "3)📊Строить графики и контролировать баланс в аналитике\n"
                "4)↩️Отменить последние 5 операций\n"
                "5)📜*Если активирована Premium функция* можно управлять накоплениями\n\n"
                "Фишки:\n"
                "—🗄️Огромная база распознавания категорий\n"
                "—🤖Бот обучается под Вас\n"
                "—📜*Если активирована Premium функция*Предлагает откладывать 1/10"
                "</blockquote>"
        )

    await message.answer(
        text,
        reply_markup=keyboards.budget_menu(
            fin_enabled=is_fin_enabled(message.from_user.id)
        ),
        parse_mode="HTML"
    )

@dp.message(F.text == "📋 Привычки/Задачи")
async def habits_menu_handler(message: Message):
    text = "📋 Привычки/Задачи"

    if get_tips(message.from_user.id):
        text += (
            "\n\n💡Подсказка<blockquote>"
            "Создавай привычки и задачи:\n"
            "• 👥Личные и общие\n"
            "• 🗓Настраивай дни и время️\n"
            "• ⏰Добавляй напоминания\n\n"
            "Затем:\n"
            "— ✔Отмечай выполнение, нажав на название в меню управление\n"
            "— 🔎Смотри весь список за нелелю/месяц/все время в меню прогресс\n"
            "— 🔥Набирай стрик"
            "</blockquote>"
        )

    await message.answer(
        text,
        reply_markup=keyboards.habits_menu(),
        parse_mode="HTML"
    ) 
    
@dp.message(F.text == "📊 Аналитика")
async def open_stats(m: Message):
    text = get_stats_text(m.from_user.id)

    await m.answer(
        text,
        reply_markup=keyboards.stats_menu(),
        parse_mode="HTML"
    )
    


def get_stats_text(user_id):
    print("\n===== [TEXT ANALYTICS START] =====")

    family_id = get_family_id(user_id)

    # 🔥 если нет семьи → всегда персонально
    if not family_id:
        users = [user_id]
    else:
        # 🔥 главный источник истины
        if is_shared_finance(user_id):
            users = get_family_members(user_id)
        else:
            users = [user_id]

    if not users:
        users = [user_id]

    print(f"[DEBUG] FINAL users={users}")

    text = "📊 Аналитика\n\n"

    total_savings = 0
    total_percent = 0
    percent_count = 0

    for uid in users:
        profile = get_user_profile(uid)
        name = profile[0] if profile and profile[0] else f"id:{uid}"

        expenses = get_expense_stats(uid)
        income = get_income_stats(uid)

        total_expense = sum(x[1] for x in expenses) if expenses else 0
        total_income = sum(x[1] for x in income) if income else 0
        balance = total_income - total_expense

        savings_val = get_savings_balance(uid)
        total_savings += savings_val

        p = get_savings_percent(uid)
        if p > 0:
            total_percent += p
            percent_count += 1

        if len(users) > 1:
            text += f"👤 <b>{name}</b>\n"

        text += "💰 Доходы:\n"
        if income:
            for cat, amount in income:
                percent = int(amount / total_income * 100) if total_income else 0
                text += f"{cat} — {amount} ₽ ({percent}%)\n"
        else:
            text += "нет данных\n"

        text += "\n💸 Расходы:\n"
        if expenses:
            for cat, amount in expenses:
                percent = int(amount / total_expense * 100) if total_expense else 0
                text += f"{cat} — {amount} ₽ ({percent}%)\n"
        else:
            text += "нет данных\n"

        text += f"\n📈 Баланс: {balance} ₽"
        text += f"\nДоход: {total_income} ₽ | Расход: {total_expense} ₽"
        text += "\n\n───────────────\n\n"

    avg_percent = int(total_percent / percent_count) if percent_count else 0

    if is_fin_enabled(user_id):
        text += f"💰 Накопления — {total_savings} ₽\n\n"
        text += f"📊 Ты откладываешь: {avg_percent}%\n"

        if avg_percent == 0:
            text += "❌ Ты пока не платишь себе первым\n"
        elif avg_percent < 10:
            text += "⚠️ Ниже нормы\n"
        elif avg_percent < 15:
            text += "👍 Хорошо\n"
        else:
            text += "🔥 Отлично\n"

        text += "\n\n💡 Сначала заплати себе, потом всем остальным"

    return text






@dp.message(StartStates.name)
async def set_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    await state.set_state(StartStates.timezone)

    await m.answer(
        "Выбери время относительно МСК:",
        reply_markup=timezone_kb()
    )


async def finance_notifications_worker(bot: Bot):
    import asyncio
    from datetime import datetime, timedelta

    last_sent = {}

    while True:
        try:
            cur.execute("SELECT id, tz FROM users")
            users = cur.fetchall()

            for user_id, tz in users:
                now = datetime.utcnow() + timedelta(hours=tz)

                if now.weekday() == 0 and now.hour == 0:
                    key = f"{user_id}_{now.date()}"

                    if last_sent.get(user_id) == key:
                        continue

                    savings, percent = get_total_savings(user_id)

                    if percent == 0:
                        text = (
                            "💰 Финансовая система\n\n"
                            "«Часть того, что ты зарабатываешь,\nпринадлежит тебе»\n\n"
                            "Но сейчас ты не откладываешь ничего\n\n"
                            "Начни хотя бы с малого — 5–10%"
                        )
                    elif percent < 10:
                        text = "Ты начал платить себе,\nно пока меньше нормы\n\n10% — это база"
                    elif percent < 15:
                        text = "Ты платишь себе первым\n\nЭто фундамент роста"
                    else:
                        text = "Ты создаёшь капитал быстрее большинства\n\nДеньги начинают работать на тебя"

                    await bot.send_message(user_id, text)

                    last_sent[user_id] = key

        except Exception as e:
            print("FIN WORKER ERROR:", e)

        await asyncio.sleep(60)
    
@dp.callback_query(F.data.startswith("color_"))
async def set_color_callback(c: CallbackQuery, state: FSMContext):
    color = c.data.split("_")[1]
    data = await state.get_data()

    # =========================
    # 🔥 СТАРТ
    # =========================
    if "name" in data:
        gender = data.get("gender")

        cur.execute("""
            UPDATE users
            SET name=?, timezone=?, color=?, gender=?
            WHERE id=?
        """, (data["name"], data["timezone"], color, gender, c.from_user.id))
        conn.commit()

        await state.clear()

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="tips_on"),
                InlineKeyboardButton(text="❌ Нет", callback_data="tips_off")
            ]
        ])

        await c.message.answer(
            "🎉 Уже почти всё готово!\n\n"
            "Остался один небольшой вопрос 💡\n"
            "Нужны ли тебе подсказки?\n\n"
            "Если ты здесь впервые — рекомендую включить их.\n\n"
            "Позже ты сможешь отключить подсказки в настройках, а ответы всегда найдёшь в разделе ❓ FAQ.\n",
            reply_markup=kb
        )
        return

    # =========================
    # 🔥 НАСТРОЙКИ (OK)
    # =========================
    cur.execute("""
        UPDATE users
        SET color=?
        WHERE id=?
    """, (color, c.from_user.id))
    conn.commit()

    await c.answer("Цвет обновлён")

    try:
        await c.message.delete()
    except:
        pass

    await c.message.answer(
        "⚙️ Настройки",
        reply_markup=keyboards.settings_menu()
    )

def set_tips(user_id, value):
    cur.execute("UPDATE users SET tips=? WHERE id=?", (value, user_id))
    conn.commit()


def get_tips(user_id):
    cur.execute("SELECT tips FROM users WHERE id=?", (user_id,))
    res = cur.fetchone()
    return res[0] if res else 1


@dp.callback_query(F.data == "toggle_tips")
async def toggle_tips_handler(c: CallbackQuery):
    current = get_tips(c.from_user.id)
    set_tips(c.from_user.id, 0 if current else 1)

    enabled = get_tips(c.from_user.id)

    await c.answer("Обновлено")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔴 Выключить" if enabled else "🟢 Включить",
            callback_data="toggle_tips"
        )]
    ])

    text = f"Подсказки: {'включены' if enabled else 'выключены'}"

    # ❗ ГАРАНТИРОВАННОЕ ОБНОВЛЕНИЕ UI
    try:
        await c.message.delete()
    except:
        pass

    await c.message.answer(text, reply_markup=kb)


   
    

  
async def weekly_reset_worker():
    from datetime import datetime, timedelta
    import asyncio

    last_reset = {}

    while True:
        try:
            cur.execute("""
                SELECT DISTINCT user_id, tz
                FROM habits
            """)
            users = cur.fetchall()

            for user_id, tz in users:
                try:
                    user_now = datetime.utcnow() + timedelta(hours=tz)

                    week_key = f"{user_id}_{user_now.strftime('%Y-%W')}"

                    if (
                        user_now.weekday() == 0
                        and user_now.hour == 0
                        and user_now.minute == 0
                    ):
                        if last_reset.get(user_id) != week_key:

                            print(f"✅ RESET for user {user_id}")

                            # 🔥 ВОТ ЧТО НУЖНО
                            cur.execute("""
                                DELETE FROM habit_logs
                                WHERE user_id=?
                            """, (user_id,))
                            conn.commit()

                            last_reset[user_id] = week_key

                except Exception as e:
                    print("USER RESET ERROR:", e)

        except Exception as e:
            print("WEEKLY WORKER ERROR:", e)

        await asyncio.sleep(30)   
    
# =========================
# СЕМЬЯ
# =========================

from aiogram.fsm.state import State, StatesGroup

class FamilyStates(StatesGroup):
    create_name = State()
    create_password = State()
    join_code = State()
    join_password = State()
    rename_name = State()  # 🔥 НОВЫЙ


@dp.message(F.text == "👥 Семья")
async def family_menu(m: Message):
    family_id = get_family_id(m.from_user.id)

    if not family_id:
        text = "Ты не в семье"

        cur.execute("SELECT tips FROM users WHERE id=?", (m.from_user.id,))
        tips = cur.fetchone()
        if tips and tips[0]:
            text += (
               "\n\n💡Подсказка<blockquote>"
               "Ты можешь создать семью или вступить:\n\n"
               "•👑Создатель задаёт имя, пароль\n"
               "и выбирает общий или личный бюджет\n"
               "Затем делится кодом\n\n"
               "•♟️Участник:\n"
               "— Нажимает «Вступить»\n"
               "— Вводит код и пароль"
               "</blockquote>"
            )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать семью", callback_data="create_family")],
            [InlineKeyboardButton(text="🔗 Вступить", callback_data="join_family")]
        ])

        await m.answer(
            text,
            reply_markup=kb,
            parse_mode="HTML"
        )

    else:
        name = get_family_name(family_id)
        members = get_family_members(m.from_user.id)

        members_text = ""
        for uid in members:
            profile = get_user_profile(uid)
            uname = profile[0] if profile else f"id:{uid}"
            members_text += f"• <b>{uname}</b>\n"

        kb = [
            [InlineKeyboardButton(text="📎 Мой код", callback_data="family_code")],
            [InlineKeyboardButton(text="🚪 Выйти", callback_data="leave_family")]
        ]

        if is_family_owner(m.from_user.id, family_id):
            kb.insert(0, [InlineKeyboardButton(text="✏️ Переименовать", callback_data="rename_family")])
            kb.insert(1, [InlineKeyboardButton(text="💰 Режим Финансов", callback_data="family_fin_mode")])

        text = (
            f"Ты в семье: <b>{name}</b>\n\n"
            f"Участники:\n{members_text}"
        )

        cur.execute("SELECT tips FROM users WHERE id=?", (m.from_user.id,))
        tips = cur.fetchone()
        if tips and tips[0]:
            text += (
                "\n\n💡Подсказка<blockquote>"
                "💵Если включены общие финансы — баланс общий.\n"
                "📋Общие привычки доступны всегда!"
                "</blockquote>"
            )

        await m.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
            parse_mode="HTML"
        )

InlineKeyboardButton(text="✏️ Имя", callback_data="set_name")

@dp.callback_query(F.data.in_(["family_fin_on", "family_fin_off"]))
async def create_family_finish(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    shared = 1 if c.data == "family_fin_on" else 0

    fid = create_family(
        c.from_user.id,
        data["name"],
        data["password"],
        shared
    )

    await state.clear()

    await c.message.answer(
        f"Семья создана: <b>{data['name']}</b>\n\nКод семьи:\n<code>{fid}</code>",
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "family_fin_mode")
async def family_fin_mode(c: CallbackQuery):
    family_id = get_family_id(c.from_user.id)

    cur.execute(
        "SELECT shared_finance FROM families WHERE family_id=?",
        (family_id,)
    )
    row = cur.fetchone()
    enabled = row[0] if row else 0

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔴 Выключить" if enabled else "🟢 Включить",
            callback_data="toggle_family_fin"
        )]
    ])

    await c.message.edit_text(
        f"Финансы: {'общие' if enabled else 'раздельные'}",
        reply_markup=kb
    )


@dp.callback_query(F.data == "toggle_family_fin")
async def toggle_family_fin(c: CallbackQuery):
    family_id = get_family_id(c.from_user.id)

    if not family_id:
        return await c.answer("Ошибка")

    if not is_family_owner(c.from_user.id, family_id):
        return await c.answer("Только создатель", show_alert=True)

    cur.execute(
        "SELECT shared_finance FROM families WHERE family_id=?",
        (family_id,)
    )
    current = cur.fetchone()[0]

    new_val = 0 if current else 1

    cur.execute(
        "UPDATE families SET shared_finance=? WHERE family_id=?",
        (new_val, family_id)
    )
    conn.commit()

    await c.answer("Обновлено")
    await family_fin_mode(c)



class SettingsStates(StatesGroup):
    change_name = State()
    
@dp.callback_query(F.data == "set_name")
async def change_name(c: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.change_name)
    await c.message.answer("Введи новое имя")







# -------- СОЗДАНИЕ --------

@dp.callback_query(F.data == "create_family")
async def create_family_start(c: CallbackQuery, state: FSMContext):
    await state.set_state(FamilyStates.create_name)
    await c.message.answer("Введи название семьи")


@dp.message(FamilyStates.create_name)
async def create_family_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    await state.set_state(FamilyStates.create_password)
    await m.answer("Придумай пароль для семьи")


@dp.message(FamilyStates.create_password)
async def create_family_password(m: Message, state: FSMContext):
    await state.update_data(password=m.text.strip())

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Общие", callback_data="family_fin_on"),
            InlineKeyboardButton(text="👤 Раздельные", callback_data="family_fin_off")
        ]
    ])

    await m.answer("Сделать финансы общими?", reply_markup=kb)
    
@dp.callback_query(F.data.in_(["family_fin_on", "family_fin_off"]))
async def create_family_finish(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    shared = 1 if c.data == "family_fin_on" else 0

    fid = create_family(
        c.from_user.id,
        data["name"],
        data["password"],
        shared
    )

    await state.clear()

    await c.message.answer(
        f"Семья создана: <b>{data['name']}</b>\n\nКод семьи:\n<code>{fid}</code>",
        parse_mode="HTML"
    )

    await c.message.answer(
        "👥 Меню семьи",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📎 Мой код", callback_data="family_code")],
            [InlineKeyboardButton(text="🚪 Выйти", callback_data="leave_family")]
        ])
    )   
    
@dp.callback_query(F.data == "rename_family")
async def rename_family_start(c: CallbackQuery, state: FSMContext):
    await state.set_state(FamilyStates.rename_name)
    await c.message.answer("Введи новое название семьи")


@dp.message(FamilyStates.rename_name)
async def rename_family_name(m: Message, state: FSMContext):
    family_id = get_family_id(m.from_user.id)

    if not family_id:
        await m.answer("❌ Ты не в семье")
        return

    if not is_family_owner(m.from_user.id, family_id):
        await m.answer("❌ Только создатель может менять название")
        return

    cur.execute(
        "UPDATE families SET name=? WHERE family_id=?",
        (m.text, family_id)
    )
    conn.commit()

    await state.clear()
    await m.answer("✅ Название обновлено")  


# ------- ВСТУПЛЕНИЕ -------

@dp.callback_query(F.data == "join_family")
async def join_family_start(c: CallbackQuery, state: FSMContext):
    await state.set_state(FamilyStates.join_code)
    await c.message.answer("Введи код семьи")


@dp.message(FamilyStates.join_code)
async def join_family_code(m: Message, state: FSMContext):
    await state.update_data(code=m.text.strip())
    await state.set_state(FamilyStates.join_password)
    await m.answer("Введи пароль")


@dp.message(FamilyStates.join_password)
async def join_family_password(m: Message, state: FSMContext):
    data = await state.get_data()

    success, name = join_family(
        m.from_user.id,
        data["code"],
        m.text.strip()
    )

    await state.clear()

    if success:
        # 🔥 ПОЛУЧАЕМ ID СЕМЬИ
        family_id = get_family_id(m.from_user.id)

        # 🔥 НАХОДИМ СОЗДАТЕЛЯ (owner)
        cur.execute("""
            SELECT id FROM users
            WHERE family_id=? 
            ORDER BY id
            LIMIT 1
        """, (family_id,))
        owner = cur.fetchone()

        if owner:
            owner_id = owner[0]

            # 🔥 БЕРЕМ РЕЖИМ ОТ СОЗДАТЕЛЯ
            cur.execute(
                "SELECT shared_finance FROM users WHERE id=?",
                (owner_id,)
            )
            res = cur.fetchone()
            shared = res[0] if res else 0
        else:
            shared = 0  # fallback

        # 🔥 ПРИМЕНЯЕМ К НОВОМУ УЧАСТНИКУ
        cur.execute(
            "UPDATE users SET shared_finance=? WHERE id=?",
            (shared, m.from_user.id)
        )
        conn.commit()

        await m.answer(
            f"Добро пожаловать в семью: <b>{name}</b>",
            parse_mode="HTML"
        )
    else:
        await m.answer("Неверный код или пароль")


# -------- ПРОЧЕЕ --------

@dp.callback_query(F.data == "family_code")
async def show_code(c: CallbackQuery):
    fid = get_family_id(c.from_user.id)

    await c.message.answer(
        f"Код семьи:\n<code>{fid}</code>",
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "leave_family")
async def leave_family_handler(c: CallbackQuery):
    leave_family(c.from_user.id)

    await c.message.answer(
        "Ты вышел из семьи",
        reply_markup=keyboards.get_main_menu()
    )
    
# =========================
# НАСТРОЙКИ
# =========================    
    

# =========================
# СТАРТ
# =========================

@dp.message(CommandStart())
async def start(m: Message, state: FSMContext):
    user_id = m.from_user.id
    user = get_user_profile(user_id)

    # 🔥 ЕСЛИ УЖЕ ЕСТЬ — ПРОСТО В МЕНЮ
    if user and user[0]:
        await state.clear()
        await m.answer(
            "🏠 Главное меню",
            reply_markup=keyboards.get_main_menu()
        )
        return

    # 🔥 ЕСЛИ НОВЫЙ — ВСЁ КАК БЫЛО
    add_user(user_id, m.from_user.first_name)

    # 🔥 ВОТ ЭТО ТВОЯ СТРОКА (ПРАВИЛЬНОЕ МЕСТО)
    add_keyboard_layout_rules(user_id)

    await state.set_state(StartStates.name)

    await m.answer(
        "👋 Добро пожаловать!\n\n"
        "Этот бот поможет тебе:\n"
        "— контролировать финансы\n"
        "— внедрять привычки\n"
        "— работать вместе с семьёй\n\n"
        "Как тебя назвать?"
    )


@dp.message(F.text.startswith("-"))
async def remove_money(m: Message):
    try:
        amount = int(m.text.replace("-", "").strip())
        remove_savings(m.from_user.id, amount)
        await m.answer(f"❌ Снято {amount} ₽ с накоплений")
    except:
        await m.answer("Ошибка")



import asyncio
from datetime import datetime


# =========================
# TIMER
# =========================
async def return_to_active_timer(c: CallbackQuery):
    if c.from_user.id in ACTIVE_TIMERS:
        chat_id, message_id = ACTIVE_TIMERS[c.from_user.id]

        # ❌ НЕ УДАЛЯЕМ СООБЩЕНИЕ
        # await c.message.delete()

        try:
            # 👉 просто убираем кнопки у текущего меню
            await c.message.edit_reply_markup(reply_markup=None)
        except:
            pass

        try:
            # 👉 прокручиваем чат к нужному сообщению (через ответ)
            await c.message.answer(
                "⏱ Таймер уже запущен ↑",
                reply_to_message_id=message_id
            )
        except:
            pass

        return True

    return False


async def start_morning_timer(bot, chat_id, message_id, duration, text, user_id):
    cur.execute("""
        SELECT file_id FROM morning_visualization
        WHERE user_id=?
        ORDER BY position
    """, (user_id,))
    images = [x[0] for x in cur.fetchall()]

    total = len(images)
    time_per_image = 30

    sent_photos = []

    ACTIVE_TIMERS[user_id] = (chat_id, message_id)

    lock_user_input(user_id)

    remaining = duration
    i = 0

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Запуск..."
        )
    except:
        pass

    while remaining > 0:
        if images:
            img = images[i % total]

            try:
                msg = await bot.send_photo(chat_id, img)
                sent_photos.append(msg.message_id)
            except:
                pass

        for _ in range(time_per_image):
            if remaining <= 0:
                break

            minutes = remaining // 60
            seconds = remaining % 60

            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"{text}\n\n⏱ Осталось: {minutes:02d}:{seconds:02d}"
                )
            except:
                pass

            await asyncio.sleep(1)
            remaining -= 1

        i += 1

    for mid in sent_photos:
        try:
            await bot.delete_message(chat_id, mid)
        except:
            pass

    try:
        await bot.delete_message(chat_id, message_id)
    except:
        pass

    unlock_user_input(user_id)

    try:
        await bot.send_message(chat_id, "✅ Выполнено")
    except:
        pass

    fake_call = type("obj", (), {
        "from_user": type("obj", (), {"id": user_id}),
        "message": type("obj", (), {"chat": type("obj", (), {"id": chat_id})})
    })

    try:
        await open_morning_menu(fake_call)
    except:
        pass

    ACTIVE_TIMERS.pop(user_id, None)


# =========================
# VISUALIZATION
# =========================
async def start_visualization(bot, chat_id, user_id, duration):
    cur.execute("""
        SELECT file_id FROM morning_visualization
        WHERE user_id=?
        ORDER BY position
    """, (user_id,))
    images = [x[0] for x in cur.fetchall()]

    if not images:
        await bot.send_message(chat_id, "Нет изображений")
        return

    total = len(images)
    time_per_image = 30

    msg = await bot.send_message(chat_id, "Запуск...")

    ACTIVE_TIMERS[user_id] = (chat_id, msg.message_id)

    # ✅ ТОЛЬКО ЭТО
    lock_user_input(user_id)

    remaining = duration
    i = 0

    while remaining > 0:
        img = images[i % total]
        current_index = (i % total) + 1

        try:
            asyncio.create_task(bot.send_photo(chat_id, img))
        except:
            pass

        for _ in range(time_per_image):
            if remaining <= 0:
                break

            minutes = remaining // 60
            seconds = remaining % 60

            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg.message_id,
                    text=f"🧠 {current_index}/{total}\n\n⏱ Осталось: {minutes:02d}:{seconds:02d}"
                )
            except:
                pass

            await asyncio.sleep(1)
            remaining -= 1

        i += 1

    try:
        await bot.delete_message(chat_id, msg.message_id)
    except:
        pass

    # ✅ РАЗБЛОК
    unlock_user_input(user_id)

    await bot.send_message(chat_id, "✅ Выполнено")

    fake_call = type("obj", (), {
        "from_user": type("obj", (), {"id": user_id}),
        "message": type("obj", (), {"chat": type("obj", (), {"id": chat_id})})
    })

    try:
        await open_morning_menu(fake_call)
    except:
        pass

    ACTIVE_TIMERS.pop(user_id, None)


# =========================
# SERVICE
# =========================
from middlewaresblock_conflict import LOCKED_USERS

def lock_user_input(user_id):
    LOCKED_USERS.add(user_id)

def unlock_user_input(user_id):
    LOCKED_USERS.discard(user_id)

def is_user_locked(user_id):
    return user_id in LOCKED_USERS

def is_morning_enabled(user_id):
    cur.execute("SELECT morning_enabled FROM users WHERE id=?", (user_id,))
    res = cur.fetchone()
    return res and res[0] == 1


async def finish_step_and_return(c, step):
    date = datetime.now().strftime("%Y-%m-%d")

    complete_morning_step(c.from_user.id, step, date)

    try:
        await c.answer("✅ Выполнено")
    except:
        pass

    await open_morning_menu(c)


# =========================
# MAIN MENU
# =========================
MORNING_TEXT = """🌅 Магия утра

Начни день осознанно и с контролем.

Перед сном задай намерение на утро.
Проснись сразу — без "ещё 5 минут".
Встань с кровати, выпей воды, приведи себя в порядок.
Подготовь тело к движению.

Утро — это фундамент всего дня.

Хэл Элрод в своей книге "Машия Утра" 
рекомендует выполнять 6 практик каждое утро:

1. 🧘 Тишина — очистить разум  
2. 💬 Аффирмации — задать мышление  
3. 🧠 Визуализация — увидеть цель  
4. 🏃 Физические упражнения — включить тело  
5. 📖 Чтение — развивать себя  
6. 🤖 Планирование — задать день  

Выбери шаг и начни."""


@dp.callback_query(lambda c: c.data == "morning_menu")
async def open_morning_menu(call: CallbackQuery):
    cur.execute("SELECT morning_enabled FROM users WHERE id=?", (call.from_user.id,))
    res = cur.fetchone()

    enabled = res[0] if res else 0

    progress = get_morning_progress(call.from_user.id)

    text = MORNING_TEXT

    if enabled:
        text += f"\n\n📊 Прогресс:\n\n{progress}"

    try:
        await call.message.edit_text(
            text,
            reply_markup=morning_menu_kb(enabled)
        )
    except:
        await call.message.answer(
            text,
            reply_markup=morning_menu_kb(enabled)
        )


@dp.callback_query(lambda c: c.data == "toggle_morning")
async def toggle_morning_handler(call: CallbackQuery):
    toggle_morning(call.from_user.id)

    await call.answer("Обновлено")

    try:
        await call.message.delete()
    except:
        pass

    fake_call = type("obj", (), {
        "from_user": call.from_user,
        "message": await call.bot.send_message(call.from_user.id, "🌅 Магия утра")
    })

    await open_morning_menu(fake_call)


# =========================
# STEP 1 — ТИШИНА
# =========================
@dp.callback_query(F.data == "m_step_1")
async def silence_menu(c: CallbackQuery):
    if not is_morning_enabled(c.from_user.id):
        return await c.answer("Функция выключена", show_alert=True)

    if await return_to_active_timer(c):
        return

    text = """🧘 Тишина

Покинь спальню, сядь удобно, но не слишком расслабленно.

Сконцентрируйся на дыхании:
вдох — пауза — выдох — пауза.

Дыши медленно и глубоко, лучше животом.

Мысли будут — это нормально.
Просто возвращай внимание к дыханию.

Твоя задача — очистить разум и успокоиться."""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать", callback_data="start_silence")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="morning_menu")]
    ])

    await c.message.edit_text(text, reply_markup=kb)


@dp.callback_query(F.data == "start_silence")
async def start_silence(c: CallbackQuery):
    user_id = c.from_user.id

    # 🔥 БЛОК ПОВТОРНОГО ЗАПУСКА
    if user_id in ACTIVE_TIMERS:
        await c.answer("Уже запущено", show_alert=True)
        return

    msg = await c.message.answer("Запуск...")

    asyncio.create_task(
        start_morning_timer(
            bot=bot,
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            duration=300,
            text="🤫 Тишина",
            user_id=user_id
        )
    )


# =========================
# STEP 2 — АФФИРМАЦИИ
# =========================
@dp.callback_query(F.data == "m_step_2")
async def affirm_menu(c: CallbackQuery):
    if not is_morning_enabled(c.from_user.id):
        return await c.answer("Функция выключена", show_alert=True)

    if await return_to_active_timer(c):
        return

    text = """💬 Аффирмации

Ты программируешь своё мышление словами.

Определи:
— чего ты хочешь
— зачем тебе это
— каким человеком нужно стать

Формулируй коротко и чётко.
Читай вслух с эмоцией каждый день."""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать", callback_data="start_affirm")],
        [InlineKeyboardButton(text="➕ Добавить", callback_data="add_affirm")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_affirm")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="morning_menu")]
    ])

    await c.message.edit_text(text, reply_markup=kb)


@dp.callback_query(F.data == "start_affirm")
async def start_affirm(c: CallbackQuery):

    if await return_to_active_timer(c):
        return

    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")

    # 🔥 БЛОК ПОВТОРНОГО ВЫПОЛНЕНИЯ
    cur.execute("""
        SELECT 1 FROM morning_logs
        WHERE user_id=? AND step=2 AND date=? AND status=1
    """, (c.from_user.id, date))
    if cur.fetchone():
        return await c.answer("Уже выполнено", show_alert=True)

    cur.execute("SELECT text FROM morning_affirmations WHERE user_id=?", (c.from_user.id,))
    rows = cur.fetchall()

    if rows:
        lines = []
        for i, r in enumerate(rows, start=1):
            lines.append(f"{i}) {r[0]}")

        text = "💬 Аффирмации\n\n" + "\n".join(lines)
    else:
        text = "Добавь аффирмации"

    try:
        msg = await c.message.edit_text("Запуск...")
    except:
        msg = await c.message.answer("Запуск...")

    asyncio.create_task(
        start_morning_timer(
            c.bot,
            msg.chat.id,
            msg.message_id,
            300,
            text,
            c.from_user.id
        )
    )

    await finish_step_and_return(c, 2)


# =========================
# STEP 3 — ВИЗУАЛИЗАЦИЯ
# =========================
@dp.callback_query(F.data == "m_step_3")
async def visual_menu(c: CallbackQuery):
    if not is_morning_enabled(c.from_user.id):
        return await c.answer("Функция выключена", show_alert=True)

    if await return_to_active_timer(c):
        return

    text = """🧠 Визуализация

Посмотри на картинку, закрой глаза и представь свою идеальную жизнь.

Что ты видишь?
Что чувствуешь?
Кем ты стал?

Проживи это состояние внутри.

Чем ярче образ — тем сильнее мотивация действовать."""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать", callback_data="start_visual")],
        [InlineKeyboardButton(text="➕ Добавить картинку", callback_data="add_visual")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_visual")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="morning_menu")]
    ])

    await c.message.edit_text(text, reply_markup=kb)


@dp.callback_query(F.data == "start_visual")
async def start_visual(c: CallbackQuery):

    if await return_to_active_timer(c):
        return

    try:
        await c.message.edit_text("Запуск...")
    except:
        await c.message.answer("Запуск...")

    # 🔥 ЗАПУСКАЕМ ПРАВИЛЬНУЮ ЛОГИКУ
    asyncio.create_task(
        start_visualization(
            c.bot,
            c.message.chat.id,
            c.from_user.id,
            300  # 5 минут (как было)
        )
    )

    await finish_step_and_return(c, 3)


# =========================
# STEP 4 — ДВИЖЕНИЕ
# =========================
@dp.callback_query(F.data == "m_step_4")
async def move_menu(c: CallbackQuery):
    if not is_morning_enabled(c.from_user.id):
        return await c.answer("Функция выключена", show_alert=True)

    if await return_to_active_timer(c):
        return

    text = """🏃 Физические упражнения

Разбуди тело через движение.

Любая активность:
— зарядка
— бег
— растяжка
— йога
— спортзал

Главное — включить тело и энергию.

Начни с малого, но делай каждый день."""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать", callback_data="start_move")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="morning_menu")]
    ])

    await c.message.edit_text(text, reply_markup=kb)


@dp.callback_query(F.data == "start_move")
async def start_move(c: CallbackQuery):

    if await return_to_active_timer(c):
        return

    if c.from_user.id in ACTIVE_TIMERS:
        await c.answer("Уже запущено", show_alert=True)
        return

    try:
        msg = await c.message.edit_text("Запуск...")
    except:
        msg = await c.message.answer("Запуск...")

    asyncio.create_task(
        start_morning_timer(
            c.bot,
            msg.chat.id,
            msg.message_id,
            1200,
            "🏃 Движение",
            c.from_user.id
        )
    )

    await finish_step_and_return(c, 4)


# =========================
# STEP 5 — ЧТЕНИЕ
# =========================
@dp.callback_query(F.data == "m_step_5")
async def read_menu(c: CallbackQuery):
    if not is_morning_enabled(c.from_user.id):
        return await c.answer("Функция выключена", show_alert=True)

    if await return_to_active_timer(c):
        return

    cur.execute("""
        SELECT pages FROM reading_stats
        WHERE user_id=?
    """, (c.from_user.id,))
    res = cur.fetchone()

    total = res[0] if res else 0

    text = f"""📖 Чтение

Развивай себя каждый день.

Даже 10 страниц в день = десятки книг в год.

Читай с целью:
— что я возьму из этой книги?
— как применю?

📊 Прочитано всего: {total} стр."""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать", callback_data="start_read")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="morning_menu")]
    ])

    await c.message.edit_text(text, reply_markup=kb)


@dp.callback_query(F.data == "start_read")
async def start_read(c: CallbackQuery, state: FSMContext):

    if await return_to_active_timer(c):
        return

    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        SELECT 1 FROM morning_logs
        WHERE user_id=? AND step=5 AND date=? AND status=1
    """, (c.from_user.id, date))
    if cur.fetchone():
        return await c.answer("Уже выполнено", show_alert=True)

    try:
        msg = await c.message.edit_text("Запуск...")
    except:
        msg = await c.message.answer("Запуск...")

    user_id = c.from_user.id
    chat_id = msg.chat.id
    message_id = msg.message_id

    async def read_flow():
        # 🔒 БЛОКИРУЕМ ВВОД
        lock_user_input(user_id)

        await start_morning_timer(
            bot=c.bot,
            chat_id=chat_id,
            message_id=message_id,
            duration=30,
            text="📖 Чтение",
            user_id=user_id
        )

        # 🔓 РАЗБЛОК
        unlock_user_input(user_id)

        await c.bot.send_message(chat_id, "Сколько страниц прочитал?")

        # 🔥 ВКЛЮЧАЕМ ОЖИДАНИЕ
        await state.update_data(await_pages=True)

        # ⏱ ТАЙМАУТ 30 СЕК
        await asyncio.sleep(30)

        data = await state.get_data()
        if data.get("await_pages"):
            await state.update_data(await_pages=False)
            await c.bot.send_message(chat_id, "⏱ Время ввода истекло")

    asyncio.create_task(read_flow())

    await finish_step_and_return(c, 5)
    
@dp.message(StateFilter(None))
async def save_pages(m: Message, state: FSMContext):
    data = await state.get_data()

    current_state = await state.get_state()
    if current_state is not None:
        return

    if not data.get("await_pages"):
        return

    if not m.text.isdigit():
        await m.answer("Введи число")
        return

    pages = int(m.text)

    cur.execute("""
        INSERT INTO reading_stats(user_id, pages)
        VALUES(?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET pages = pages + ?
    """, (m.from_user.id, pages, pages))

    conn.commit()

    await state.update_data(await_pages=False)

    await m.answer(f"📊 Добавлено {pages} стр.")

# =========================
# STEP 6 — ПЛАНИРОВАНИЕ
# =========================
@dp.callback_query(F.data == "m_step_6")
async def plan_menu(c: CallbackQuery):
    if not is_morning_enabled(c.from_user.id):
        return await c.answer("Функция выключена", show_alert=True)

    # 🔥 ДОБАВИТЬ
    if await return_to_active_timer(c):
        return

    await c.message.edit_text(
        """🤖 Планирование дня

Не забудь:
— привычки
— финансы""",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Выполнено", callback_data="done_plan")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="morning_menu")]
        ])
    )


# =========================
# FAQ
# =========================
ADMIN_ID = -1003915437862


@dp.callback_query(F.data == "faq_guide")
async def faq_guide(c: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Финансы", callback_data="guide_finance")],
        [InlineKeyboardButton(text="📋 Привычки / Задачи", callback_data="guide_habits")],
        [InlineKeyboardButton(text="📊 Аналитика", callback_data="guide_stats")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq")]
    ])

    await c.message.edit_text(
        "📚 Инструкция\n\nВыбери раздел:",
        reply_markup=kb
    )
    await c.answer()

@dp.callback_query(F.data == "guide_finance")
async def guide_finance(c: CallbackQuery):
    await c.message.edit_text(
        "💵 Финансы\n\n"
        "— 💸 Расход → введи сумму и категорию\n"
        "Пример: 500 еда\n\n"
        "— 💰 Доход → добавь поступление\n\n"
        "— 🏛 Накопления (если включено)\n"
        "Позволяет откладывать деньги\n\n"
        "— ↩️ Отмена → удаление операций\n\n"
        "💡 Можно пересылать сообщения из банка — бот сам поймёт",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_guide")]
        ])
    )
    await c.answer()
     
    
@dp.callback_query(F.data == "guide_habits")
async def guide_habits(c: CallbackQuery):
    await c.message.edit_text(
        "📋 Привычки / Задачи\n\n"
        "— Создавай привычки\n"
        "— Отмечай выполнение\n"
        "— Следи за прогрессом\n\n"
        "💡 Помогает выработать дисциплину",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_guide")]
        ])
    )
    await c.answer()


    
@dp.callback_query(F.data == "guide_stats")
async def guide_stats(c: CallbackQuery):
    await c.message.edit_text(
        "📊 Аналитика\n\n"
        "— Смотри доходы и расходы\n"
        "— Анализируй баланс\n"
        "— Графики помогают понять траты\n\n"
        "💡 Основа финансового контроля",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_guide")]
        ])
    )
    await c.answer()
    
    
@dp.callback_query(F.data == "faq_premium")
async def faq_premium(c: CallbackQuery):
    await c.message.edit_text(
        "💎 Премиум функции\n\n"
        "🏛 Вавилон (накопления)\n"
        "— автоматически откладывает % от дохода\n\n"
        "🌅 Магия утра (скоро)\n"
        "— система утренних привычек\n\n"
        "🔥 Выход из зоны комфорта (скоро)\n"
        "— челленджи для роста\n\n"
        "💡 Эти функции ускоряют развитие",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq")]
        ])
    )
    await c.answer()

@dp.callback_query(F.data == "faq_video")
async def faq_video(c: CallbackQuery):
    await c.message.answer_video(
        video="BAACAgIAAxkBAAIO3GnaM384s8nV6g-bDTyNGCReIL53AAJBnQACGx7QSuIm_a755jB8OwQ",
        caption="🎥 Видео-гайд по приложению"
    )


  
class FeedbackState(StatesGroup):
    type = State()
    title = State()
    custom_title = State()  # 👈 НОВОЕ
    text = State()
    photo = State()  

def feedback_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐞 Баг", callback_data="fb_bug")],
        [InlineKeyboardButton(text="💡 Идея", callback_data="fb_idea")],
        [InlineKeyboardButton(text="❓ Вопрос", callback_data="fb_question")],
        [InlineKeyboardButton(text="⭐️ Отзыв", callback_data="fb_review")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq")]  # 👈 ДОБАВЬ
    ])

@dp.callback_query(F.data == "faq_feedback")
async def feedback_start(c: CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackState.type)

    await c.message.edit_text(
        "📩 Обратная связь\n\nВыбери тип обращения:",
        reply_markup=feedback_type_kb()
    )
    await c.answer()

@dp.callback_query(F.data.startswith("fb_"))
async def feedback_type(c: CallbackQuery, state: FSMContext):
    fb_type = c.data.replace("fb_", "")

    await state.update_data(type=fb_type)
    await state.set_state(FeedbackState.title)

    titles_map = {
        "bug": [
            ("Не работает кнопка", "title_btn"),
            ("Ошибка в тексте", "title_text"),
            ("Проблема с оплатой", "title_pay"),
        ],
        "idea": [
            ("Новая функция", "title_new"),
            ("Улучшение интерфейса", "title_ui"),
        ],
        "question": [
            ("Как работает функция", "title_how"),
            ("Где найти настройку", "title_where"),
        ],
        "review": [
            ("Все нравится", "title_good"),
            ("Есть замечания", "title_bad"),
        ]
    }

    buttons = titles_map.get(fb_type, [])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        *[[InlineKeyboardButton(text=text, callback_data=cb)] for text, cb in buttons],
        [InlineKeyboardButton(text="Другое", callback_data="title_other")]
    ])

    titles = {
        "bug": "🐞 Баг",
        "idea": "💡 Идея",
        "question": "❓ Вопрос",
        "review": "⭐ Отзыв"
    }

    await c.message.edit_text(
        f"{titles[fb_type]}\n\n📌 Шаг 1: Выбери заголовок:",
        reply_markup=kb
    )
    await c.answer()

@dp.callback_query(F.data.startswith("title_"))
async def feedback_title_choice(c: CallbackQuery, state: FSMContext):
    mapping = {
        "title_btn": "Не работает кнопка",
        "title_text": "Ошибка в тексте",
        "title_pay": "Проблема с оплатой",
        "title_new": "Новая функция",
        "title_ui": "Улучшение интерфейса",
        "title_how": "Как работает функция",
        "title_where": "Где найти настройку",
        "title_good": "Все нравится",
        "title_bad": "Есть замечания"
    }

    if c.data == "title_other":
        await state.set_state(FeedbackState.custom_title)

        await c.message.edit_text("📌 Введи свой заголовок:")
        await c.answer()
        return

    title = mapping.get(c.data)

    await state.update_data(title=title)
    await state.set_state(FeedbackState.text)

    await c.message.edit_text("📌 Шаг 2: ✍️ Опиши подробнее:")
    await c.answer()

@dp.message(FeedbackState.custom_title)
async def feedback_custom_title(m: Message, state: FSMContext):
    await state.update_data(title=m.text)
    await state.set_state(FeedbackState.text)

    await m.answer("📌 Шаг 2: ✍️ Опиши подробнее:")


@dp.message(FeedbackState.text)
async def feedback_text(m: Message, state: FSMContext):
    await state.update_data(text=m.text)
    await state.set_state(FeedbackState.photo)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_photo")]
    ])

    await m.answer("📌 Шаг 3: 📎 Пришли скрин или пропусти:", reply_markup=kb)

@dp.callback_query(F.data == "skip_photo", FeedbackState.photo)
async def skip_photo(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    username = f"@{c.from_user.username}" if c.from_user.username else "—"

    text = (
        "📩 Новое обращение\n\n"
        f"👤 ID: {c.from_user.id}\n"
        f"👤 Username: {username}\n\n"
        f"📂 Тип: {data.get('type')}\n"
        f"📌 Заголовок: {data.get('title')}\n\n"
        f"📝 Сообщение:\n{data.get('text')}"
    )

    await c.bot.send_message(ADMIN_ID, text)

    await c.message.edit_text("✅ Отправлено!")
    await state.clear()
    await c.answer()

@dp.message(FeedbackState.photo, F.photo)
async def feedback_photo(m: Message, state: FSMContext):
    data = await state.get_data()

    username = f"@{m.from_user.username}" if m.from_user.username else "—"

    caption = (
        "📩 Новое обращение\n\n"
        f"👤 ID: {m.from_user.id}\n"
        f"👤 Username: {username}\n\n"
        f"📂 Тип: {data.get('type')}\n"
        f"📌 Заголовок: {data.get('title')}\n\n"
        f"📝 Сообщение:\n{data.get('text')}"
    )

    await m.bot.send_photo(
        ADMIN_ID,
        photo=m.photo[-1].file_id,
        caption=caption
    )

    await m.answer("✅ Отправлено!")
    await state.clear()



# =========================
# ADD DATA
# =========================
@dp.callback_query(F.data == "add_affirm")
async def add_affirm(c: CallbackQuery, state: FSMContext):
    user_id = c.from_user.id

    # 🔒 БЛОКИРУЕМ
    lock_user_input(user_id)

    await c.message.answer("Введи аффирмацию:")
    await state.set_state("await_affirm")

    # ⏱ ТАЙМАУТ 30 СЕК
    async def timeout():
        await asyncio.sleep(30)

        current_state = await state.get_state()
        if current_state == "await_affirm":
            await state.clear()
            unlock_user_input(user_id)
            await c.message.answer("⏱ Время ввода истекло")

    asyncio.create_task(timeout())


@dp.message(StateFilter("await_affirm"))
async def save_affirm(m: Message, state: FSMContext):
    user_id = m.from_user.id

    text = m.text.strip()

    if not text:
        await m.answer("Пусто")
        return

    text = text[0].upper() + text[1:]

    while text and text[-1] in ".!?*,":  
        text = text[:-1]

    text += "."

    cur.execute(
        "INSERT INTO morning_affirmations VALUES(?,?)",
        (user_id, text)
    )
    conn.commit()

    # 🔓 РАЗБЛОК
    unlock_user_input(user_id)

    await state.clear()

    await m.answer("✅ Добавлено")

    fake_call = type("obj", (), {
        "from_user": m.from_user,
        "message": m
    })

    await affirm_menu(fake_call)

@dp.callback_query(F.data == "delete_affirm")
async def delete_affirm_menu(c: CallbackQuery):
    cur.execute("SELECT rowid, text FROM morning_affirmations WHERE user_id=?", (c.from_user.id,))
    rows = cur.fetchall()

    if not rows:
        return await c.answer("Нет аффирмаций", show_alert=True)

    text = "Выбери для удаления:\n\n"
    kb = []

    for i, row in enumerate(rows, start=1):
        text += f"{i}) {row[1]}\n"

        kb.append([
            InlineKeyboardButton(
                text=str(i),
                callback_data=f"del_affirm_{row[0]}"
            )
        ])

    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="m_step_2")])

    await c.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

@dp.callback_query(F.data == "add_visual")
async def add_visual(c: CallbackQuery, state: FSMContext):
    user_id = c.from_user.id

    # 🔒 БЛОК
    lock_user_input(user_id)

    await c.message.answer("Отправь картинку")
    await state.set_state("await_img")

    # ⏱ ТАЙМАУТ
    async def timeout():
        await asyncio.sleep(30)

        current_state = await state.get_state()
        if current_state == "await_img":
            await state.clear()
            unlock_user_input(user_id)
            await c.message.answer("⏱ Время вышло")

    asyncio.create_task(timeout())


@dp.message(StateFilter("await_img"))
async def save_img(m: Message, state: FSMContext):
    user_id = m.from_user.id

    if not m.photo:
        return

    data = await state.get_data()

    added = data.get("added_count", 0) + 1
    await state.update_data(added_count=added)

    cur.execute("""
        SELECT position FROM morning_visualization
        WHERE user_id=?
        ORDER BY position
    """, (user_id,))
    used = [x[0] for x in cur.fetchall()]

    position = 1
    while position in used:
        position += 1

    if position > 10:
        await m.answer("❌ Максимум 10 картинок")
        return

    file_id = m.photo[-1].file_id

    cur.execute(
        "INSERT INTO morning_visualization VALUES(?,?,?)",
        (user_id, file_id, position)
    )
    conn.commit()

    await m.answer(f"✅ Добавлено {position}/10")

    # 🔓 ВОТ ЭТО ДОБАВЬ
    unlock_user_input(user_id)

    if added == 1:
        fake_call = type("obj", (), {
            "from_user": m.from_user,
            "message": m
        })

        await visual_menu(fake_call)
 
@dp.callback_query(F.data == "delete_visual")
async def delete_visual_menu(c: CallbackQuery):
    cur.execute("""
        SELECT position FROM morning_visualization
        WHERE user_id=?
        ORDER BY position
    """, (c.from_user.id,))

    rows = [x[0] for x in cur.fetchall()]

    if not rows:
        return await c.answer("Нет картинок", show_alert=True)

    kb = []

    for pos in rows:
        kb.append([
            InlineKeyboardButton(
                text=f"❌ Удалить {pos}",
                callback_data=f"del_visual_{pos}"
            )
        ])

    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="m_step_3")])

    await c.message.edit_text("Выбери картинку:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)) 
 

ACTIVE_TIMERS = {}  # user_id: (chat_id, message_id)

def morning_menu_kb(enabled):
    kb = []

    kb.append([
        InlineKeyboardButton(
            text="🔘 Включить" if not enabled else "✅ Выключить",
            callback_data="toggle_morning"
        )
    ])

    if enabled:
        kb += [
            [InlineKeyboardButton(text="1. 🧘 Тишина", callback_data="m_step_1")],
            [InlineKeyboardButton(text="2. 💬 Аффирмации", callback_data="m_step_2")],
            [InlineKeyboardButton(text="3. 🧠 Визуализация", callback_data="m_step_3")],
            [InlineKeyboardButton(text="4. 🏃 Физические упражнения", callback_data="m_step_4")],
            [InlineKeyboardButton(text="5. 📖 Чтение", callback_data="m_step_5")],
            [InlineKeyboardButton(text="6. 🤖 Планирование", callback_data="m_step_6")],
        ]

    kb.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_sub")
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb)


async def main():
    asyncio.create_task(reminder_worker(bot))
    asyncio.create_task(weekly_reset_worker())
    asyncio.create_task(finance_notifications_worker(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())    

