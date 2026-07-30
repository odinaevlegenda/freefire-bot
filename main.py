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

# Функсияи гирифтани Ник аз Donatov.net ва дигар манбаъҳо
def get_player_nickname(player_id):
    # 1. Санҷиш тавассути Donatov.net (бо фармоиш додани Header-ҳои одамӣ)
    try:
        url = "https://donatov.net/api/shop/products/free-fire/check-player"
        payload = {"account": str(player_id)}
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://donatov.net",
            "Referer": "https://donatov.net/free-fire-diamonds"
        }
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            nick = data.get("nickname") or data.get("name") or data.get("player_name")
            if nick:
                return nick
    except Exception:
        pass

    # 2. Агар Donatov.net ҷавоб надиҳад, тавассути API-и озоди Garena мегирад
    try:
        url2 = f"https://api.garena.com/shop/v1/public/player/name?app_id=100067&player_id={player_id}"
        res2 = requests.get(url2, timeout=5).json()
        if "nickname" in res2 and res2["nickname"]:
            return res2["nickname"]
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

    wait_msg = bot.send_message(message.chat.id, "⏳ Санҷиши никнейм..." if lang == "tj" else "⏳ Проверка ника...")

    # Гирифтани никнейм
    nickname = get_player_nickname(user_game_id)

    try:
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception:
        pass

    if nickname:
        if lang == "tj":
            success_msg = (
                f"✅ **Аккаунт пайдо шуд!**\n\n"
                f"🎮 **Никнейм:** `{nickname}`\n"
                f"🆔 **ID:** `{user_game_id}`"
            )
        else:
            success_msg = (
                f"✅ **Аккаунт найден!**\n\n"
                f"🎮 **Никнейм:** `{nickname}`\n"
                f"🆔 **ID:** `{user_game_id}`"
            )
    else:
        if lang == "tj":
            success_msg = f"✅ **ID қабул шуд:** `{user_game_id}`"
        else:
            success_msg = f"✅ **ID принят:** `{user_game_id}`"

    bot.send_message(message.chat.id, success_msg, parse_mode="Markdown")

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=10)
        
