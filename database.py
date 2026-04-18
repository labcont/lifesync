import sqlite3

conn = sqlite3.connect("data.db")
cur = conn.cursor()


# ✅ 1. СОЗДАЁМ ТАБЛИЦУ СРАЗУ С НУЖНЫМ ПОЛЕМ
cur.execute("""
CREATE TABLE IF NOT EXISTS families(
    family_id TEXT,
    name TEXT,
    password TEXT,
    shared_finance INTEGER DEFAULT 1
)
""")

conn.commit()







# =========================
# HABITS UPDATE (ДОБАВЛЕНО)
# =========================
def init_habits_update():
    # ===== HABITS =====
    try:
        cur.execute("ALTER TABLE habits ADD COLUMN type TEXT")
    except:
        pass

    try:
        cur.execute("ALTER TABLE habits ADD COLUMN time TEXT")
    except:
        pass

    try:
        cur.execute("ALTER TABLE habits ADD COLUMN task_type TEXT")
    except:
        pass

    try:
        cur.execute("ALTER TABLE habits ADD COLUMN family_id TEXT")
    except:
        pass

    try:
        cur.execute("ALTER TABLE habits ADD COLUMN reminder INTEGER")
    except:
        pass
        
    try:
        cur.execute("ALTER TABLE habits ADD COLUMN tz INTEGER DEFAULT 0")
    except:
        pass 
        
    try:
        cur.execute("ALTER TABLE users ADD COLUMN family_id INTEGER")
    except:
        pass 
    try:
        cur.execute("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT 'male'")
    except:
        pass        

    # ===== USERS =====
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        timezone INTEGER
    )
    """)

    # 🔥 ДОБАВЛЯЕМ НОВЫЕ ПОЛЯ БЕЗ ЛОМА
    try:
        cur.execute("ALTER TABLE users ADD COLUMN name TEXT")
    except:
        pass

    try:
        cur.execute("ALTER TABLE users ADD COLUMN color TEXT")
    except:
        pass

    # ===== PRODUCTIVITY (НОВОЕ) =====
    try:
        cur.execute("ALTER TABLE users ADD COLUMN productivity_main INTEGER DEFAULT 0")
    except:
        pass

    try:
        cur.execute("ALTER TABLE users ADD COLUMN productivity_plan INTEGER DEFAULT 0")
    except:
        pass

    try:
        cur.execute("ALTER TABLE users ADD COLUMN productivity_priority INTEGER DEFAULT 0")
    except:
        pass

    conn.commit()

    # ===== REMINDERS =====
    cur.execute("""
    CREATE TABLE IF NOT EXISTS habit_reminders(
        habit_id INTEGER,
        user_id INTEGER,
        day_key TEXT
    )
    """)

    conn.commit()

init_habits_update()

# =========================
# USERS UPDATE (НОВОЕ)
# =========================
def init_users_update():
    try:
        cur.execute("ALTER TABLE users ADD COLUMN shared_finance INTEGER DEFAULT 1")
    except:
        pass

    conn.commit()

init_users_update()


def add_savings_column():
    cur.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cur.fetchall()]

    if "savings" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN savings INTEGER DEFAULT 0")
        conn.commit()
     
def get_savings(user_id):
    return get_savings_balance(user_id)     
     
      

cur.execute("""CREATE TABLE IF NOT EXISTS transactions(
user_id INTEGER,
amount INTEGER,
type TEXT,
category TEXT
)""")


cur.execute("""
CREATE TABLE IF NOT EXISTS habits(
    user_id INTEGER,
    name TEXT,
    days TEXT,
    type TEXT,
    time TEXT,
    task_type TEXT,
    family_id TEXT,
    reminder INTEGER,
    tz INTEGER DEFAULT 0
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS family_members(
    user_id INTEGER,
    family_id TEXT
)
""")

cur.execute("""CREATE TABLE IF NOT EXISTS rules(
user_id INTEGER,
keyword TEXT,
category TEXT
)""")

conn.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS savings_logs(
    user_id INTEGER,
    family_id TEXT,
    amount INTEGER,
    type TEXT
)
""")

