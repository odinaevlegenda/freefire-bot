import telebot
from telebot import types
import requests

# ==================== ТАНЗИМОТ ====================
TOKEN = '8924908374:AAF6cctZO-gh35sBKu-uU0ntoRtjP38VLgE'
ADMIN_ID = 6895966276

user_languages = {}
bot = telebot.TeleBot(TOKEN)

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

# Функсияи пайдо кардани НИКНЕЙМ бе API Key
def process_ff_id(message):
    user_game_id = message.text.strip()
    user_id = message.from_user.id
    lang = user_languages.get(user_id, "tj")
    
    if not user_game_id.isdigit():
        err_msg = "❌ ID нодуруст аст! Лутфан танҳо рақамҳоро ворид кунед:" if lang == "tj" else "❌ Неверный ID! Пожалуйста, введите только цифры:"
        msg = bot.send_message(message.chat.id, err_msg)
        bot.register_next_step_handler(msg, process_ff_id)
        return

    wait_msg = bot.send_message(message.chat.id, "⏳ Ҷустуҷӯи никнейми бозӣ..." if lang == "tj" else "⏳ Поиск ника...")

    nickname = None
    
    # Истифодаи API-и озоди Free Fire (Region SG/IND/EU)
    try:
        url = f"https://region-info-ff.vercel.app/api/info?id={user_game_id}"
        res = requests.get(url, timeout=7).json()
        if "AccountInfo" in res and "AccountName" in res["AccountInfo"]:
            nickname = res["AccountInfo"]["AccountName"]
        elif "nickname" in res:
            nickname = res["nickname"]
    except Exception:
        pass

    # Агар аз сервери аввал нагирад, аз сервери дуюм месанҷем
    if not nickname:
        try:
            url2 = f"https://free-fire-api-three.vercel.app/api/ff_info?id={user_game_id}"
            res2 = requests.get(url2, timeout=7).json()
            if "nickname" in res2:
                nickname = res2["nickname"]
            elif "AccountName" in res2:
                nickname = res2["AccountName"]
        except Exception:
            pass

    # Тоза кардани паёми интизорӣ
    try:
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception:
        pass

    # Намоиши натиҷа
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
            success_msg = (
                f"✅ **ID қабул шуд:** `{user_game_id}`\n"
                f"⚠️ *(Никнейм ба таври автоматикӣ пайдо нашуд)*"
            )
        else:
            success_msg = (
                f"✅ **ID принят:** `{user_game_id}`\n"
                f"⚠️ *(Никнейм не найден автоматически)*"
            )

    bot.send_message(message.chat.id, success_msg, parse_mode="Markdown")

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
