from telebot import TeleBot
import requests
import telebot
import json
API='3fe0e2348031d7a1fabcf78487e89811'


TOKEN="8234999691:AAFyTz6zqqGPfgdZNMv1vwbzr6UxEMvH1iw"
bot: TeleBot=telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start','main',"Привет"])
def main(message):
    bot.send_message(message.chat.id, f'привет, {message.from_user.first_name},{message.from_user.last_name}' )


@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id,'<b>Help</b> <em><u>contact:@B0TlK</u></em>', parse_mode='html')


@bot.message_handler(commands=['weather'])
def weather(message):
    bot.send_message(message.chat.id, 'Напиши название города ')
    bot.register_next_step_handler(message, get_weather)
def get_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        bot.reply_to(message,f'Сейчас погода: {temp} °C ')
    else:
        bot.reply_to(message, 'Город указан не верно')


bot.polling(none_stop=True)
