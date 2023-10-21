import asyncio
import logging
import sys
import os
import json
#import pytesseract
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router,  F, types

from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

load_dotenv()
TOKEN = os.getenv("TOKEN")
form_router = Router()

class PasStates(StatesGroup):
	AUTH = State()
	NEEDTRAIN = State()

def readStringFromFile(s):
	with open("Hakaton-bot\strings.json", "r", encoding='utf-8') as fh:
		st = json.load(fh, )
		return st[s]

@form_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
	await state.set_state(PasStates.AUTH)
	res = readStringFromFile("hello")
	cat = FSInputFile('Hakaton-bot\\images\\train.jpg')
	await message.answer_photo(cat, caption=res)
	await need_auth_mes(message)

async def need_auth_mes(message: Message) -> None:
	kb = [
		[types.KeyboardButton(text='Регистрация')],
		[types.KeyboardButton(text='Авторизация')]
	]
	markup = types.ReplyKeyboardMarkup(keyboard = kb)
	await message.answer(readStringFromFile("auth"), reply_markup=markup)

@form_router.message(PasStates.AUTH)
async def need_auth(message: Message, state: FSMContext) -> None:
	await need_auth_mes(message)

async def send_photo_handler(message: types.Message) -> None:
	await message.answer(readStringFromFile("send_me"))

async def main() -> None:
	bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
	dp = Dispatcher()
	dp.include_router(form_router)
	await dp.start_polling(bot)


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, stream=sys.stdout)
	asyncio.run(main())