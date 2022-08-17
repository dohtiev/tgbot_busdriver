## -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
import os
from os.path import join, dirname
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import pygsheets

def get_from_env(key):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)

storage=MemoryStorage()

class FSMAdmin(StatesGroup):
    name = State()
    date = State()
    start = State()
    final = State()
    description = State()

bot = Bot(token=get_from_env("TELEGRAM_BOT_TOKEN"),  parse_mode=types.ParseMode.HTML)
driver_number = get_from_env("driver_number")
driver_telegram = get_from_env("driver_telegram")
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_button = ['Подать заявку', 'Связаться с водителем']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_button)

    await message.answer('Выбери необходимую операцию', reply_markup=keyboard)

@dp.message_handler(Text(equals='Подать заявку'), state=None)
async def cm_start(message: types.Message):
    await FSMAdmin.name.set()
    await message.answer('Напиши свое имя и фамилию')

@dp.message_handler(state=FSMAdmin.name)
async def save_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await message.answer('Напиши дату поездки')

@dp.message_handler(state=FSMAdmin.date)
async def save_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text
    await FSMAdmin.next()
    await message.answer('Напиши начальную точку поездки <i>(откуда)</i>')

@dp.message_handler(state=FSMAdmin.start)
async def save_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['start'] = message.text
    await FSMAdmin.next()
    await message.answer('Напиши конечную точку поездки <i>(куда)</i>')

@dp.message_handler(state=FSMAdmin.final)
async def save_final(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['final'] = message.text
    await FSMAdmin.next()
    await message.answer('Напиши дополнительную информацию <i>(если нужно)</i>')

@dp.message_handler(state=FSMAdmin.description)
async def save_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

    async with state.proxy() as data:
        # file = open('users_data.txt', 'a')
        # for key, value in data.items():
        #     file.write(f'{key}: {value}\n')
        # file.write(f'\n')
        # file.close()
        await message.answer(f"<i>Ваша заявка принята</i>\nИмя и фамилия: <b>{data['name']}</b>,\n"
                             f"Дата поездки: <b>{data['date']}</b>,\n"
                             f"Начальная точка: <b>{data['start']}</b>,\n"
                             f"Конечная точка: <b>{data['final']}</b>,\n"
                             f"Дополнительная информация: <b>{data['description']}</b>,\n"
                             f"<i>Спасибо за обращение</i>")

    gc = pygsheets.authorize(service_file=get_from_env("path_to_credentials"))
    sht1 = gc.open_by_key(get_from_env("sheet_key"))
    wks = sht1.sheet1
    data_for_sheet = [[data['name']], [data['date']], [data['start']], [data['final']], [data['description']]]
    wks.append_table(values=data_for_sheet, start='A2', end=None, dimension='COLUMNS', overwrite=False)
    # print(wks.get_values('A2','E2'))
    await state.finish()

@dp.message_handler(Text(equals='Связаться с водителем'))
async def get_info(message: types.Message):
    driver_info=f'Номер телефона водителя: <b>{driver_number}</b>\nТелеграмм водителя: <b>@{driver_telegram}</b>'
    await message.answer(driver_info)
def main():
    executor.start_polling(dp)

if __name__ == '__main__':
    main()
