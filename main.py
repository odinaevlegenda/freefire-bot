import telebot
from telebot import types

# ==================== ТАНЗИМОТ ====================
TOKEN = '8924908374:AAF6cctZO-gh35sBKu-uU0ntoRtjP38VLgE'
ADMIN_ID = 6895966276

# Рӯйхати каналҳо
CHANNELS = [
    '@bio_of5',
    '@otziv_of5'
]

# Базаи содда барои нигоҳ доштани забони корбарон
user_languages = {}

bot = telebot.TeleBot(TOKEN)

# Функцияи санҷиши обуна
def check_subscriptions(user_id):
    unsubscribed = []
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['creator', 'administrator', 'member']:
                unsubscribed.append(channel)
        except Exception:
            unsubscribed.append(channel)
    return unsubscribed

# /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    unsubscribed = check_subscriptions(user_id)
    
    if unsubscribed:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Биография OF5 🔹", url="https://t.me/bio_of5")
        btn2 = types.InlineKeyboardButton("Отзыв OF5 🔹", url="https://t.me/otziv_of5")
        btn_check = types.InlineKeyboardButton("Тасдиқ кардан ✅", callback_data="check_subscription")
        
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn_check)
        
        bot.send_message(
            message.chat.id, 
            "• Барои истифодаи бот ба каналхои мо обуна шавед • ✅", 
            reply_markup=markup
        )
    else:
        # Агар забони корбар аллакай соҳранит шуда бошад (ва админ набошад)
        if user_id in user_languages and user_id != ADMIN_ID:
            show_main_menu(message.chat.id, user_languages[user_id], message.from_user.first_name)
        else:
            # Агар забон интихоб нашуда бошад ё корбар Админ бошад
            show_language_menu(message.chat.id)

# Санҷиши кнопкаи «Тасдиқ кардан ✅»
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_callback(call):
    user_id = call.from_user.id
    unsubscribed = check_subscriptions(user_id)
    
    if not unsubscribed:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "Тасдиқ қабул шуд ✅", show_alert=True)
        
        if user_id in user_languages and user_id != ADMIN_ID:
            show_main_menu(call.message.chat.id, user_languages[user_id], call.from_user.first_name)
        else:
            show_language_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "Шумо то ҳол обуна нашудед ❌", show_alert=True)

# Менюи интихоби забон
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

# Обработкаи кнопкаҳои забон
@bot.callback_query_handler(func=lambda call: call.data in ["lang_tj", "lang_ru"])
def language_callback(call):
    user_id = call.from_user.id
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Соҳранит кардани забони интихобшуда
    selected_lang = "tj" if call.data == "lang_tj" else "ru"
    user_languages[user_id] = selected_lang
    
    show_main_menu(call.message.chat.id, selected_lang, call.from_user.first_name)

# Менюи асосӣ (Алмос / Ваучер)
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

# Обработкаи кнопкаҳои Алмос ва Ваучер
@bot.callback_query_handler(func=lambda call: call.data in ["select_diamond", "select_voucher"])
def items_callback(call):
    # Паёми пештараро гум (нест) мекунем
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "tj")
    
    if call.data == "select_diamond":
        # Дар инҷо қисми ояндаи Алмосҳо меравад
        pass
    elif call.data == "select_voucher":
        # Дар инҷо қисми ояндаи Ваучерҳо меравад
        pass

bot.polling(none_stop=True)
