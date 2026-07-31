import telebot
from telebot import types
import os

TOKEN = '8701145683:AAHkSf1gMQK_j08xIvwBem40y8yF96EuixI'
bot = telebot.TeleBot(TOKEN)

# Номи каналҳо барои тафтиши обуна
CHANNELS = ['@bio_of5', '@otziv_of5']

# ID-и админ
ADMIN_ID = 6895966276  

# Номи файли сурат ё линки он
PHOTO_URL_OR_PATH = 'main_banner.jpg' 

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

def get_main_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("FREE FIRE 🔥", callback_data="none")
    btn2 = types.InlineKeyboardButton("ПРОФИЛЬ 📉", callback_data="none")
    btn3 = types.InlineKeyboardButton("ТАЪРИХ 🕐", callback_data="none")
    btn4 = types.InlineKeyboardButton("ҚОИДАҲО 🚧", callback_data="none")
    btn5 = types.InlineKeyboardButton("ПАНЕЛИ АДМИН ⚡", callback_data="admin_panel")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
        
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
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
    
    # 1. Тафтиши обуна
    if call.data == "check_sub":
        if check_subscriptions(user_id):
            bot.answer_callback_query(call.id, "Боти худкор шуморо ба боти худ роҳ дод! ✅", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
            caption_text = MENU_CAPTION_TEMPLATE.format(name=user_name)
            keyboard = get_main_menu_keyboard()
            
            try:
                if PHOTO_URL_OR_PATH.startswith('http'):
                    bot.send_photo(call.message.chat.id, PHOTO_URL_OR_PATH, caption=caption_text, reply_markup=keyboard)
                elif os.path.exists(PHOTO_URL_OR_PATH):
                    with open(PHOTO_URL_OR_PATH, 'rb') as photo:
                        bot.send_photo(call.message.chat.id, photo, caption=caption_text, reply_markup=keyboard)
                else:
                    bot.send_message(call.message.chat.id, caption_text, reply_markup=keyboard)
            except Exception:
                bot.send_message(call.message.chat.id, caption_text, reply_markup=keyboard)
        else:
            bot.answer_callback_query(call.id, "Error : 1 обуна нашудан ба каналҳо ❌", show_alert=True)

    # 2. Тугмаи Панели Админ
    elif call.data == "admin_panel":
        if user_id == ADMIN_ID:
            bot.answer_callback_query(call.id, "Хуш омадед ба панели админ! ⚡", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Error : 2 Барои админ!", show_alert=True)

    # 3. Тугмаҳои оддӣ (ҳеҷ амале намекунанд)
    elif call.data == "none":
        bot.answer_callback_query(call.id)

bot.polling(none_stop=True)
            
