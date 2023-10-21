import asyncio
import logging
import sys
from os import getenv
import json

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.types.web_app_info import WebAppInfo

TOKEN = getenv("TOKEN")

dp = Dispatcher()

def readStringFromFile(s):
	with open("strings.json", "r", encoding='utf-8') as fh:
		st = json.load(fh, )
		return st[s]

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
	'''
	kb = [
		[types.KeyboardButton(text='Открыть веб страницу', web_app=WebAppInfo(url='http://localhost:8000/'))]
	]
	markup = types.ReplyKeyboardMarkup(keyboard = kb)
	await message.answer(f"Hello, {hbold(message.from_user.full_name)}!", reply_markup=markup)'''
	res = readStringFromFile("hello")
	await message.answer(res)


@dp.message()
async def main_handler(message: types.Message) -> None:
	try:
		# Этапы приложения
		# 
		await message.send_copy(chat_id=message.chat.id)
	except TypeError:
		await message.answer("Nice try!")


async def main() -> None:
	bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
	await dp.start_polling(bot)


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, stream=sys.stdout)
	asyncio.run(main())