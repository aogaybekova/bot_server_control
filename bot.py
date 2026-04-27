import asyncio
from logic import *
import pandas as pd
import numpy as np
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import time
from aiogram.filters import Command, CommandObject
from aiogram.types import Chat, Message
import logging
from telegram.ext import Updater, CommandHandler
import sys
from aiogram import Bot, Dispatcher, types#, html, executor
import aioschedule
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import subprocess
import re
from sqlalchemy import create_engine, text
import gc
from aiogram.filters import Command
import os
users = []
user_id = my_userid
users_for_send = []
users_for_calls_send=[]
names = []
save_users_for_send = []
save_users_for_calls_send=[]

#------------------------------- тут объявляем бота----------------------#
bot = Bot(token="API_token",
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# --------------------------------тут команды----------------------------#

#тут пока заглушка
@dp.message(Command('restart'))
async def start_command(message):
    await message.reply("Чат перезапущен")

#старт
@dp.message(Command('start'))
async def start(message: Message):
    print(message.from_user.id, message.from_user.first_name)
    users.append(message.from_user.id)
    names.append(message.from_user.first_name)
    await message.reply("Привет! Я бот отдела рисков")

#регистрация на основную рассылку
@dp.message(Command('register'))
async def register(message: Message):
    print(message.from_user.id, message.from_user.first_name)
    users_for_send.append(message.from_user.id)
    names.append(message.from_user.first_name)
    save_users_for_send = list(dict.fromkeys(users_for_send))
    #await message.reply(message.from_user.id, message.from_user.first_name)
    await message.reply("Теперь вы будите получать рассылку")
    print('users_for_send', users_for_send)
    print('save_users_for_send', save_users_for_send)

    return users_for_send

#отмена регистрации на основную рассылку
@dp.message(Command('cancel_register'))
async def cancel_register(message: Message):
    print(message.from_user.id, message.from_user.first_name)
    users_for_send.remove(message.from_user.id)
    # names.append(message.from_user.first_name)
    save_users_for_send = list(dict.fromkeys(users_for_send))
    #await message.reply(message.from_user.id, message.from_user.first_name)
    await message.reply("Теперь вы не будите получать рассылку")
    print('users_for_send', users_for_send)
    print('save_users_for_send', save_users_for_send)

    return users_for_send

#регистрация на звонки
@dp.message(Command('register_calls'))
async def register_calls(message: Message):
    print(message.from_user.id, message.from_user.first_name)
    users_for_calls_send.append(message.from_user.id)
    names.append(message.from_user.first_name)
    save_users_for_calls_send = list(dict.fromkeys(users_for_calls_send))
    #await message.reply(message.from_user.id, message.from_user.first_name)
    await message.reply("Теперь вы будите получать рассылку по звонкам")
    print('users_for_calls_send', users_for_calls_send)

    return users_for_calls_send

#отмена регистрации на основную рассылку
@dp.message(Command('cancel_call'))
async def cancel_call(message: Message):
    print(message.from_user.id, message.from_user.first_name)
    users_for_calls_send.remove(message.from_user.id)
    # names.append(message.from_user.first_name)
    save_users_for_calls_send = list(dict.fromkeys(users_for_calls_send))
    #await message.reply(message.from_user.id, message.from_user.first_name)
    await message.reply("Теперь вы не будите получать рассылку")
    print('users_for_send', users_for_calls_send)
    print('save_users_for_send', save_users_for_calls_send)

    return users_for_calls_send

#ссыло4ка на мониторинг
@dp.message(Command('info_monitoring'))
async def info_mon(message: Message):
    await message.reply("https://huggingface.co/spaces/picklecucumber/monitoring")

#ссыло4ка на разведение потоков
@dp.message(Command('info_stream_branching'))
async def info_branch(message: Message):
    await message.reply("https://www.figma.com/deck/kQ5bwvIjSYkdvg1yZ0xPkS/Customer-segmentation-models-presentation?node-id=1-1196&node-type=canvas&t=7ykCiSNbdD8CDEgD-1&scaling=min-zoom&content-scaling=fixed&page-id=0%3A1")

#последняя заявка
@dp.message(Command('last_apps'))
async def start_command(message):
    data = new_data()
    await message.answer('последняя прошедшая заявка')
    await message.answer(data.loc[0].to_string())

#последние 5 заявок
@dp.message(Command('last_five_apps'))
async def start_command(message):
    data = new_data()
    await message.answer('Последние прошедшие заявки')
    await message.answer(data.to_string())

#проблемные звонки коллекторов
@dp.message(Command('problem_calls'))
async def start_command(message):
    df = collector_calls()
    await message.answer('Звонки с нарушениями за вчера')

    if df.shape[0] == 1:
        await message.answer(df.loc[0].to_string())
    else:
        for i in range(df.shape[0]):
            await message.answer(df.loc[i].to_string())
            await message.answer('--------------------')

#pdn
@dp.message(Command('pdn'))
async def PDN(message):
    cutoff=0.03
    pdn50 = PDN_50_80()
    pdn80 = PDN_80()
    if (pdn50>cutoff)|(pdn50==cutoff):
        await message.reply((f"PDN50-80 ={pdn50} .Превышение на {round(pdn50-cutoff, 3)} за последние 3 дня"))
    else:
        await message.reply((f"PDN50-80 = {pdn50} . В норме за последние 3 дня"))
    if (pdn80>cutoff)|(pdn80==cutoff):
        await message.reply((f"PDN80+ = {pdn80} .Превышение на {round(pdn80-cutoff, 3)} за последние 3 дня"))
    else:
        await message.reply((f"PDN80+ = {pdn80} . В норме за последние 3 дня"))

@dp.message(Command('service'))
async def Service(message):
    data_OK, data_time =services()

    # df в строку
    def format_dataframe_to_string(df):
        table_string = df.to_string(index=False)
        return f"<pre>{table_string}</pre>"

    formatted_table0 = format_dataframe_to_string(data_OK.loc[data_OK['Процент ОК']<90][['ExternalServiceName','Процент ОК', 'Процент TIMEOUT']])
    formatted_table1 = format_dataframe_to_string(data_time.loc[data_time.avg_sec>data_time.avg_sec_month])

    await message.answer(formatted_table0, parse_mode=ParseMode.HTML)
    await message.answer(formatted_table1, parse_mode=ParseMode.HTML)


@dp.message(Command('all_service'))
async def all_Service(message):
    data_OK, data_time =services()

    # Конвертируем DataFrame в форматированную строку
    def format_dataframe_to_string(df):
        table_string = df.to_string(index=False)
        return f"<pre>{table_string}</pre>"

    # Отправляем сообщение
    formatted_table0 = format_dataframe_to_string(data_OK[['ExternalServiceName','Процент ОК', 'Процент ERROR','Процент TIMEOUT']])
    formatted_table1 = format_dataframe_to_string(data_time)

    await message.answer(formatted_table0, parse_mode=ParseMode.HTML)
    await message.answer(formatted_table1, parse_mode=ParseMode.HTML)


@dp.message(Command('tasklist'))
async def echo_handler(message: Message) -> None:
    try:
        await message.answer(subprocess.getoutput('docker ps --format json'))
    except TypeError:
        await message.answer("Nice cock!")

@dp.message(Command('start_consoles'))
async def start_consoles(message):
    try:
        command = 'docker-compose up -d prod_antifraud prod_nerez prod_repeated prod_crimea prod_all'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        await message.answer(output if output.strip() else "Контейнеры запущены")
    except Exception as e:
        await message.answer(f"Ошибка при запуске контейнеров: {e}")

# перезапуск моделек
@dp.message(Command('restart_consoles'))
async def restart_consoles(message):
    try:
        command = 'docker-compose restart prod_antifraud prod_nerez prod_repeated prod_crimea prod_all'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        await message.answer(output if output.strip() else "Контейнеры перезапущены")
    except Exception as e:
        await message.answer(f"Ошибка при перезапуске контейнеров: {e}")


@dp.message(Command('ping'))
async def send_pong(message):
    pong=""
    hostname0='192.168.20.81'
    hostname1='192.168.20.82'
    response = os.system('ping ' + hostname0)
    response1 = os.system('ping ' + hostname1)
    if (response == 0)&(response1 == 0):
        pong=(str(hostname0)+' & ' +str(hostname1)+' is up')

    elif (response == 0)&(response1 != 0):
        pong = (str(hostname0) + ' is up'+' & '+str(hostname1) + ' is down')

    elif (response != 0)&(response1 == 0):
        pong = (str(hostname0) + ' is down'+' & '+str(hostname1) + ' is up')

    else:
        pong=( str(hostname0)+' & ' +str(hostname1)+' is down')

    await message.reply(pong)

#проверка работы моделей
@dp.message(Command('check'))
async def check_anyway(message):
    s = crash_process()
    if len(s) !=0:
        try:
            await message.answer(text=f"Упала консолька")
            for i in range(len(s)):
                await message.answer(text=s[i].to_string())
        except Exception as e:
            print(e)
    else: await message.answer(text=f"Все работает")
def exec_cmd(command):
    try:
        sub_ = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        subprocess_return = sub_.stdout.read()
        return subprocess_return
    except:
        return "Nice cock!"


@dp.message(Command("cmd"))
async def cmd_set(message: Message,command: CommandObject):
    if (user_id == message.chat.id): #проверяем, что пишет именно владелец

        # Пробуем разделить аргументы на две части по первому встречному пробелу
        if command.args is None:
            await message.answer("Ошибка: не переданы аргументы")
        else:
            try:
                print('command.args.split(" ")', command.args.split(" "))
                command_to = command.args.split(" ")
                command_to_cmd = " ".join(str(element) for element in command_to)
                p = exec_cmd(command_to_cmd)#.decode('utf8')
                print(p[:4096])
                if len(p) > 4096:
                    await message.answer(p[:1488])
                else:
                    await message.answer(p)
            # Если получилось меньше двух частей, вылетит ValueError
            except:
                await message.answer(
                    "Ошибка: неправильный формат команды. Пример:\n"
                    "/cmd <message>"
                )
                return
    else:
        await message.answer(f"У юзера {message.chat.id} нет прав доступа")


"""------------------рассылка-------------------------"""

async def report0():
    data_OK, data_time =services()

    # df в форматированную строку
    def format_dataframe_to_string(df):
        table_string = df.to_string(index=False)
        return f"<pre>{table_string}</pre>"

    formatted_table0 = format_dataframe_to_string(data_OK.loc[data_OK['Процент ОК']<90][['ExternalServiceName','Процент ОК','Процент TIMEOUT']])
    formatted_table1 = format_dataframe_to_string(data_time.loc[data_time.avg_sec>data_time.avg_sec_month])

    if data_OK.loc[data_OK['Процент ОК']<90].shape[0] != 0:
        for user in users_for_send:
            try:
                await bot.send_message(chat_id=user, text=formatted_table0)
                await bot.send_message(chat_id=user, text=formatted_table1)
            except Exception as e:
                print(e)
    else:
        for user in users_for_send:
            try:
                await bot.send_message(chat_id=user, text=f"Нет задержек по сервисам")
            except Exception as e:
                print(e)

    text0, text1 = pdn_for_report()
    for user in users_for_send:
        try:
            await bot.send_message(chat_id=user, text=text1)
            await bot.send_message(chat_id=user, text=text0)
        except Exception as e:
            print(e)


#попытка репортинга коллекторов
async def report1():
    df = collector_calls()
    if df.shape[0] > 1:
        for user in users_for_calls_send:
            try:
                await bot.send_message(chat_id=user, text=f"Звонки с нарушениями за вчера")
                for i in range(df.shape[0]):
                    await bot.send_message(chat_id=user, text=df.loc[i].to_string())
                    await bot.send_message(chat_id=user, text=f"--------------------")
            except Exception as e:
                print(e)

    elif df.shape[0] == 1:
        for user in users_for_calls_send:
            try:
                print(user)
                await bot.send_message(chat_id=user, text=f"Звонок с нарушениями за вчера")
                await bot.send_message(chat_id=user, text=df.loc[0].to_string())
            except Exception as e:
                print(e)
    else:
        for user in users_for_calls_send:
            try:
                print(user)
                await bot.send_message(chat_id=user, text=f"Нет звонков с нарушениями за вчера")
            except Exception as e:
                print(e)

#проверка не упалили консоли
async def check():
    s = crash_process()
    if len(s) !=0:
        try:
            await bot.send_message(chat_id=505568035, text=f"Упала консолька")
            for i in s:
                await bot.send_message(chat_id=505568035, text=i.to_string())
        except Exception as e:
            print(e)




async def main() -> None:


    # диспетчеризация событий запуска
    scheduler = AsyncIOScheduler()
    timezone="Europe/Moscow"

    scheduler.add_job(report0, trigger="cron", hour=10, minute=00, start_date=datetime.now())
    scheduler.add_job(report1, trigger="cron", hour=10, minute=10, start_date=datetime.now())
    scheduler.add_job(check, "interval", minutes=30)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    gc.collect()

