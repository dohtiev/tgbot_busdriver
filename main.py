## -*- coding: utf-8 -*-
import telebot
from dotenv import load_dotenv
import os
from os.path import join, dirname


def get_from_env(key):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)

bot = telebot.TeleBot(get_from_env("TELEGRAM_BOT_TOKEN"))
driver_number = get_from_env("driver_number")
driver_telegram = get_from_env("driver_telegram")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Здравствуйте, <b>{message.from_user.first_name}</b>", parse_mode='html')
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Подать заявку', 'Связаться с водителем')
    bot.send_message(message.from_user.id, 'Что вы хотите сделать?', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_user_choice(message):
    if message.text.strip() == "Подать заявку":
        save_user_data(message)
    elif message.text.strip() == "Связаться с водителем":
        bot.send_message(message.from_user.id, f"Номер телефона водителя: <b>{driver_number}</b>,\n"
                                               f"Телеграм водителя: <b>@{driver_telegram}</b>", parse_mode="html")


def save_user_data(message):
    name = bot.send_message(message.from_user.id, 'Введите имя и фамилию пассажира',
                            reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(name, save_name)


def save_name(message):
    file = open("data/data.txt", "a")
    file.write("Имя и фамилия пассажира: " + message.text + '\n')
    file.close()
    date = bot.send_message(message.from_user.id, 'Введите дату поездки')
    bot.register_next_step_handler(date, save_date)


def save_date(message):
    file = open("data/data.txt", "a")
    file.write("Дата поездки: " + message.text + '\n')
    file.close()
    start_point = bot.send_message(message.from_user.id, 'Введите начальую точку поездки (откуда)')
    bot.register_next_step_handler(start_point, save_start_point)


def save_start_point(message):
    file = open("data/data.txt", "a")
    file.write("Начальный пункт: " + message.text + '\n')
    file.close()
    final_point = bot.send_message(message.from_user.id, 'Введите конечную точку поездки (куда)')
    bot.register_next_step_handler(final_point, save_final_point)


def save_final_point(message):
    file = open("data/data.txt", "a")
    file.write("Конечный пункт: " + message.text + '\n')
    file.close()
    optional_information = bot.send_message(message.from_user.id,
                                            'Введите дополнительное сообщения для водителя\n<i>(если не нужно напишите: -)</i>',
                                            parse_mode="html")
    bot.register_next_step_handler(optional_information, save_optional_information)


def save_optional_information(message):
    file = open("data/data.txt", "a")
    file.write("Дополнительная информация: "  + message.text + '\n\n')
    file.close()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Подать заявку', 'Связаться с водителем')
    bot.send_message(message.from_user.id, 'Спасибо, ваша заявка <b>принята</b>',parse_mode="html", reply_markup=markup)

bot.polling(none_stop=True)
