from datetime import datetime, timedelta
import csv
import re
import string
from difflib import SequenceMatcher
import db
import pandas as pd
import config
from telethon.sync import TelegramClient, errors
from telethon import TelegramClient
import logging
import table
logging.basicConfig(level=logging.ERROR) 

def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'[\U0001F600-\U0001F6FF]', '', text)
    text = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

async def get_day_posts(date_start, date_end):
    async with TelegramClient("my_session", config.API_ID, config.API_HASH, system_version='4.16.30-vxCUSTOM') as client:
        channel_name = "https://t.me/dragology"
        msg_date = None
        data_list = []
        today = datetime.now().date()
        yesterday = today - timedelta(days = 1)
        print("we are in def")
        if date_start == '0' and date_end == '0':
            period_start = yesterday 
            period_end = yesterday
            print("we find dates")
            print(period_start)
        elif date_start == '1' and date_end == '1':
            period_start = yesterday 
            period_end = yesterday
            print("we find dates")
            print(period_start)
        else:
            if isinstance(date_start, str):
                period_start = datetime.strptime(date_start, "%Y-%m-%d").date()
                period_end = datetime.strptime(date_end, "%Y-%m-%d").date()
                print(period_start)
                print(period_end)
                #period_start = yesterday 
                #period_end = yesterday
            else:
                period_start = date_start
                period_end = date_end
                print(period_start)
                print(period_end)
                #period_start = yesterday 
                #period_end = yesterday

        async for message in client.iter_messages(channel_name):
            message_date = message.date.date() + timedelta(hours=3)
            m_text = message.message
            if m_text:
                if period_start <= message_date <=period_end:
                    message_id = message.id
                    msg_date = message.date + timedelta(hours=3)
                    print(msg_date)
                    text = message.message
                    header = text[:text.find("\n")]
                    text = text.replace(header + "\n\n", "")
                    text = text.replace("\n", " ")
                    if text == "":
                        text = "Опрос" #парсер не собирает с них текст, возможно правильнее будет ввообще не отраажть их в статистике
                    message_views = message.views 
                    message_forwards = message.forwards
                    message_reactions = message.reactions
                    if message_reactions is not None:
                        total_reactions = sum(reaction.count for reaction in message_reactions.results)
                    else:
                        total_reactions = 0
                    try:
                        comments = await client.get_messages(channel_name, reply_to=message.id, limit=10000)
                        total_comments = len(comments)
                    except errors.FloodWaitError as e:
                        print(f"Waiting for {e.seconds} seconds due to flood wait.")
                        continue
                    except errors.MessageIdInvalidError:
                        print("The message ID used in the peer was invalid. The message might have been deleted or changed.")
                        continue
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        continue
                    data_list.append([message_id, msg_date, header, text, message_views,message_forwards, total_reactions, total_comments])
                elif period_start > message_date:
                    break   

        # my_chats = []

        # # с помощью функции client.iter_dialogs() можно итерироваться по диалогам
        # async for chat in client.iter_dialogs():
        #     # имя чата можно получить вот так:
        #     chat_name = chat.name
        #     my_chats.append(chat_name)

        # data_redact = []
        # chat_name = my_chats[0]
        # print(chat_name)
        # current_date = datetime.now()
        # not_current_date = current_date - timedelta(days=3)
        # async for message in client.iter_messages(chat_name):
        #     if message == "21496" and len(message) > 100:
        #         message_date = message.date.date() + timedelta(hours=3)
        #         m_text = message.message
        #         if m_text:
        #             if not_current_date <= message_date <=current_date:
        #                 message_id = message.id
        #                 msg_date = message.date + timedelta(hours=3)
        #                 print(msg_date)
        #                 text = message.message
        #                 header = text[:text.find("\n")]
        #                 text = text.replace(header + "\n\n", "")
        #                 text = text.replace("\n", " ")
        #                 author = message.author_username
                       
        #                 data_redact.append([message_id, msg_date, header, text, author])
        #             elif not_current_date > message_date:
        #                 break 


        
    # csv_file_path_2 = 'result_2.csv'
    # csv_header = ["ID","Message Date", "Header", "Text", "Author"]
    # with open(csv_file_path_2, 'w', newline='', encoding='utf-8') as csv_file:
    #     csv_writer = csv.writer(csv_file, delimiter=';')
    #     csv_writer.writerow(csv_header)
    #     for row in data_list:
    #         csv_writer.writerow(row)

    csv_file_path = 'result.csv'
    csv_header = ["ID","Message Date", "Header", "Text", "Views","Total Forwards", "Total Reactions", "Total Comments"]
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(csv_header)
        for row in data_list:
            csv_writer.writerow(row)
    

    return csv_file_path

