import telebot
from telebot import types
import time

TOKEN = '8701145683:AAHkSf1gMQK_j08xIvwBem40y8yF96EuixI'
bot = telebot.TeleBot(TOKEN)

# Номи каналҳо барои тафтиши обуна
CHANNELS = ['@bio_of5', '@otziv_of5']

# ID-и админ
ADMIN_ID = 6895966276  

# ID-и сурати ту
PHOTO_FILE_ID = 'QhSaZwKhMkeivwtFA' 

# Базаи содда барои ҳисоби харидҳо ва таърих
user_purchases = {}
user_history = {}

# База барои нигоҳдории блокҳо ва кликҳои админ-панел
# user_blocks[user_id] = timestamp_until_unblocked
user_blocks = {}

# admin_click_count[user_id] = count
admin_clicks = {}

MENU_CAPTION_TEMPLATE = (
    "Хуш омадед! {name} 🌴\n\n"
    "Боти худкор аз шумо интихоби вариантҳо талаб мекунад📊 :"
)

def check_subscriptions(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

def is_user_blocked(user_id):
    """Тафтиш мекунад, ки корбар дар блок аст ё не"""
    if user_id in user_blocks:
        unblock_time = user_blocks[user_id]
        if time.time() < unblock_time:
            remaining_seconds = int(unblock_time - time.time())
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            return True, hours, minutes
        else:
            del user_blocks[user_id]
    return False, 0, 0

def block_user_hours(user_id, hours):
    """Блок кардани корбар ба соати муайян"""
    user_blocks[user_id] = time.time() + (hours * 3600)

def get_main_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("FREE FIRE 🔥", callback_data="open_ff")
    btn2 = types.InlineKeyboardButton("ПРОФИЛЬ 📉", callback_data="open_profile")
    btn3 = types.InlineKeyboardButton("ТАЪРИХ 🕐", callback_data="open_history")
    btn4 = types.InlineKeyboardButton("ҚОИДАҲО 🚧", callback_data="open_rules")
    btn5 = types.InlineKeyboardButton("ПАНЕЛИ АДМИН ⚡", callback_data="admin_panel")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
        
    return markup

def send_main_menu(chat_id, user_name):
    caption_text = MENU_CAPTION_TEMPLATE.format(name=user_name)
    keyboard = get_main_menu_keyboard()
    
    try:
        bot.send_photo(chat_id, PHOTO_FILE_ID, caption=caption_text, reply_markup=keyboard)
    except Exception as e:
        print(f"Хатогӣ дар фиристодани сурат: {e}")
        bot.send_message(chat_id, caption_text, reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Тафтиши блок
    blocked, hours, minutes = is_user_blocked(user_id)
    if blocked:
        bot.send_message(message.chat.id, f"⛔ Шумо ба қоидаҳо риоя накардед! Паёми шумо дар муддати {hours} соату {minutes} дақиқа қабул карда намешавад ‼️\n\nАгар иштибоҳ шуда бошад ба админ муроҷиат кунед: @odinaevff 🌴")
        return

    if check_subscriptions(user_id):
        send_main_menu(message.chat.id, user_name)
    else:
        text = "Барои истифодаи Боти худкор ба каналҳои мо обуна шавед ✅"
        
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Биография OF5 🔹", url="https://t.me/bio_of5")
        btn2 = types.InlineKeyboardButton("Отзыв OF5 🔹", url="https://t.me/otziv_of5")
        btn_check = types.InlineKeyboardButton("Тафтиш кардан 🔃", callback_data="check_sub")
        
        markup.row(btn1, btn2)
        markup.row(btn_check)
        
        bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    username = call.from_user.username
    
    # Тафтиши блок барои ҳамаи тугмаҳо
    blocked, hours, minutes = is_user_blocked(user_id)
    if blocked:
        bot.answer_callback_query(call.id, f"⛔ Шумо блок ҳастед! Эътибор: {hours} соату {minutes} дақиқа", show_alert=True)
        return

    # 1. Тафтиши обуна
    if call.data == "check_sub":
        if check_subscriptions(user_id):
            bot.answer_callback_query(call.id, "Боти худкор шуморо ба боти худ роҳ дод! ✅", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_main_menu(call.message.chat.id, user_name)
        else:
            bot.answer_callback_query(call.id, "Error : 1 обуна нашудан ба каналҳо ❌", show_alert=True)

    # 2. Тугмаи FREE FIRE
    elif call.data == "open_ff":
        bot.answer_callback_query(call.id)
        
        ff_text = "Шумо дар кадом Регион мехоҳед донат кунед ? 🤔"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_sg = types.InlineKeyboardButton("FREE FIRE SG 🇹🇯", callback_data="none")
        btn_id = types.InlineKeyboardButton("FREE FIRE INDONESIA 🇮🇩", callback_data="none")
        btn_back = types.InlineKeyboardButton("БА ҚАФО 🔙", callback_data="back_to_menu")
        
        markup.add(btn_sg, btn_id)
        markup.add(btn_back)
        
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=ff_text,
                reply_markup=markup
            )
        except Exception:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, ff_text, reply_markup=markup)

    # 3. Тугмаи ПРОФИЛЬ
    elif call.data == "open_profile":
        bot.answer_callback_query(call.id)
        
        user_nick = f"@{username}" if username else "Мавҷуд нест"
        purchases = user_purchases.get(user_id, 0)
        
        profile_text = (
            f"Салом! {user_name} 🌴\n\n"
            f"🔠 : {user_nick}\n"
            f"🆔 : {user_id}\n"
            f"🛒 : #{purchases}\n\n"
            f"Ин профили шумо аст! 😋"
        )
        
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("БА ҚАФО 🔙", callback_data="back_to_menu")
        markup.add(btn_back)
        
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=profile_text,
                reply_markup=markup
            )
        except Exception:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, profile_text, reply_markup=markup)

    # 4. Тугмаи ТАЪРИХ
    elif call.data == "open_history":
        bot.answer_callback_query(call.id)
        
        history_list = user_history.get(user_id, [])
        
        if not history_list:
            history_text = (
                "Таърихҳои донат дар бози ! 🛒\n\n"
                "Шумо ҳануз ягон донат накардаед! 🚧\n\n"
                "Инҳо буданд таърихҳои донати шумо 📊"
            )
        else:
            records = "\n".join(history_list)
            history_text = (
                f"Таърихҳои донат дар бози ! 🛒\n\n"
                f"{records}\n\n"
                f"Инҳо буданд таърихҳои донати шумо 📊"
            )
        
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("БА ҚАФО 🔙", callback_data="back_to_menu")
        markup.add(btn_back)
        
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=history_text,
                reply_markup=markup
            )
        except Exception:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, history_text, reply_markup=markup)

    # 5. Тугмаи ҚОИДАҲО (Кнопка 4)
    elif call.data == "open_rules":
        bot.answer_callback_query(call.id)
        
        rules_text = (
            "Қоидаҳо ⛔\n\n"
            "Қоидаи 1 \n"
            "Ҳангоми партофтани чеки тақаллубӣ дар муддати 1 соат бот паёми шуморо қабул намекунад ‼️\n\n"
            "Қоидаи 2 \n"
            "Аз бот ссылка, борҳояш ё паёмҳояшро дуздида (копироват) ба дигар бот фиристодан дар муддати 12 соат бот паёми шуморо қабул намекунад ‼️\n\n"
            "Қоидаи 3\n"
            "Ҳангоми ба паёми ПАНЕЛИ АДМИН ⚡ 3 бор зер кардан яъне ботро ба даст овардан дар муддати 24 соат бот паёми шуморо қабул намекунад ‼️\n\n"
            "Агар ягон иштибоҳ ё нохоста пахш карди ба админ муроҷиат кунед !\n"
            "@odinaevff 🌴"
        )
        
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("БА ҚАФО 🔙", callback_data="back_to_menu")
        markup.add(btn_back)
        
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=rules_text,
                reply_markup=markup
            )
        except Exception:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, rules_text, reply_markup=markup)

    # 6. Тугмаи БА ҚАФО (Баргаштан ба менюи асосӣ)
    elif call.data == "back_to_menu":
        bot.answer_callback_query(call.id)
        caption_text = MENU_CAPTION_TEMPLATE.format(name=user_name)
        keyboard = get_main_menu_keyboard()
        
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=caption_text,
                reply_markup=keyboard
            )
        except Exception:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_main_menu(call.message.chat.id, user_name)

    # 7. Панели админ (Бо ҳисоби 3 зер кардан ва блок 24 соат)
    elif call.data == "admin_panel":
        if user_id == ADMIN_ID:
            bot.answer_callback_query(call.id, "Хуш омадед ба панели админ! ⚡", show_alert=True)
        else:
            # Ҳисоб кардани пахши тугма
            clicks = admin_clicks.get(user_id, 0) + 1
            admin_clicks[user_id] = clicks
            
            if clicks >= 3:
                # Блок кардани корбар ба 24 соат (Қоидаи 3)
                block_user_hours(user_id, 24)
                admin_clicks[user_id] = 0  # Сброс
                bot.answer_callback_query(call.id, "⛔ Шумо 3 бор кӯшиши ба даст овардани ботро кардед! Бот шуморо ба 24 соат блок кард ‼️", show_alert=True)
            else:
                remaining_attempts = 3 - clicks
                bot.answer_callback_query(call.id, f"Error : 2 Барои админ! (Кӯшишҳои боқимонда: {remaining_attempts})", show_alert=True)

    # 8. Тугмаҳои дигар
    elif call.data == "none":
        bot.answer_callback_query(call.id)

bot.polling(none_stop=True)
    
