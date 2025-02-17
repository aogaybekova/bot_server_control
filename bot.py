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
from aiogram import Bot, Dispatcher#, html, executor
import aioschedule
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import subprocess
from sqlalchemy import create_engine, text
import gc
from aiogram.filters import Command

import os
users = []
user_id = id
users_for_send = []
names = []
save_users_for_send = []


#------------------------------- тут объявляем бота----------------------#
bot = Bot(token="api-token", default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# --------------------------------тут команды----------------------------#

#тут пока заглушка
@dp.message(Command('restart'))
async def start_command(message):
    await message.reply("Чат перезапущен")

@dp.message(Command('start'))
async def start(message: Message):
    print(message.from_user.id, message.from_user.first_name)
    users.append(message.from_user.id)
    names.append(message.from_user.first_name)
    await message.reply("Привет! Я бот отдела рисков")

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

    return save_users_for_send

@dp.message(Command('info_monitoring'))
async def info_mon(message: Message):
    await message.reply("https://huggingface.co/spaces/picklecucumber/monitoring")

@dp.message(Command('info_stream_branching'))
async def info_branch(message: Message):
    await message.reply("https://www.figma.com/deck/kQ5bwvIjSYkdvg1yZ0xPkS/Customer-segmentation-models-presentation?node-id=1-1196&node-type=canvas&t=7ykCiSNbdD8CDEgD-1&scaling=min-zoom&content-scaling=fixed&page-id=0%3A1")

@dp.message(Command('last_apps'))
async def start_command(message):
    data = new_data()
    await message.answer('последняя прошедшая заявка')
    await message.answer(data.loc[0].to_string())

@dp.message(Command('last_five_apps'))
async def start_command(message):
    data = new_data()
    await message.answer('Последние прошедшие заявки')
    await message.answer(data.to_string())


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
    data=services()
    if len(data.loc[data.flg.eq(True)])!=0:
        for i in data.loc[data.flg.eq(True)].iterrows():
            await message.answer(f"Задержка ответа по сервису:  " + str(data.loc[i[0], 'ExternalService']) + ". Ответ по сервису: " + str(round(data.loc[i[0], 'avg_sec'],2)) + ". Максимальное допустимое значение: " + str(data.loc[i[0], 'tresh']))

    else:
        await message.answer((f"Нет задержек по сервисам"))

@dp.message(Command('all_service'))
async def all_Service(message):
    data=services()
    await message.answer(data[['ExternalService', 'avg_sec', 'tresh']].to_string())


@dp.message(Command('tasklist'))
async def echo_handler(message: Message) -> None:
    """
     Обработчик перенаправит полученное сообщение обратно отправителю.

    По умолчанию обработчик сообщений обрабатывает все типы сообщений (например, текст, фотографию, стикер и т. д.).
    """
    try:
        await message.answer(subprocess.getoutput('wmic process where "name like "python%"" get processid,commandline'))

    except TypeError:
        await message.answer("Nice cock!")

@dp.message(Command('ping'))
async def send_pong(message):
    pong=""
    hostname0='localhost'
    hostname1='localhost2'
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
    data = services()
    if len(data.loc[data.flg.eq(True)]) != 0:
        for i in data.loc[data.flg.eq(True)].iterrows():
            try:
                for user in users_for_send:
                    print(user)
                    await bot.send_message(chat_id=user, text=f"Задержка ответа по сервису:  " + str(data.loc[i[0], 'ExternalService']) + ". Ответ по сервису: " + str(round(data.loc[i[0], 'avg_sec'], 2)) + " сек . Максимальное допустимое значение: " + str(data.loc[i[0], 'tresh'])+ " сек.")

            except Exception as e:
                print(users_for_send)
                print(e)
    else:
        try:
            for user in users_for_send:
                print(user)
                await bot.send_message(chat_id=user, text=f"Нет задержек по сервисам")

        except Exception as e:
            print(users_for_send)
            print(e)
    text0, text1 = pdn_for_report()
    try:
        for user in users_for_send:
            print(user)
            await bot.send_message(chat_id=user, text=text1)
            await bot.send_message(chat_id=user, text=text0)
    except Exception as e:
        print(users_for_send)
        print(e)
async def main() -> None:


    # диспетчеризация событий запуска
    scheduler = AsyncIOScheduler()
    timezone="Europe/Moscow"

    scheduler.add_job(report0, trigger="cron", hour=10, minute=30, start_date=datetime.now())

    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    gc.collect()