conn.commit()

def fix_savings_table():
    print("🔥 FIX SAVINGS TABLE")

    cur.execute("PRAGMA table_info(savings_logs)")
    columns = [col[1] for col in cur.fetchall()]

    if "family_id" not in columns:
        print("[FIX] adding family_id to savings_logs")

        cur.execute("ALTER TABLE savings_logs ADD COLUMN family_id TEXT")
        conn.commit()

fix_savings_table()

def add_transaction(uid, amount, t, cat):
    cur.execute(
        "INSERT INTO transactions VALUES(?,?,?,?)",
        (uid, amount, t, cat)
    )
    conn.commit()

def get_expense_stats(uid):
    print("\n[EXPENSE STATS]")

    # 🔥 твоя система пользователей (НЕ ЛОМАЕМ)
    users = resolve_users_for_analytics(uid)

    # 🔥 ВАЖНО: проверка раздельных финансов
    if not is_shared_finance(uid):
        print("[DEBUG] SEPARATE MODE → only self")
        users = [uid]

    if not users:
        print("[WARN] users empty → fallback")
        users = [uid]

    print(f"[DEBUG] FINAL users={users}")

    cur.execute(f"""
        SELECT category, SUM(amount)
        FROM transactions
        WHERE user_id IN ({",".join("?"*len(users))})
        AND type='expense'
        GROUP BY category
    """, users)

    result = cur.fetchall()

    print(f"[DEBUG] RESULT={result}")
    return result


def get_income_stats(uid):
    print("\n[INCOME STATS]")

    users = resolve_users_for_analytics(uid)

    # 🔥 ВАЖНО: раздельные финансы
    if not is_shared_finance(uid):
        print("[DEBUG] SEPARATE MODE → only self")
        users = [uid]

    if not users:
        print("[WARN] users empty → fallback")
        users = [uid]

    print(f"[DEBUG] FINAL users={users}")

    cur.execute(f"""
        SELECT category, SUM(amount)
        FROM transactions
        WHERE user_id IN ({",".join("?"*len(users))})
        AND type='income'
        GROUP BY category
    """, users)

    result = cur.fetchall()

    print(f"[DEBUG] RESULT={result}")
    return result


def get_category_breakdown(uid, t):
    print("\n[CATEGORY BREAKDOWN]")

    users = resolve_users_for_analytics(uid)

    if not users:
        print("[WARN] users empty → fallback")
        users = [uid]

    print(f"[DEBUG] users={users} | type={t}")

    cur.execute(f"""
        SELECT category, user_id, SUM(amount)
        FROM transactions
        WHERE user_id IN ({",".join("?"*len(users))})
        AND type=?
        GROUP BY category, user_id
    """, (*users, t))

    result = cur.fetchall()

    print(f"[DEBUG] RESULT={result}")
    return result


# СТАРОЕ (НЕ ЛОМАЕМ)
def get_stats(uid):
    return get_expense_stats(uid)


def add_rule(uid, keyword, category):
    cur.execute("INSERT INTO rules VALUES(?,?,?)",(uid, keyword, category))
    conn.commit()


def get_rules(uid):
    cur.execute("SELECT keyword, category FROM rules WHERE user_id=?", (uid,))
    return cur.fetchall()


# =========================
# HABITS V2 (НОВОЕ)
# =========================

cur.execute("""
CREATE TABLE IF NOT EXISTS habit_logs(
habit_id INTEGER,
user_id INTEGER,
date TEXT,
status TEXT
)
""")

conn.commit()


