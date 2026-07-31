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
    
    if check_subscriptions(user_id):
        bot.send_message(message.chat.id, "Боти худкор шуморо шодбош мегуяд ! 🙂")
    else:
        text = (
            "Error : 1 обуна нашудан ба канал ❌\n"
            "Барои истифодаи Боти худкор ба каналҳои мо обуна шавед ✅"
        )
        
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Биография OF5 🔹", url="https://t.me/bio_of5")
        btn2 = types.InlineKeyboardButton("Отзыв OF5 🔹", url="https://t.me/otziv_of5")
        markup.add(btn1, btn2)
        
        bot.send_message(message.chat.id, text, reply_markup=markup)

bot.polling(none_stop=True)