def get_records_data():
    records = db.get_records_by_yesterday()
    data_list = []
    if records:
        for record in records:
            record_dict = {
                'post_message_id': record.post_message_id,
                'post_text': record.post_text,
                'author_username': record.author_username,
                'post_date': record.post_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            data_list.append(record_dict)
    return data_list

def similarity(text1, text2):
    matcher = SequenceMatcher(None, text1, text2)
    similarity_coefficient = matcher.ratio()

    return similarity_coefficient

def compare_dicts(dict1, dict2):
    result_dict = []
    i = 0
    print("все записиси из второго словаря:")
    print(dict2)
    for record1 in dict1:
        text1 = record1.get('Header', '')  +" "+ record1.get('Text', '') 
        text1 = preprocess_text(text1)
        print(f"{i}. \n {text1}")
        i = i+1
        for record2 in dict2:
            text2 = record2.get('post_text', '')
            text2 = preprocess_text(text2)

            # Вычисляем коэффициент схожести
            similarity_coefficient = similarity(text1, text2)
            if similarity_coefficient > 0.5:
                result_entry = {
                    'author_username': record2['author_username'],
                    'Header': record1['Header'],
                    'Post_link': record1["ID"],
                    'Total_Forwards': record1['Total Forwards'],
                    'Similarity_Coefficient': similarity_coefficient
                }
                result_dict.append(result_entry)
                print(result_entry)
                print()
                break
    return result_dict


def create_day_stat(file_name):
    df = pd.read_csv(file_name, delimiter=';')
    df_sorted = df.sort_values(by='Total Forwards', ascending=False)
    result_dict = df_sorted.to_dict(orient='records')

    db_data = get_records_data()
    result = compare_dicts(result_dict, db_data)
    sorted_results = sorted(result, key=lambda x: x['Total_Forwards'], reverse=True)
    top_five_results = sorted_results[:5]

    today = datetime.now().date()
    yesterday = today - timedelta(days = 1)
    formatted_date = yesterday.strftime("%d.%m")
    i = 1
    text = f"<b>Итоги {formatted_date}</b>\n\n"
    
    for item in top_five_results:
        if item['Total_Forwards'] >= 100:
            text += f"🔥 <a href = \"https://t.me/dragology/{item['Post_link']}\"> {item['Header']}</a> от @{item['author_username']} ({item['Total_Forwards']})\n\n" 
        else:
            text += f"{i}) <a href = \"https://t.me/dragology/{item['Post_link']}\"> {item['Header']}</a> от @{item['author_username']} ({item['Total_Forwards']})\n\n" 
        i=i+1
    work_with_table(sorted_results)
    return text

def work_with_table(sorted_results):
    author_post_count = {}
    for record in sorted_results:
        author_username = record['author_username']
        if author_username in author_post_count:
            author_post_count[author_username] += 1
        else:
            author_post_count[author_username] = 1

    current_date = datetime.now()
    yesterday = current_date - timedelta(days=1)
    formatted_date_day = yesterday.strftime("%d.%m")
    formatted_date_mounth = yesterday.strftime("%m.%Y")
    #table.Write_to_table_all(author_post_count, formatted_date_mounth, formatted_date_day)


def mounth_sum(file_name):
    df = pd.read_csv(file_name, delimiter=';', encoding="utf-8")
    # Сортировка по каждому показателю и выбор первых пяти записей
    top_by_views = df.sort_values(by='Views', ascending=False).head(5)
    top_by_forwards = df.sort_values(by='Total Forwards', ascending=False).head(5)
    top_by_reactions = df.sort_values(by='Total Reactions', ascending=False).head(5)
    top_by_comments = df.sort_values(by='Total Comments', ascending=False).head(5)

    dict_top_by_views = top_by_views[['ID', 'Header', 'Views']].to_dict(orient='records')
    dict_top_by_forwards = top_by_forwards[['ID','Header', 'Total Forwards']].to_dict(orient='records')
    dict_top_by_reactions = top_by_reactions[['ID','Header', 'Total Reactions']].to_dict(orient='records')
    dict_top_by_comments = top_by_comments[['ID','Header', 'Total Comments']].to_dict(orient='records')
   
    i = 1
    text = f"<b>Итоги за прошедший месяц!</b>\n\n"
    text += "<b>ТОП 5 по просмотрам:</b>\n"
    for item in dict_top_by_views:
        text += f"{i}) <a href = \"https://t.me/dragology/{item['ID']}\"> {item['Header']}</a> ({item['Views']})\n" 
        i=i+1
    i = 1
    text += "\n<b>ТОП 5 по репостам:</b>\n"
    for item in dict_top_by_forwards:
        text += f"{i}) <a href = \"https://t.me/dragology/{item['ID']}\"> {item['Header']}</a> ({item['Total Forwards']})\n" 
        i=i+1
    
    i = 1
    text += "\n<b>ТОП 5 по реакциям:</b>\n"
    for item in dict_top_by_reactions:
        text += f"{i}) <a href = \"https://t.me/dragology/{item['ID']}\"> {item['Header']}</a> ({item['Total Reactions']})\n" 
        i=i+1
    
    i = 1
    text += "\n<b>ТОП 5 по комментариям:</b>\n"
    for item in dict_top_by_comments:
        text += f"{i}) <a href = \"https://t.me/dragology/{item['ID']}\"> {item['Header']}</a> ({item['Total Comments']})\n" 
        i=i+1

    return text