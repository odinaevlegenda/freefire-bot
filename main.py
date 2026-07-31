import telebot
from telebot import types

TOKEN = '8701145683:AAHkSf1gMQK_j08xIvwBem40y8yF96EuixI'
bot = telebot.TeleBot(TOKEN)

# Номи каналҳо барои тафтиши обуна
CHANNELS = ['@bio_of5', '@otziv_of5']

# ID-и админ
ADMIN_ID = 6895966276  

# ID-и сурати ту
PHOTO_FILE_ID = 'QhSaZwKhMkeivwtFA' 

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

def send_main_menu(chat_id, user_name):
    caption_text = MENU_CAPTION_TEMPLATE.format(name=user_name)
    keyboard = get_main_menu_keyboard()
    
    try:
        # Фиристодани сурат тавассути File ID
        bot.send_photo(chat_id, PHOTO_FILE_ID, caption=caption_text, reply_markup=keyboard)
    except Exception as e:
        # Агар ID хато бошад ё сурат наравад, танҳо матнро мефиристад
        print(f"Хатогӣ дар фиристодани сурат: {e}")
        bot.send_message(chat_id, caption_text, reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
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
    
    if call.data == "check_sub":
        if check_subscriptions(user_id):
            bot.answer_callback_query(call.id, "Боти худкор шуморо ба боти худ роҳ дод! ✅", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_main_menu(call.message.chat.id, user_name)
        else:
            bot.answer_callback_query(call.id, "Error : 1 обуна нашудан ба каналҳо ❌", show_alert=True)

    elif call.data == "admin_panel":
        if user_id == ADMIN_ID:
            bot.answer_callback_query(call.id, "Хуш омадед ба панели админ! ⚡", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Error : 2 Барои админ!", show_alert=True)

    elif call.data == "none":
        bot.answer_callback_query(call.id)

bot.polling(none_stop=True)
