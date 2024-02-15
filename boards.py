from aiogram.utils.keyboard import InlineKeyboardBuilder
from main import MyCallback

Buttons_builder = InlineKeyboardBuilder()
Buttons_builder.button(text=f"(файл)Статистика за прошлый месяц", callback_data=MyCallback(Action = "last_mounth"))
Buttons_builder.button(text=f"(не работает)Указать период", callback_data=MyCallback(Action = "__period"))
Buttons_builder.button(text=f"Тестовое для Лады", callback_data=MyCallback(Action = "test"))
Buttons_builder.adjust(1, 1)

YesNo_builder = InlineKeyboardBuilder()
YesNo_builder.button(text=f"Да", callback_data=MyCallback(Action = "Start_parse"))
YesNo_builder.button(text=f"Ввести заново", callback_data=MyCallback(Action = "period"))
Buttons_builder.adjust(1, 1)