def add_habit(user_id, name, days, h_type, time, task_type, family_id=None, reminder=None, tz=0):
    if h_type == "family":
        family_id = get_family_id(user_id)

    cur.execute("""
        INSERT INTO habits (user_id, name, days, type, time, task_type, family_id, reminder, tz)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, days, h_type, time, task_type, family_id, reminder, tz))

    conn.commit()


def get_habits(user_id):
    family_id = get_family_id(user_id)

    if family_id:
        cur.execute("""
            SELECT rowid, name, days, type, time, task_type, reminder
            FROM habits
            WHERE user_id=? OR (family_id=? AND type='family')
        """, (user_id, family_id))
    else:
        cur.execute("""
            SELECT rowid, name, days, type, time, task_type, reminder
            FROM habits
            WHERE user_id=?
        """, (user_id,))

    return cur.fetchall()


def add_habit_log(habit_id, user_id, date, status):
    cur.execute("""
        INSERT INTO habit_logs VALUES(?,?,?,?)
    """, (habit_id, user_id, date, status))
    conn.commit()


def get_habit_logs(habit_id, user_id):
    cur.execute("""
        SELECT date, status FROM habit_logs
        WHERE habit_id=? AND user_id=?
    """, (habit_id, user_id))
    return cur.fetchall()


def delete_habit(habit_id):
    cur.execute("DELETE FROM habits WHERE rowid=?", (habit_id,))
    cur.execute("DELETE FROM habit_logs WHERE habit_id=?", (habit_id,))
    conn.commit()
    
    
def set_habit_reminder(habit_id, minutes_before):
    cur.execute("""
        UPDATE habits
        SET reminder = ?
        WHERE rowid = ?
    """, (minutes_before, habit_id))

    conn.commit()
    
def get_all_habits_with_time():
    cur.execute("""
        SELECT rowid, user_id, name, time, reminder
        FROM habits
        WHERE time IS NOT NULL AND reminder IS NOT NULL
    """)
    return cur.fetchall()
    
def was_reminded_today(habit_id, user_id, day_key):
    cur.execute("""
        SELECT 1 FROM habit_reminders
        WHERE habit_id=? AND user_id=? AND day_key=?
    """, (habit_id, user_id, day_key))
    return cur.fetchone() is not None


def mark_reminded(habit_id, user_id, day_key):
    cur.execute("""
        INSERT INTO habit_reminders (habit_id, user_id, day_key)
        VALUES (?, ?, ?)
    """, (habit_id, user_id, day_key))
    conn.commit()
    
def add_user(user_id, name="User", gender="male"):
    cur.execute("""
        INSERT OR IGNORE INTO users (id, name, gender)
        VALUES (?, ?, ?)
    """, (user_id, name, gender))


def get_user(user_id):
    cur.execute("SELECT id FROM users WHERE id=?", (user_id,))
    return cur.fetchone()


def save_user_timezone(user_id, tz):
    cur.execute("UPDATE users SET timezone=? WHERE id=?", (tz, user_id))
    conn.commit()


def get_user_timezone(user_id):
    cur.execute("SELECT timezone FROM users WHERE id=?", (user_id,))
    res = cur.fetchone()
    return res[0] if res else None    
    
# =========================
# 👥 FAMILY
# =========================

import uuid

def create_family(user_id, name, password, shared_finance):
    import uuid

    family_id = str(uuid.uuid4())[:6]

    try:
        shared_finance = int(shared_finance)
    except:
        shared_finance = 1 if str(shared_finance).lower() in ["true", "yes"] else 0

    cur.execute(
        "INSERT INTO families (family_id, name, password, shared_finance) VALUES (?, ?, ?, ?)",
        (family_id, name, password, shared_finance)
    )

    cur.execute(
        "INSERT INTO family_members VALUES (?, ?)",
        (user_id, family_id)
    )

    cur.execute(
        "UPDATE users SET family_id=?, shared_finance=? WHERE id=?",
        (family_id, shared_finance, user_id)
    )

    conn.commit()
    return family_id


def join_family(user_id, family_id, password):
    cur.execute(
        "SELECT name, password, shared_finance FROM families WHERE family_id=?",
        (family_id,)
    )
    res = cur.fetchone()

    if not res or res[1] != password:
        return False, None

    family_name = res[0]
    shared_finance = res[2]

    cur.execute("""
        SELECT 1 FROM family_members
        WHERE user_id=? AND family_id=?
    """, (user_id, family_id))

    if not cur.fetchone():
        cur.execute(
            "INSERT INTO family_members VALUES (?, ?)",
            (user_id, family_id)
        )

    cur.execute(
        "UPDATE users SET family_id=?, shared_finance=? WHERE id=?",
        (family_id, shared_finance, user_id)
    )

    conn.commit()

    return True, family_name


def get_family(user_id):
    cur.execute(
        """SELECT f.family_id, f.name
           FROM families f
           JOIN family_members m ON f.family_id = m.family_id
           WHERE m.user_id=?""",
        (user_id,)
    )
    return cur.fetchone()


def leave_family(user_id):
    cur.execute(
        "DELETE FROM family_members WHERE user_id=?",
        (user_id,)
    )

    # 🔥 ВАЖНО — убираем связь
    cur.execute(
        "UPDATE users SET family_id=NULL WHERE id=?",
        (user_id,)
    )

    conn.commit()


def get_family_members(user_id):
    cur.execute(
        "SELECT family_id FROM family_members WHERE user_id=?",
        (user_id,)
    )
    res = cur.fetchone()

    if not res:
        return [user_id]

    family_id = res[0]

    cur.execute(
        "SELECT user_id FROM family_members WHERE family_id=?",
        (family_id,)
    )
    return [x[0] for x in cur.fetchall()]
    
def set_user_profile(user_id, name, color, gender=None):
    if gender is None:
        cur.execute("""
            INSERT INTO users (id, name, color)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                color=excluded.color
        """, (user_id, name, color))
    else:
        cur.execute("""
            INSERT INTO users (id, name, color, gender)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                color=excluded.color,
                gender=excluded.gender
        """, (user_id, name, color, gender))

    conn.commit()


def get_user_profile(user_id):
    cur.execute("""
        SELECT name, timezone, color, gender FROM users WHERE id=?
    """, (user_id,))
    return cur.fetchone()    
    
import sqlite3

def ensure_family_column():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE users ADD COLUMN family_id INTEGER")
        conn.commit()
    except:
        pass

    conn.close()


def get_family_id(user_id):
    cur.execute("""
        SELECT family_id FROM family_members WHERE user_id=?
    """, (user_id,))
    
    res = cur.fetchone()
    return res[0] if res else None
   
ensure_family_column()   

def get_family_name(family_id):
    cur.execute("SELECT name FROM families WHERE family_id=?", (family_id,))
    row = cur.fetchone()
    return row[0] if row else "Без названия"
    
def is_family_owner(user_id, family_id):
    cur.execute("""
        SELECT user_id FROM family_members
        WHERE family_id=?
        ORDER BY rowid ASC
        LIMIT 1
    """, (family_id,))
    res = cur.fetchone()
    return res and res[0] == user_id


def rename_family(family_id, new_name):
    cur.execute("UPDATE families SET name=? WHERE family_id=?", (new_name, family_id))
    conn.commit()    
    
def set_gender(user_id, gender):
    cur.execute("UPDATE users SET gender=? WHERE id=?", (gender, user_id))
    conn.commit()    
    


# =========================
# 💰 SAVINGS (НОВАЯ СИСТЕМА)
# =========================

def resolve_users_for_analytics(user_id: int):
    print("===== [ANALYTICS RESOLVE START] =====")

    try:
        family_id = get_family_id(user_id)

        # 🔥 ЕСЛИ НЕТ СЕМЬИ → всегда персонально
        if not family_id:
            print("[DEBUG] NO FAMILY → PERSONAL MODE")
            return [user_id]

        shared = is_shared_finance(user_id)
        print(f"[DEBUG] shared_finance={shared}")

        # 🔥 ЕСЛИ РАЗДЕЛЬНЫЕ ФИНАНСЫ → только пользователь
        if not shared:
            print("[DEBUG] PERSONAL MODE")
            return [user_id]

        users = get_family_members(user_id)

        # защита от дублей
        users = list(set(users))

        print(f"[DEBUG] FAMILY USERS={users}")
        return users if users else [user_id]

    except Exception as e:
        print(f"[ERROR] resolve_users_for_analytics: {e}")
        return [user_id]


def withdraw_savings(user_id, amount):
    print("\n[WITHDRAW SAVINGS]")

    try:
        amount = int(amount)
    except:
        print("[ERROR] invalid amount")
        return False

    if amount <= 0:
        return False

    balance = get_savings_balance(user_id)

    if amount > balance:
        print("[ERROR] not enough money")
        return False

    family_id = get_family_id(user_id)
    mode = "shared" if is_shared_finance(user_id) else "separate"

    if mode == "shared" and family_id:
        cur.execute(
            "INSERT INTO savings_logs (user_id, family_id, amount, type) VALUES (?, ?, ?, ?)",
            (user_id, family_id, amount, "withdraw")
        )
    else:
        cur.execute(
            "INSERT INTO savings_logs (user_id, family_id, amount, type) VALUES (?, ?, ?, ?)",
            (user_id, None, amount, "withdraw")
        )

    conn.commit()
    print("[DEBUG] WITHDRAW DONE")
    return True
    
def add_savings(user_id, amount):
    print("\n[ADD SAVINGS]")

    try:
        amount = int(amount)
    except:
        print("[ERROR] amount invalid")
        return False

    if amount <= 0:
        print("[ERROR] amount <= 0")
        return False

    family_id = get_family_id(user_id)
    print(f"[DEBUG] family_id={family_id}")

    mode = "shared" if is_shared_finance(user_id) else "separate"
    print(f"[DEBUG] mode={mode}")

    if mode == "shared" and family_id:
        # 🔥 ПИШЕМ НА ВСЮ СЕМЬЮ
        cur.execute(
            "INSERT INTO savings_logs (user_id, family_id, amount, type) VALUES (?, ?, ?, ?)",
            (user_id, family_id, amount, "add")
        )
    else:
        # 🔥 SOLO
        cur.execute(
            "INSERT INTO savings_logs (user_id, family_id, amount, type) VALUES (?, ?, ?, ?)",
            (user_id, None, amount, "add")
        )

    conn.commit()
    print("[DEBUG] SAVINGS ADDED")
    return True    


def get_savings_balance(user_id):
    print("\n[SAVINGS BALANCE]")

    family_id = get_family_id(user_id)
    mode = "shared" if is_shared_finance(user_id) else "separate"

    print(f"[DEBUG] family_id={family_id}")
    print(f"[DEBUG] mode={mode}")

    # 🔥 FIX: если нет семьи → только персонально
    if not family_id:
        mode = "separate"

    if mode == "shared" and family_id:
        print("[DEBUG] USING FAMILY SAVINGS")

        cur.execute("""
            SELECT type, SUM(amount)
            FROM savings_logs
            WHERE family_id=?
            GROUP BY type
        """, (family_id,))
    else:
        print("[DEBUG] USING PERSONAL SAVINGS")

        cur.execute("""
            SELECT type, SUM(amount)
            FROM savings_logs
            WHERE user_id=? AND family_id IS NULL
            GROUP BY type
        """, (user_id,))

    data = cur.fetchall()
    print(f"[DEBUG] RAW DATA={data}")

    total_add = 0
    total_withdraw = 0

    for t, amount in data:
        if t == "add":
            total_add = amount or 0
        elif t == "withdraw":
            total_withdraw = amount or 0

    balance = total_add - total_withdraw

    print(f"[DEBUG] BALANCE={balance}")
    return balance


def get_total_income(user_id):
    print("\n[TOTAL INCOME]")

    users = resolve_users_for_analytics(user_id)

    if not users:
        users = [user_id]

    print(f"[DEBUG] users={users}")

    cur.execute(f"""
        SELECT SUM(amount)
        FROM transactions
        WHERE user_id IN ({",".join("?"*len(users))})
        AND type='income'
    """, users)

    res = cur.fetchone()

    total = res[0] if res and res[0] else 0

    print(f"[DEBUG] TOTAL={total}")
    return total


def get_savings_percent(user_id):
    savings = get_savings_balance(user_id)
    income = get_total_income(user_id)

    total = income + savings  # 🔥 ВАЖНО

    if total == 0:
        return 0

    return int((savings / total) * 100)


def fix_db():
    columns = [col[1] for col in cur.execute("PRAGMA table_info(users)").fetchall()]

    if "gender" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT 'male'")

    if "tz" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN tz INTEGER DEFAULT 0")

    if "savings" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN savings INTEGER DEFAULT 0")

    if "fin_enabled" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN fin_enabled INTEGER DEFAULT 0")

    conn.commit()
 
 
fix_db() 


import random

def get_motivation_text():
    texts = [
        "💡 Сначала заплати себе, потом всем остальным",
        "💰 Бедные тратят — богатые откладывают",
        "📈 10% сегодня = свобода завтра",
        "🔥 Контроль денег = контроль жизни"
    ]
    return random.choice(texts)
    
    
# =========================
# 🌅 MORNING MAGIC
# =========================

def init_morning_magic():
    ensure_morning_column()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS morning_logs(
        user_id INTEGER,
        step INTEGER,
        date TEXT,
        status INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS morning_affirmations(
        user_id INTEGER,
        text TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS morning_visualization(
        user_id INTEGER,
        file_id TEXT,
        position INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS morning_settings(
        user_id INTEGER,
        step INTEGER,
        duration INTEGER DEFAULT 300
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reading_stats (
        user_id INTEGER PRIMARY KEY,
        pages INTEGER DEFAULT 0
    )
    """)

    conn.commit()

