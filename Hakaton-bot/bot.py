import asyncio
import logging
import sys
import os
import json
import re
from PIL import Image
import pytesseract
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.types.web_app_info import WebAppInfo
from img_proccesing import ImgProccessor

load_dotenv()
TOKEN = os.getenv("TOKEN")

dp = Dispatcher()

img_proccessor = ImgProccessor()

def readStringFromFile(s):
	with open("strings.json", "r", encoding='utf-8') as fh:
		st = json.load(fh, )
		return st[s]

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
	
	kb = [
		[types.KeyboardButton(text='Открыть веб страницу', web_app=WebAppInfo(url='https://127.0.0.1:5000'))]
	]
	markup = types.ReplyKeyboardMarkup(keyboard = kb)
	await message.answer(f"Hello, {hbold(message.from_user.full_name)}!", reply_markup=markup)
	#res = readStringFromFile("hello")
	#await message.answer(res)


@dp.message()
async def main_handler(message: types.Message) -> None:
	try:
		# Этапы приложения
		#
		#  
		if message.content_type == "photo":
			file_id = message.photo[0].file_id
			path = 'chat_'+str(message.chat.id)
			os.makedirs(path, exist_ok = True)
			await message.bot.download(message.photo[-1],os.path.join(path,'photo.png'))
			#data = img_proccessor.try_extract_data(os.path.join(path,'photo.png'))
			#await message.answer(json.dumps(data))
	except Exception as e:
		await message.answer(str(e))


async def main() -> None:
	bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
	await dp.start_polling(bot)


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, stream=sys.stdout)
	asyncio.run(main())