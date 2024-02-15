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

    author_mapping = {
         'FNAFGOD':'Лера (FNAFGOD)',
         'romanserevreymac':'Роман (romanserevreymac)',
         'KriJolt':'Егор (KriJolt)',
         'Paradirererere':'Даер (Paradirererere)',
         'travis_bickle_76':'Артем (travis_bickle_76)',
         'egzoll':'Егор (egzoll)',
         'plachacwa':'Placheta? R. M.? (plachacwa)',
         'dragondocx': 'Влад (dragondocx)'
    }
    start_col = column_index 

    # Вставляем данные в таблицу
    for google_sheets_author, post_count in data.items():
            author = author_mapping[google_sheets_author]
            cell = worksheet.find(author)
            row_index = cell.row
            worksheet.update_cell(row_index, start_col, post_count)

   