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
from aiogram.types.web_app_info import WebAppInfo
from sqlalchemy.sql.expression import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import hashlib

load_dotenv()
TOKEN = os.getenv("TOKEN")
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
dp = Dispatcher()
form_router = Router()
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(engine)

class PasStates(StatesGroup):
	AUTH = State()
	NEEDTRAIN = State()
	MARKET = State()

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
		[types.KeyboardButton(text='🔑Регистрация', web_app=WebAppInfo(url='https://127.0.0.1:5000/reg')), types.KeyboardButton(text='🚪Авторизация', web_app=WebAppInfo(url='https://127.0.0.1:5000/auth'))]
	]
	markup = types.ReplyKeyboardMarkup(row_width = 2, keyboard = kb)
	await message.answer(readStringFromFile("auth"), reply_markup=markup)

@form_router.message(PasStates.AUTH, (F.content_type.in_({'web_app_data'})))
async def from_auth_or_reg(message: Message, state: FSMContext) -> None:
	#!!! Получили данные из реги/ауфа, type говорит auth или reg
	with Session() as session:
		data = json.loads(message.web_app_data.data)
		db_response = ''
		if data['type'] == 'auth':
			hash_object = hashlib.md5(bytes(data['password'],'utf-8'))
			db_response = session.execute(func.dev.login(hash_object.hexdigest(),data['email'])).all()[0][0]
			if db_response != 'ok':
				await message.answer('lox')
				return
		if data['type'] == 'reg':
			hash_object = hashlib.md5(bytes(data['password'],'utf-8'))
			db_response = session.execute(func.dev.register(message.chat.id,hash_object.hexdigest(),data['email'])).all()[0][0]
			session.commit()
			if db_response != 'ok':
				await message.answer('lox')
				return
	await state.set_state(PasStates.NEEDTRAIN)
	await message.answer(message.web_app_data.data)
	await send_photo_handler(message)

@form_router.message(PasStates.AUTH)
async def need_auth(message: Message, state: FSMContext) -> None:
	await need_auth_mes(message)

@form_router.message(PasStates.NEEDTRAIN, (F.content_type.in_({'photo', "document"})))
async def need_train_mes(message: Message, state: FSMContext) -> None:
	#!!! Тут мы сожрали фотку или документ на шаги когда он нам нужен
	with Session() as session:
		train,wagon,place = '100',100,100
		db_response = session.execute(func.dev.add_ride(train,wagon,place,message.chat.id)).all()[0][0]
		if db_response != 'ok':
			await message.answer(db_response)
		session.commit()
	await state.set_state(PasStates.MARKET)
	await message.answer(readStringFromFile("find"))
	await send_market(message)

async def send_market(message: types.Message) -> None:
	kb = [
		[types.KeyboardButton(text='Маркет', web_app=WebAppInfo(url='https://127.0.0.1:5000/market'))]
	]
	markup = types.ReplyKeyboardMarkup(keyboard = kb)
	await message.answer(readStringFromFile("sucess"), reply_markup=markup)

async def send_photo_handler(message: types.Message) -> None:
	markup = types.ReplyKeyboardRemove()
	await message.answer(readStringFromFile("send_me"), reply_markup=markup)

@form_router.message(PasStates.MARKET, (F.content_type.in_({'web_app_data'})))
async def from_auth_or_reg(message: Message, state: FSMContext) -> None:
	await message.answer(message.web_app_data.data)

async def main() -> None:
	bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
	dp.include_router(form_router)
	await dp.start_polling(bot)

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, stream=sys.stdout)
	asyncio.run(main())