from datetime import datetime, timedelta
import csv
import re
import string
from difflib import SequenceMatcher
import pandas as pd
import config
from telethon.sync import errors
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
        my_chats = []
        authors_dict = {}
        data_redact_list = []
        channel_name = "https://t.me/dragology"
        msg_date = None
        data_list = []
        today = datetime.now().date()
        yesterday = today - timedelta(days = 1)

        if date_start == '0' and date_end == '0': # для ежедневных вызовов
            
            period_start = yesterday 
            period_end = yesterday

            async for chat in client.iter_dialogs():
                chat_name = chat.name
                my_chats.append(chat_name)

            users = await client.get_participants(my_chats[0])  
            for user in users:
                user_id = user.id
                user_username = user.username
                authors_dict[user_id] = user_username

            message_period_end = today
            message_period_start = today - timedelta(days = 3)
            async for message in client.iter_messages(my_chats[0]):
                message_date = message.date.date() + timedelta(hours=3)
                m_text = message.message
                if m_text:
                    if len(m_text) > 50:
                        if message_period_start <= message_date <=message_period_end:
                            message_id = message.id
                            msg_date = message.date + timedelta(hours=3)
                            text = message.message
                            message_author_id = message.from_id.user_id
                            message_author = authors_dict[message_author_id]
                            data_redact_list.append([message_id, msg_date, text, message_author])
                        elif message_period_start > message_date:
                            break

        else:   # для ручного ввода или прошлого месяца
            if isinstance(date_start, str):
                period_start = datetime.strptime(date_start, "%Y-%m-%d").date()
                period_end = datetime.strptime(date_end, "%Y-%m-%d").date()
            else:
                period_start = date_start
                period_end = date_end

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

    csv_file_path_chat_messages = 'chat_messages.csv'
    csv_header = ["ID","Message Date", "Text", "Author"]
    with open(csv_file_path_chat_messages, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(csv_header)
        for row in data_redact_list:
            csv_writer.writerow(row)
                
    name_string = yesterday.strftime('%Y_%m_%d')
    csv_file_path_day_posts= f'day_posts_{name_string}.csv'
    csv_header = ["ID","Message Date", "Header", "Text", "Views","Total Forwards", "Total Reactions", "Total Comments"]
    with open(csv_file_path_day_posts, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(csv_header)
        for row in data_list:
            csv_writer.writerow(row)
    
    return csv_file_path_day_posts, csv_file_path_chat_messages

def similarity(text1, text2):
    matcher = SequenceMatcher(None, text1, text2)
    similarity_coefficient = matcher.ratio()

    return similarity_coefficient

def compare_dicts(dict1, dict2):
    result_dict = []
    for record1 in dict1:
        text1 = record1.get('Header', '')  +" "+ record1.get('Text', '') 
        text1 = preprocess_text(text1)
        for record2 in dict2:
            text2 = record2.get('Text', '')
            text2 = preprocess_text(text2)

            similarity_coefficient = similarity(text1, text2)
            if similarity_coefficient > 0.7:
                result_entry = {
                    'author_username': record2['Author'],
                    'Header': record1['Header'],
                    'Post_link': record1["ID"],
                    'Total_Forwards': record1['Total Forwards'],
                    'Similarity_Coefficient': similarity_coefficient
                }
                result_dict.append(result_entry)
                break
    return result_dict


def create_day_stat(day_posts, chat_messages):
    df_post = pd.read_csv(day_posts, delimiter=';')
    df_sorted = df_post.sort_values(by='Total Forwards', ascending=False)
    result_posts_dict = df_sorted.to_dict(orient='records')

    df_messages = pd.read_csv(chat_messages, delimiter=';')
    result_messages_dict = df_messages.to_dict(orient='records')

    result = compare_dicts(result_posts_dict, result_messages_dict)

    sorted_results = sorted(result, key=lambda x: x['Total_Forwards'], reverse=True)
    top_five_results = sorted_results[:5]

    today = datetime.now().date()
    yesterday = today - timedelta(days = 1)
    formatted_date = yesterday.strftime("%d.%m")
    i = 1
    text = f"<b>Итоги {formatted_date}</b>\n\n"
    
    for item in top_five_results:
        item["Header"] = item["Header"].replace("ё", "e")
        header = re.sub('[^\x00-\x7Fа-яА-Я]', '', item["Header"])
        if item['Total_Forwards'] >= 100:
            text += f"🔥 <a href = \"https://t.me/dragology/{item['Post_link']}\"> {header}</a> от @{item['author_username']} ({item['Total_Forwards']})\n\n" 
        else:
            text += f"{i}) <a href = \"https://t.me/dragology/{item['Post_link']}\"> {header}</a> от @{item['author_username']} ({item['Total_Forwards']})\n\n" 
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
    table.Write_to_table_all(author_post_count, formatted_date_mounth, formatted_date_day)


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
