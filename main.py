import telebot
from telebot import types
import time
import re
import requests

TOKEN = '8701145683:AAHkSf1gMQK_j08xIvwBem40y8yF96EuixI'
bot = telebot.TeleBot(TOKEN)

# Номи каналҳо барои тафтиши обуна
CHANNELS = ['@bio_of5', '@otziv_of5']

# ID-и админ
ADMIN_ID = 6895966276  

# ID-и сурати ту
PHOTO_FILE_ID = 'QhSaZwKhMkeivwtFA' 

# Базаҳои маълумот
user_purchases = {}
user_history = {}
user_blocks = {}
admin_clicks = {}
user_states = {}

MENU_CAPTION_TEMPLATE = (
    "Хуш омадед! {name} 🌴\n\n"
    "Боти худкор аз шумо интихоби вариантҳо талаб мекунад📊 :"
)

def get_ff_nickname(game_id):
    """Функсия барои гирифтани аниқи никнейм аз API мустақим"""
    # 1. Кӯшиши аввал: API-и боэътимоди Free Fire
    try:
        url_api = f"https://freefire-virtex.vercel.app/api/checkid?id={game_id}"
        res = requests.get(url_api, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if "nickname" in data and data["nickname"]:
                return data["nickname"]
            elif "name" in data and data["name"]:
                return data["name"]
    except Exception:
        pass

    # 2. Кӯшиши дуюм: API-и захиравӣ
    try:
        url_api2 = f"https://api.garena.com/shop/auth/check_id?id={game_id}"
        res2 = requests.get(url_api2, timeout=5)
        if res2.status_code == 200:
            data2 = res2.json()
            if "nickname" in data2:
                return data2["nickname"]
    except Exception:
        pass

    # 3. Кӯшиши сеюм: Дархости мустақим ба мобилверсо
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json, text/plain, */*'
        }
        url_mv = f"https://mobileverso.com.br/api/freefire/id/{game_id}"
        res3 = requests.get(url_mv, headers=headers, timeout=5)
        if res3.status_code == 200:
            data3 = res3.json()
            if "nick" in data3:
                return data3["nick"]
            elif "name" in data3:
                return data3["name"]
    except Exception:
        pass

    return None

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
    
    if user_id in user_states:
        del user_states[user_id]

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
    
    blocked, hours, minutes = is_user_blocked(user_id)
    if blocked:
        bot.answer_callback_query(call.id, f"⛔ Шумо блок ҳастед! Эътибор: {hours} соату {minutes} дақиқа", show_alert=True)
        return

    if call.data == "check_sub":
        if check_subscriptions(user_id):
            bot.answer_callback_query(call.id, "Боти худкор шуморо ба боти худ роҳ дод! ✅", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_main_menu(call.message.chat.id, user_name)
        else:
            bot.answer_callback_query(call.id, "Error : 1 обуна нашудан ба каналҳо ❌", show_alert=True)

    elif call.data == "open_ff":
        bot.answer_callback_query(call.id)
        
        ff_text = "Шумо дар кадом Регион мехоҳед донат кунед ? 🤔"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_sg = types.InlineKeyboardButton("FREE FIRE SG 🇹🇯", callback_data="select_region_sg")
        btn_id = types.InlineKeyboardButton("FREE FIRE INDONESIA 🇮🇩", callback_data="select_region_id")
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

    elif call.data in ["select_region_sg", "select_region_id"]:
        bot.answer_callback_query(call.id)
        
        region_name = "FREE FIRE SG 🇹🇯" if call.data == "select_region_sg" else "FREE FIRE INDONESIA 🇮🇩"
        user_states[user_id] = {'state': 'waiting_for_game_id', 'region': region_name}
        
        ask_id_text = (
            f"Регион: {region_name}\n\n"
            "Лутфан 🆔 - бозиро фиристед ба бот!\n"
            "Мисол : 112345678910"
        )
        
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("БА ҚАФО 🔙", callback_data="open_ff")
        markup.add(btn_back)
        
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=ask_id_text,
                reply_markup=markup
            )
        except Exception:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, ask_id_text, reply_markup=markup)

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

    elif call.data == "back_to_menu":
        bot.answer_callback_query(call.id)
        if user_id in user_states:
            del user_states[user_id]
            
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

    elif call.data == "admin_panel":
        if user_id == ADMIN_ID:
            bot.answer_callback_query(call.id, "Хуш омадед ба панели админ! ⚡", show_alert=True)
        else:
            clicks = admin_clicks.get(user_id, 0) + 1
            admin_clicks[user_id] = clicks
            
            if clicks >= 3:
                block_user_hours(user_id, 24)
                admin_clicks[user_id] = 0
                bot.answer_callback_query(call.id, "⛔ Шумо 3 бор кӯшиши ба даст овардани ботро кардед! Бот шуморо ба 24 соат блок кард ‼️", show_alert=True)
            else:
                remaining_attempts = 3 - clicks
                bot.answer_callback_query(call.id, f"Error : 2 Барои админ! (Кӯшишҳои боқимонда: {remaining_attempts})", show_alert=True)

    elif call.data == "none":
        bot.answer_callback_query(call.id)

# Қабули ID-и бозӣ аз корбар ва тафтиши никнейм
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    
    blocked, hours, minutes = is_user_blocked(user_id)
    if blocked:
        bot.send_message(message.chat.id, f"⛔ Шумо ба қоидаҳо риоя накардед! Паёми шумо дар муддати {hours} соату {minutes} дақиқа қабул карда намешавад ‼️\n\nАгар иштибоҳ шуда бошад ба админ муроҷиат кунед: @odinaevff 🌴")
        return

    if user_id in user_states and user_states[user_id].get('state') == 'waiting_for_game_id':
        game_id_text = message.text.strip()
        
        if re.fullmatch(r'^\d{8,14}$', game_id_text):
            region = user_states[user_id].get('region', '')
            del user_states[user_id]
            
            msg = bot.reply_to(message, "🔍 Лутфан сабр кунед, тафтиши ID дар сайт...")
            
            # Ҷустуҷӯи ном аз API
            player_name = get_ff_nickname(game_id_text)
            
            if player_name:
                text = (
                    f"✅ 🆔-и бозии шумо қабул шуд!\n\n"
                    f"👤 Ники аккаунт: `{player_name}`\n"
                    f"🆔: `{game_id_text}`\n"
                    f"🌍 Регион: {region}"
                )
            else:
                text = (
                    f"✅ 🆔-и бозии шумо қабул шуд!\n\n"
                    f"🆔: `{game_id_text}`\n"
                    f"🌍 Регион: {region}\n"
                    f"`{player_name}`\n"
                )
                
            bot.edit_message_text(text, chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")
        else:
            bot.reply_to(message, "🆔 - бояд рақам бошад ва аз 8-14 то бошад !")

bot.polling(none_stop=True)
