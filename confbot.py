from aiogram import Bot, Dispatcher, F
import config

bot = Bot(config.token_api, parse_mode="HTML")
dispatcher = Dispatcher()