def ensure_morning_column():
    cur.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cur.fetchall()]

    if "morning_enabled" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN morning_enabled INTEGER DEFAULT 0")
        conn.commit()

def toggle_morning(user_id):
    cur.execute("SELECT morning_enabled FROM users WHERE id=?", (user_id,))
    res = cur.fetchone()

    if not res:
        return False

    new_val = 0 if res[0] == 1 else 1

    cur.execute(
        "UPDATE users SET morning_enabled=? WHERE id=?",
        (new_val, user_id)
    )
    conn.commit()

    return new_val
    
def complete_morning_step(user_id, step, date):
    # удаляем старую запись (если есть)
    cur.execute("""
        DELETE FROM morning_logs
        WHERE user_id=? AND step=? AND date=?
    """, (user_id, step, date))

    # вставляем новую
    cur.execute("""
        INSERT INTO morning_logs (user_id, step, date, status)
        VALUES (?, ?, ?, ?)
    """, (user_id, step, date, 1))

    conn.commit()   
    
def get_morning_progress(user_id, date):
    cur.execute("""
        SELECT step FROM morning_logs
        WHERE user_id=? AND date=? AND status=1
    """, (user_id, date))

    done = [x[0] for x in cur.fetchall()]

    result = []
    for i in range(1, 7):
        if i in done:
            result.append("🟩")
        else:
            result.append("⬜")

    return "".join(result)    
    
