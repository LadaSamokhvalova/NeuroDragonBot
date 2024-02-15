from difflib import SequenceMatcher
import re
from datetime import datetime, timedelta
import string
import table

# def similarity(text1, text2):
#     matcher = SequenceMatcher(None, text1, text2)
#     similarity_coefficient = matcher.ratio()
#     return similarity_coefficient

# def preprocess_text(text):
#     text = text.lower()
#     text = text.translate(str.maketrans('', '', string.punctuation))
#     text = re.sub(r'[\U0001F600-\U0001F6FF]', '', text)
#     text = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', '', text)
#     text = re.sub(r'\s+', ' ', text).strip()
    
#     return text

# def compare_dicts():

#     text1 =  "Сегодня отмечается всемирный день «измените свой пароль»\n\nСуть праздника понятна из названия—чтобы отметить его, просто поменяйте пароли от своих аккаунтов, это повысит их безопасность и позволит не волноваться за злоумышленников, которые могут захотеть украсть ваш аккаунт.\n\nПоявился такой необычный праздник ещё в 2012 и нужен он, чтобы большее количество людей узнало о необходимости регулярно менять пароли."
#     text2 = "Суть праздника понятна из названия — чтобы отметить его, просто поменяйте пароли от всех своих аккаунтов, это повысит их безопасность и позволит не волноваться насчёт злоумышленников, которые могут захотеть украсть ваш аккаунт.  Появился такой необычный праздник ещё в 2012. Его цель, чтобы большее количество людей узнало о необходимости регулярно обновлять пароли. Главное потом не забудьте их!"
#     # Вычисляем коэффициент схожести
#     print(preprocess_text(text1))
#     print()
#     print(preprocess_text(text2))

#     similarity_coefficient = similarity(preprocess_text(text1), preprocess_text(text2))
#     print(similarity_coefficient)
            
# compare_dicts()
# today = datetime.now() 
# yesterday = datetime.now() - timedelta(days=3)
# yesterday_str = yesterday.strftime('%Y-%m-%d %H:%M:%S')
# print(today)
# print(yesterday_str)

current_date = datetime.now()
yesterday = current_date - timedelta(days=1)
formatted_date_day = yesterday.strftime("%d.%m")
formatted_date_mounth = yesterday.strftime("%m.%Y")

print(formatted_date_day)
table.Write_to_table_all(formatted_date_mounth, formatted_date_day)