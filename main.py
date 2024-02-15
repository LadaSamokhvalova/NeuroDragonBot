import asyncio
from datetime import datetime, timedelta
from telegram import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from telethon import TelegramClient
import config
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import db
import aioschedule
import function
from aiogram.types import FSInputFile
import boards
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

bot = Bot(config.token_api, parse_mode="HTML")
dp = Dispatcher()

class MyCallback(CallbackData, prefix="my"):
    Action: str

class Form(StatesGroup):
    period_start = State()
    period_end = State()


async def get_day_result(bot: TelegramClient) -> None:
    try:
        await bot.send_message(chat_id=config.Lada_chat_id, text="Сейчас пришлю файл статистики за день")
        file_path = await function.get_day_posts('0', '0')
        file = FSInputFile(file_path)
        await bot.send_document(chat_id = config.Lada_chat_id, document=file, caption="Вот он файл за день прошедший")
        result = function.create_day_stat(file_path)
        await bot.send_message(chat_id=config.Lada_chat_id, text=result, disable_web_page_preview = True)
        await bot.send_message(chat_id=config.redac_caht_id, message_thread_id = "25532", text=result, disable_web_page_preview = True)
        today = datetime.now().date()
        if today.day == 1:
            last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_month_end = today.replace(day=1) - timedelta(days=1)
            await bot.send_message(chat_id=config.Lada_chat_id,
                                        text = f"Начинаю сбор данных. Может занять 10-30 минут.\n\nбудут собранны данные с {last_month_start} до {last_month_end}",
                                    )
            file_path = await function.get_day_posts(last_month_start, last_month_end)
            file = FSInputFile(file_path, "Месяц.csv")
            await bot.send_document(chat_id = config.Lada_chat_id, document=file, caption="Готово")
            answer_text = function.mounth_sum(file_path)
            await bot.send_message(chat_id=config.Lada_chat_id,
                                        text = answer_text
                                        , disable_web_page_preview = True)
            await bot.send_message(chat_id=config.redac_caht_id, 
                                   message_thread_id = "25532",
                                    text = answer_text
                                    , disable_web_page_preview = True)

    except Exception as e:
        print(f"Error sending daily results: {e}")
        await bot.send_message(chat_id=config.Lada_chat_id, text="Произошла ошибка при отправке статистики")

async def scheduler():
    aioschedule.every().day.at("00:03").do(get_day_result, bot)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(30)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    print("hi") 
    today  = datetime.now().time()
    if message.from_user.username == "BABAZANNA":
        await message.answer(f"Мяу-чи-ки-ряу, сейчас на сервере {today}", 
                            reply_markup=boards.Buttons_builder.as_markup())

@dp.message()
async def message_hendler(message: Message) -> None:
    if str(message.message_thread_id) == "21496":
        if  message.text == "Бот?" and str(message.from_user.id) == config.Lada_chat_id:
            await message.reply("Работаю. Принимаю сообщения только тут") 
        else:
            if message.text != None or message.caption != None:
                if message.text != None and len(message.text) > 100:
                    db.create_record(message.message_id, message.text, message.from_user.username, message.date+ timedelta(hours=3))
                elif message.caption != None and len(message.caption) > 100:
                    db.create_record(message.message_id, message.caption, message.from_user.username, message.date+ timedelta(hours=3))
    elif str(message.message_thread_id) == "25532":
        if  message.text == "Бот?" and str(message.from_user.id) == config.Lada_chat_id:
            await message.reply("мы в топике Итоги")
            print(message.chat.id) 

@dp.callback_query(MyCallback.filter(F.Action == "test"))
async def my_callback_last_mounth(query: CallbackQuery):
    await query.answer()
    await bot.send_message(chat_id=config.Lada_chat_id, text="Вы в тестовом режиме. Сейчас пришлю файл статистики за день")
    file_path = await function.get_day_posts('0', '0')
    file = FSInputFile(file_path)
    await bot.send_document(chat_id = config.Lada_chat_id, document=file, caption="Вот он файл за день прошедший")
    result = function.create_day_stat(file_path)
    await bot.send_message(chat_id=config.Lada_chat_id, text=result, disable_web_page_preview = True)
    


@dp.callback_query(MyCallback.filter(F.Action == "last_mounth"))
async def my_callback_last_mounth(query: CallbackQuery, callback_data: MyCallback):
    await query.answer()
    today = datetime.now().date()
    last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_end = today.replace(day=1) - timedelta(days=1)
    await bot.send_message(chat_id=query.from_user.id,
                                text = f"Начинаю сбор данных. Может занять 10-30 минут.\n\nбудут собранны данные с {last_month_start} до {last_month_end}",
                               )
    file_path = await function.get_day_posts(last_month_start,last_month_end)
    file = FSInputFile(file_path, "Месяц.csv")
    await bot.send_document(chat_id = query.from_user.id, document=file, caption="Готово")
    answer_text = function.mounth_sum(file_path)
    await bot.send_message(chat_id=query.from_user.id,
                                text = answer_text)


@dp.callback_query(MyCallback.filter(F.Action == "period"))
async def my_callback_period(query: CallbackQuery, callback_data: MyCallback, state : FSMContext):
    await query.answer()
    await bot.send_message(chat_id=query.from_user.id,
                                text = f"Пришлите дату <b>начала</b> периода.\n\n(пример: \"2024-01-24\")")
    await state.set_state(Form.period_start)

@dp.message(Form.period_start)
async def message_start_period_hendler(message: Message, state: FSMContext) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                                text = f"Пришлите дату <b>конца</b> периода.\n\n(пример: \"2024-01-24\")")
    await state.update_data(start = message.text) 
    
    await state.set_state(Form.period_end)

@dp.message(Form.period_end)
async def message_start_t_period_hendler(message: Message, state: FSMContext) -> None:
    await state.update_data(end = message.text) 
    data = await state.get_data()
    await bot.send_message(chat_id=message.from_user.id,
                                text = f"Будут собраны данные с {data['start']} по {data['end']}. Начать?",
                                reply_markup=boards.YesNo_builder.as_markup())

    
@dp.callback_query(MyCallback.filter(F.Action == "Start_parse"))
async def my_callback_age(query: CallbackQuery, callback_data: MyCallback, state : FSMContext):
    await query.answer()
    data = await state.get_data()
    await bot.send_message(chat_id=query.from_user.id,
                                text = f"Начинаю сбор данных. Может длится долго.\n\nбудут собранны данные с {data['start']} по {data['end']}",
                               )
    file_path = await function.get_day_posts(data['start'],data['end'])
    file = FSInputFile(file_path, "Период.csv")
    await bot.send_document(chat_id = query.from_user.id, document=file, caption="Готово")

async def main() -> None:
    try:        
        await bot.send_message(chat_id=config.Lada_chat_id, text="Работаю")
        await asyncio.gather(dp.start_polling(bot, skip_updates=True), scheduler())

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        await bot.send_message(chat_id=config.Lada_chat_id, text=f"При запуске произошла ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
                