def reset_morning_day(date):
    cur.execute("""
        DELETE FROM morning_logs WHERE date=?
    """, (date,))
    conn.commit()

def add_keyboard_layout_rules(user_id):
    layout_map = {
        "еда": ["tlf"],
        "транспорт": ["nhfy", "nhfycgjhn", "nhfy cgjhn"],
        "зп": ["pg"],
        "подарок": ["gjlfhjr"],
        "кешбек": ["rti,"],
        "дивиденды/вклады": ["lbdblytyls"]
    }

    for correct, wrong_list in layout_map.items():
        for wrong in wrong_list:
            variants = [
                wrong,
                wrong.lower(),
                wrong.upper(),
                wrong.capitalize()
            ]

            for variant in variants:
                cur.execute(
                    "INSERT OR IGNORE INTO rules VALUES(?,?,?)",
                    (user_id, variant.strip().lower(), correct.capitalize())
                )

    conn.commit()
# =========================
# 🚀 ЗАПУСК ИНИЦИАЛИЗАЦИИ
# =========================

init_morning_magic()    

def init_tips_column():
    try:
        cur.execute("ALTER TABLE users ADD COLUMN tips INTEGER DEFAULT 1")
    except:
        pass
    conn.commit()

init_tips_column()

# =========================
# 🚀 СЕМЬЯ КАЧ
# =========================

        
def debug_family_state(user_id):
    print("\n===== [FAMILY DEBUG] =====")

    # family_members
    cur.execute("SELECT * FROM family_members WHERE user_id=?", (user_id,))
    fm = cur.fetchall()
    print(f"[DEBUG] family_members rows: {fm}")

    # users table
    cur.execute("SELECT family_id FROM users WHERE id=?", (user_id,))
    u = cur.fetchone()
    print(f"[DEBUG] users.family_id: {u}")

    # JOIN проверка
    cur.execute("""
        SELECT f.family_id, f.name
        FROM families f
        JOIN family_members m ON f.family_id = m.family_id
        WHERE m.user_id=?
    """, (user_id,))
    fam = cur.fetchone()
    print(f"[DEBUG] JOIN family: {fam}")

    print("===== [END FAMILY DEBUG] =====\n")        
        
