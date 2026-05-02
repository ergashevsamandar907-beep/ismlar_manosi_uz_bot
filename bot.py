import asyncio
import sqlite3
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# TO'G'RI TOKEN VA ID LAR
API_TOKEN = "8718770348:AAGKn5Sk1E8P-JNMzOf8q5JnPEmRvaAZy0M"
ADMIN_ID = 8663125946  
KANAL_USERNAME = "@mayahumayahi"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
REFERRAL_BONUS = 100  

# 1. BAZA BILAN ISHLASH (TIL USTUNI QO'SHILDI)
def baza_yarat():
    conn = sqlite3.connect("bot_bazasi.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            id INTEGER PRIMARY KEY,
            balans INTEGER DEFAULT 0,
            invited_by INTEGER DEFAULT NULL,
            til TEXT DEFAULT 'uz'
        )
    """)
    # Agar jadval oldin yaratilgan bo'lsa, 'til' ustuni bor-yo'qligini tekshirib, bo'lmasa qo'shadi
    try:
        cursor.execute("ALTER TABLE foydalanuvchilar ADD COLUMN til TEXT DEFAULT 'uz'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def foydalanuvchi_qosh(user_id, referrer_id=None):
    conn = sqlite3.connect("bot_bazasi.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO foydalanuvchilar (id, balans, invited_by, til) VALUES (?, 0, ?, 'uz')", (user_id, referrer_id))
        conn.commit()
        if referrer_id:
            cursor.execute("UPDATE foydalanuvchilar SET balans = balans + ? WHERE id = ?", (REFERRAL_BONUS, referrer_id))
            conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def foydalanuvchi_tilini_yangila(user_id, til):
    conn = sqlite3.connect("bot_bazasi.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE foydalanuvchilar SET til = ? WHERE id = ?", (til, user_id))
    conn.commit()
    conn.close()

def foydalanuvchi_tilini_ol(user_id):
    conn = sqlite3.connect("bot_bazasi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT til FROM foydalanuvchilar WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else "uz"

def foydalanuvchilar_soni():
    conn = sqlite3.connect("bot_bazasi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM foydalanuvchilar")
    soni = cursor.fetchone()[0]
    conn.close()
    return soni

def foydalanuvchi_balansi(user_id):
    conn = sqlite3.connect("bot_bazasi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balans FROM foydalanuvchilar WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0

async def aza_bolganmi(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=KANAL_USERNAME, user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            return True
        return False
    except Exception:
        return True

baza_yarat()

# 2. KO'P TILLI LUG'AT
MATNLAR = {
    "uz": {
        "start": "Assalomu alaykum! Ism kiriting yoki menyudan foydalaning.",
        "btn_ismlar": "🔍 Ismlar ro'yxati 📋",
        "btn_tasodif": "🎲 Tasodifiy ism 🎲",
        "btn_hamkor": "🤝 Hamkorlik dasturi 🤝",
        "btn_stat": "📊 Statistika 📊",
        "btn_ishlash": "🧠 Bot qanday ishlaydi",
        "btn_profil": "👤 Profilim",
        "btn_til": "🌐 Tilni almashtirish",
        "sub_text": "Botdan foydalanishdan oldin homiy kanalimizga a'zo bo'lishingiz kerak:",
        "sub_btn": "📢 Kanalga a'zo bo'lish",
        "sub_check": "✅ Tasdiqlash",
        "sub_error": "Siz hali kanalga a'zo bo'lmadingiz! ❌",
        "sub_success": "Rahmat! Endi botdan to'liq foydalanishingiz mumkin.",
        "ref_bonus": "🎉 Yangi do'st taklif qildingiz! Sizga {bonus} so'm berildi.",
        "stat_text": "📊 Jami obunachilar: {soni} ta.",
        "work_text": "Tugmalardan foydalaning yoki ism yozib yuboring.",
        "profile_text": "👤 Profilingiz:\n🆔 ID: `{user_id}`\n💰 Balans: {balans} so'm",
        "not_found": "Kechirasiz, bu ism ma'nosi hali bazamizga qo'shilmagan.",
        "change_lang": "Iltimos, tilni tanlang:",
        "lang_changed": "Til muvaffaqiyatli o'zgartirildi! 🇺🇿"
    },
    "ru": {
        "start": "Здравствуйте! Введите имя или используйте меню.",
        "btn_ismlar": "🔍 Список имен 📋",
        "btn_tasodif": "🎲 Случайное имя 🎲",
        "btn_hamkor": "🤝 Партнерская программа 🤝",
        "btn_stat": "📊 Статистика 📊",
        "btn_ishlash": "🧠 Как работает бот",
        "btn_profil": "👤 Мой профиль",
        "btn_til": "🌐 Сменить язык",
        "sub_text": "Перед использованием бота необходимо подписаться на спонсорский канал:",
        "sub_btn": "📢 Подписаться на канал",
        "sub_check": "✅ Проверить",
        "sub_error": "Вы еще не подписались на канал! ❌",
        "sub_success": "Спасибо! Теперь вы можете полноценно использовать бота.",
        "ref_bonus": "🎉 Siz priglasili novogo druga! Vam nachisleno {bonus} sum.",
        "stat_text": "📊 Всего подписчиков: {soni}.",
        "work_text": "Используйте кнопки или отправьте имя.",
        "profile_text": "👤 Ваш профиль:\n🆔 ID: `{user_id}`\n💰 Баланс: {balans} сум",
        "not_found": "Извините, значение этого имени еще не добавлено в базу.",
        "change_lang": "Пожалуйста, выберите язык:",
        "lang_changed": "Язык успешно изменен! 🇷🇺"
    },
    "en": {
        "start": "Hello! Enter a name or use the menu.",
        "btn_ismlar": "🔍 List of Names 📋",
        "btn_tasodif": "🎲 Random Name 🎲",
        "btn_hamkor": "🤝 Referral Program 🤝",
        "btn_stat": "📊 Statistics 📊",
        "btn_ishlash": "🧠 How the bot works",
        "btn_profil": "👤 My Profile",
        "btn_til": "🌐 Change Language",
        "sub_text": "Before using the bot, you must subscribe to our sponsor channel:",
        "sub_btn": "📢 Subscribe to the channel",
        "sub_check": "✅ Verify",
        "sub_error": "You have not subscribed to the channel yet! ❌",
        "sub_success": "Thank you! Now you can fully use the bot.",
        "ref_bonus": "🎉 You invited a new friend! You earned {bonus} sum.",
        "stat_text": "📊 Total subscribers: {soni}.",
        "work_text": "Use buttons or send a name.",
        "profile_text": "👤 Your profile:\n🆔 ID: `{user_id}`\n💰 Balance: {balans} sum",
        "not_found": "Sorry, the meaning of this name is not added yet.",
        "change_lang": "Please select a language:",
        "lang_changed": "Language changed successfully! 🇬🇧"
    }
}

# TUGMALARNI TILGA QARAB CHIQARISH FUNKSIYASI
def menyu_klaviaturasi(til):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MATNLAR[til]["btn_ismlar"]),
                KeyboardButton(text=MATNLAR[til]["btn_tasodif"])
            ],
            [
                KeyboardButton(text=MATNLAR[til]["btn_hamkor"]),
                KeyboardButton(text=MATNLAR[til]["btn_stat"])
            ],
            [
                KeyboardButton(text=MATNLAR[til]["btn_ishlash"]),
                KeyboardButton(text=MATNLAR[til]["btn_profil"])
            ],
            [
                KeyboardButton(text=MATNLAR[til]["btn_til"])
            ]
        ],
        resize_keyboard=True
    )

def til_tanlash_klaviaturasi():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="setlang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en")
            ]
        ]
    )

def aazolik_klaviaturasi(til):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=MATNLAR[til]["sub_btn"], url=f"https://t.me/{KANAL_USERNAME.replace('@', '')}")
            ],
            [
                InlineKeyboardButton(text=MATNLAR[til]["sub_check"], callback_data="check_sub")
            ]
        ]
    )

# ISMLARNING MA'NOLARI BAZASI
ISMLAR_MANOSI = {
    "oybek": "Oybek — oy kabi go'zal, porloq va beklik martabasiga ega bo'lgan yigit.",
    "behzod": "Behzod — yaxshi fe'l-atvorli, aslzoda va barkamol inson.",
    "jasur": "Jasur — botir, mard, qo'rqmas va dovyurak yigit.",
    "dunyo": "Dunyo — olam, borliq, yer yuzi.",
    "kamron": "Kamron — maqsadiga yetuvchi, omadli, baxtli va g'olib inson.",
    "zilola": "Zilola — tiniq, pokiza suv kabi beg'ubor va go'zal qiz."
    # Boshqa barcha ismlar ham shu yerda qoladi...
}

# START COMMAND
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    til = foydalanuvchi_tilini_ol(user_id)
    
    if not await aza_bolganmi(user_id):
        await message.answer(MATNLAR[til]["sub_text"], reply_markup=aazolik_klaviaturasi(til))
        return

    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id == user_id:
            referrer_id = None
            
    foydalanuvchi_qosh(user_id, referrer_id)
    if referrer_id and referrer_id != user_id:
        try:
            ref_til = foydalanuvchi_tilini_ol(referrer_id)
            await bot.send_message(chat_id=referrer_id, text=MATNLAR[ref_til]["ref_bonus"].format(bonus=REFERRAL_BONUS))
        except:
            pass
            
    await message.answer(MATNLAR[til]["start"], reply_markup=menyu_klaviaturasi(til))

# TILNI O'ZGARTIRISH (CALLBACK)
@dp.callback_query(lambda c: c.data.startswith("setlang_"))
async def change_language_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    yangi_til = callback_query.data.split("_")[1]
    
    foydalanuvchi_tilini_yangila(user_id, yangi_til)
    await callback_query.message.delete()
    await bot.send_message(
        chat_id=user_id, 
        text=MATNLAR[yangi_til]["lang_changed"], 
        reply_markup=menyu_klaviaturasi(yangi_til)
    )

# CALLBACK CHECK_SUB
@dp.callback_query(lambda c: c.data == "check_sub")
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    til = foydalanuvchi_tilini_ol(user_id)
    if await aza_bolganmi(user_id):
        await callback_query.message.delete()
        await bot.send_message(chat_id=user_id, text=MATNLAR[til]["sub_success"], reply_markup=menyu_klaviaturasi(til))
    else:
        await callback_query.answer(MATNLAR[til]["sub_error"], show_alert=True)

# ASOSIY XABARLAR QISMI
@dp.message()
async def bot_messages(message: types.Message):
    user_id = message.from_user.id
    til = foydalanuvchi_tilini_ol(user_id)

    if not await aza_bolganmi(user_id):
        await message.answer(MATNLAR[til]["sub_text"], reply_markup=aazolik_klaviaturasi(til))
        return

    foydalanuvchi_qosh(user_id)
    text = message.text.strip()

    # Tugmalarni har bir tilda tekshirish
    if text in [MATNLAR["uz"]["btn_ismlar"], MATNLAR["ru"]["btn_ismlar"], MATNLAR["en"]["btn_ismlar"]]:
        ismlar = ", ".join([k.capitalize() for k in ISMLAR_MANOSI.keys()])
        await message.answer(f"📚 Bazadagi ismlar:\n\n{ismlar}")
        return

    elif text in [MATNLAR["uz"]["btn_tasodif"], MATNLAR["ru"]["btn_tasodif"], MATNLAR["en"]["btn_tasodif"]]:
        tasodifiy_ism = random.choice(list(ISMLAR_MANOSI.keys()))
        mano = ISMLAR_MANOSI[tasodifiy_ism]
        await message.answer(f"🎲 Ism:\n\n📌 **{tasodifiy_ism.capitalize()}** — {mano}")
        return

    elif text in [MATNLAR["uz"]["btn_hamkor"], MATNLAR["ru"]["btn_hamkor"], MATNLAR["en"]["btn_hamkor"]]:
        bot_info = await bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        balans = foydalanuvchi_balansi(user_id)
        await message.answer(f"💰 Balans: {balans} so'm\n🔗 Link: `{ref_link}`")
        return

    elif text in [MATNLAR["uz"]["btn_stat"], MATNLAR["ru"]["btn_stat"], MATNLAR["en"]["btn_stat"]]:
        soni = foydalanuvchilar_soni()
        await message.answer(MATNLAR[til]["stat_text"].format(soni=soni))
        return

    elif text in [MATNLAR["uz"]["btn_ishlash"], MATNLAR["ru"]["btn_ishlash"], MATNLAR["en"]["btn_ishlash"]]:
        await message.answer(MATNLAR[til]["work_text"])
        return

    elif text in [MATNLAR["uz"]["btn_profil"], MATNLAR["ru"]["btn_profil"], MATNLAR["en"]["btn_profil"]]:
        balans = foydalanuvchi_balansi(user_id)
        await message.answer(MATNLAR[til]["profile_text"].format(user_id=user_id, balans=balans), parse_mode="Markdown")
        return

    elif text in [MATNLAR["uz"]["btn_til"], MATNLAR["ru"]["btn_til"], MATNLAR["en"]["btn_til"]]:
        await message.answer(MATNLAR[til]["change_lang"], reply_markup=til_tanlash_klaviaturasi())
        return

    # Ism qidirish qismi
    ism_clean = text.lower().replace("’", "").replace("`", "").replace("'", "")
    if ism_clean in ISMLAR_MANOSI:
        await message.answer(ISMLAR_MANOSI[ism_clean])
    else:
        await message.answer(MATNLAR[til]["not_found"])

# BOTNI ISHGA TUSHIRISH
async def main():
    print("---------------------------------------")
    print(" Bot ko'p tilli rejimda ishga tushdi!")
    print(" Telegramdan /start tugmasini bosing.")
    print("---------------------------------------")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())