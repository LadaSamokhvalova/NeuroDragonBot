import gspread 
from google.oauth2 import service_account
from googleapiclient.discovery import build


import config

SCOPES = ['https,//www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = config.SERVICE_ACCOUNT_FILE
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)
gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
sh = gc.open_by_key(config.google_sheet_id) 

def Write_to_table_all(data, date_mounth, date_day):
    worksheet = sh.worksheet(date_mounth)
    column_index = worksheet.find(date_day).col

    author_list = worksheet.col_values(1)
    day_col = column_index 

    # Вставляем данные в таблицу
    for google_sheets_author, post_count in data.items():
            for index, element in enumerate(author_list):
               if google_sheets_author in element:
                    row_index = index+1
                    worksheet.update_cell(row_index, day_col, post_count)
                    break

   