def fix_family_duplicates():
    print("\n[FIX FAMILY DUPLICATES]")

    cur.execute("""
        SELECT user_id, family_id, COUNT(*)
        FROM family_members
        GROUP BY user_id, family_id
        HAVING COUNT(*) > 1
    """)

    duplicates = cur.fetchall()

    for user_id, family_id, count in duplicates:
        print(f"[FIX] user={user_id} family={family_id} duplicates={count}")

        cur.execute("""
            DELETE FROM family_members
            WHERE rowid NOT IN (
                SELECT MIN(rowid)
                FROM family_members
                WHERE user_id=? AND family_id=?
            )
            AND user_id=? AND family_id=?
        """, (user_id, family_id, user_id, family_id))

    conn.commit()        
    
fix_family_duplicates()    
 
def is_shared_finance(user_id):
    try:
        # получаем семью пользователя
        cur.execute("SELECT family_id FROM users WHERE id=?", (user_id,))
        res = cur.fetchone()

        if not res or not res[0]:
            return False  # нет семьи

        family_id = res[0]

        # получаем режим семьи
        cur.execute(
            "SELECT shared_finance FROM families WHERE family_id=?",
            (family_id,)
        )
        row = cur.fetchone()

        if not row:
            return False

        return bool(row[0])

    except Exception as e:
        print("[ERROR] is_shared_finance:", e)
        return False


