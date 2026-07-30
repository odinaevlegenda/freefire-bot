import telebot
from telebot import types
import requests

# ==================== ТАНЗИМОТ ====================
TOKEN = '8924908374:AAHPDE4yidjUpJxCdKZzPypkWsaEtD3bU5w'
ADMIN_ID = 6895966276

user_languages = {}
bot = telebot.TeleBot(TOKEN)

try:
    bot.remove_webhook()
except Exception:
    pass

def check_subscriptions(user_id):
    return []

# /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    
    if user_id in user_languages and user_id != ADMIN_ID:
        name = message.from_user.first_name or "Дӯст"
        show_main_menu(message.chat.id, user_languages[user_id], name)
    else:
        show_language_menu(message.chat.id)

# Интихоби забон
def show_language_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn_tj = types.InlineKeyboardButton("Тоҷики 🇹🇯", callback_data="lang_tj")
    btn_ru = types.InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")
    markup.add(btn_tj)
    markup.add(btn_ru)
    
    bot.send_message(
        chat_id, 
        "Забонро интихоб кунед 🇹🇯 / Выбирайте язык 🇷🇺", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ["lang_tj", "lang_ru"])
def language_callback(call):
    user_id = call.from_user.id
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    
    selected_lang = "tj" if call.data == "lang_tj" else "ru"
    user_languages[user_id] = selected_lang
    
    name = call.from_user.first_name or "Дӯст"
    show_main_menu(call.message.chat.id, selected_lang, name)

# Менюи асосӣ
def show_main_menu(chat_id, lang, first_name):
    markup = types.InlineKeyboardMarkup()
    
    if lang == "tj":
        btn_diamond = types.InlineKeyboardButton("Алмос 💎", callback_data="select_diamond")
        btn_voucher = types.InlineKeyboardButton("Ваучер 🎟️", callback_data="select_voucher")
        text = f"Хуш омадед {first_name} 👋\n\nБарои харидани алмос ё ваучер интихоб кунед :"
    else:
        btn_diamond = types.InlineKeyboardButton("Алмазы 💎", callback_data="select_diamond")
        btn_voucher = types.InlineKeyboardButton("Ваучер 🎟️", callback_data="select_voucher")
        text = f"Добро пожаловать {first_name} 👋\n\nВыберите для покупки алмазов или ваучера :"
        
    markup.add(btn_diamond)
    markup.add(btn_voucher)
    
    bot.send_message(chat_id, text, reply_markup=markup)

# Пурсидани ID-и Free Fire
@bot.callback_query_handler(func=lambda call: call.data in ["select_diamond", "select_voucher"])
def items_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "tj")
    
    if lang == "tj":
        msg = bot.send_message(call.message.chat.id, "🆔 **ID-и FREE FIRE**-ро ворид кунед:", parse_mode="Markdown")
    else:
        msg = bot.send_message(call.message.chat.id, "🆔 Введите ваш **ID FREE FIRE**:", parse_mode="Markdown")
        
    bot.register_next_step_handler(msg, process_ff_id)

# Ҷустуҷӯи Никнейм
def get_player_nickname(player_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    # 1. KZShopGarena
    try:
        url_kz = f"https://kzshopgarena.com/api/check?id={player_id}"
        res_kz = requests.get(url_kz, headers=headers, timeout=5).json()
        if "nickname" in res_kz and res_kz["nickname"]:
            return res_kz["nickname"]
        if "name" in res_kz and res_kz["name"]:
            return res_kz["name"]
    except Exception:
        pass

    # 2. Сервери эҳтиётии 1
    try:
        url_alt1 = f"https://ff-api-roan.vercel.app/api/ff?id={player_id}"
        res_alt1 = requests.get(url_alt1, timeout=5).json()
        if "nickname" in res_alt1 and res_alt1["nickname"]:
            return res_alt1["nickname"]
        if "AccountName" in res_alt1 and res_alt1["AccountName"]:
            return res_alt1["AccountName"]
    except Exception:
        pass

    # 3. Сервери эҳтиётии 2
    try:
        url_alt2 = f"https://free-fire-api-three.vercel.app/api/ff_info?id={player_id}"
        res_alt2 = requests.get(url_alt2, timeout=5).json()
        if "nickname" in res_alt2 and res_alt2["nickname"]:
            return res_alt2["nickname"]
        if "AccountName" in res_alt2 and res_alt2["AccountName"]:
            return res_alt2["AccountName"]
    except Exception:
        pass

    return None

def process_ff_id(message):
    user_game_id = message.text.strip()
    user_id = message.from_user.id
    lang = user_languages.get(user_id, "tj")
    
    if not user_game_id.isdigit():
        err_msg = "❌ ID нодуруст аст! Лутфан танҳо рақамҳоро ворид кунед:" if lang == "tj" else "❌ Неверный ID! Пожалуйста, введите только цифры:"
        msg = bot.send_message(message.chat.id, err_msg)
        bot.register_next_step_handler(msg, process_ff_id)
        return

    wait_msg = bot.send_message(message.chat.id, "⏳ Санҷиши никнейм ва ID..." if lang == "tj" else "⏳ Проверка ника и ID...")

    # Гирифтани никнейм
    nickname = get_player_nickname(user_game_id)

    try:
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception:
        pass

    # Агар никнейм пайдо шавад — ID ва Никро нишон медиҳад
    if nickname:
        if lang == "tj":
            success_msg = (
                f"✅ **ID ва Никнейм тасдиқ шуд!**\n\n"
                f"👤 **Никнейми шумо:** `{nickname}`\n"
                f"🆔 **ID-и шумо:** `{user_game_id}`\n\n"
                f"📌 Оё ин аккаунти шумост?"
            )
        else:
            success_msg = (
                f"✅ **ID и Никнейм подтверждены!**\n\n"
                f"👤 **Ваш Никнейм:** `{nickname}`\n"
                f"🆔 **Ваш ID:** `{user_game_id}`\n\n"
                f"📌 Это ваш аккаунт?"
            )
        bot.send_message(message.chat.id, success_msg, parse_mode="Markdown")
    else:
        # Агар ID нодуруст бошад ё никнейм набарояд, аз нав пурсиш мекунад
        if lang == "tj":
            error_msg = "❌ **Никнейм пайдо нашуд!**\n\nЛутфан ID-ро санҷида, аз нав дуруст ворид кунед:"
        else:
            error_msg = "❌ **Никнейм не найден!**\n\nПожалуйста, проверьте ID и введите заново:"
            
        msg = bot.send_message(message.chat.id, error_msg, parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_ff_id)

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=10)
