from aiogram.utils.keyboard import InlineKeyboardBuilder
from main import MyCallback

Buttons_builder = InlineKeyboardBuilder()
Buttons_builder.button(text=f"Прошлый месяц (csv файл)", callback_data=MyCallback(Action = "last_mounth"))
Buttons_builder.button(text=f"Указать период (csv файл)", callback_data=MyCallback(Action = "period"))
Buttons_builder.button(text=f"Вчерашние итоги (в этот чат)", callback_data=MyCallback(Action = "test"))
Buttons_builder.adjust(1, 1,1)

YesNo_builder = InlineKeyboardBuilder()
YesNo_builder.button(text=f"Да", callback_data=MyCallback(Action = "Start_parse"))
YesNo_builder.button(text=f"Ввести заново", callback_data=MyCallback(Action = "period"))
YesNo_builder.button(text=f"Я передумал", callback_data=MyCallback(Action = "Stop_parse"))
Buttons_builder.adjust(1, 1,1)