def set_shared_finance(user_id, value: bool):
    try:
        cur.execute("""
            SELECT family_id FROM family_members WHERE user_id=?
        """, (user_id,))
        row = cur.fetchone()

        if not row:
            return

        family_id = row[0]

        cur.execute("""
            UPDATE families
            SET shared_finance=?
            WHERE family_id=?
        """, (1 if value else 0, family_id))

        conn.commit()

    except Exception as e:
        print("[ERROR] set_shared_finance:", e)

def toggle_finance_mode(family_id: str, mode: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        UPDATE families 
        SET finance_mode = ? 
        WHERE id = ?
    """, (mode, family_id))

    conn.commit()
    conn.close()
    
def init_fin_column():
    try:
        cur.execute("ALTER TABLE users ADD COLUMN fin_enabled INTEGER DEFAULT 0")
    except:
        pass
    conn.commit()

init_fin_column()


def is_fin_enabled(user_id):
    try:
        cur.execute("SELECT fin_enabled FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()

        if not row:
            return False

        return bool(row[0])

    except:
        return False


def toggle_fin_enabled(user_id):
    try:
        current = is_fin_enabled(user_id)

        cur.execute("""
            UPDATE users
            SET fin_enabled=?
            WHERE id=?
        """, (0 if current else 1, user_id))

        conn.commit()

        return not current

    except Exception as e:
        print("toggle_fin_enabled error:", e)
        return False    