import telebot
from telebot import types

TOKEN = '8701145683:AAHkSf1gMQK_j08xIvwBem40y8yF96EuixI'
bot = telebot.TeleBot(TOKEN)

CHANNELS = ['@bio_of5', '@otziv_of5']

def check_subscriptions(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    
    text = (
        "Барои истифодаи Боти худкор ба каналҳои мо обуна шавед ✅"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Биография OF5 🔹", url="https://t.me/bio_of5")
    btn2 = types.InlineKeyboardButton("Отзыв OF5 🔹", url="https://t.me/otziv_of5")
    btn_check = types.InlineKeyboardButton("Тафтиш кардан 🔃", callback_data="check_sub")
    
    markup.row(btn1, btn2)
    markup.row(btn_check)
    
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_callback(call):
    user_id = call.from_user.id
    
    if check_subscriptions(user_id):
        bot.answer_callback_query(call.id, "Боти худкор шуморо ба боти худ роҳ дод! ✅", show_alert=True)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "Error : 1 обуна нашудан ба каналҳо ❌", show_alert=True)

bot.polling(none_stop=True)
