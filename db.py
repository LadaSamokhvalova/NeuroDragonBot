from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from  New_posts import New_posts

# Создаем соединение с базой данных
engine = create_engine('sqlite:///dragondb.db', echo=True)
Session = sessionmaker(bind=engine)


def create_record(msg_id, p_text, username, msg_date):
    try:
        # Создаем сессию
        with Session() as session:
            # Добавляем данные в базу данных
            new_record = New_posts(post_message_id=msg_id, post_text=p_text, author_username=username, post_date = msg_date)
            session.add(new_record)
            session.commit()
    except Exception as e:
        print(f"Произошла ошибка при добавлении записи в базу данных: {e}")

def get_records_by_yesterday():
    try:
        yesterday = datetime.now() - timedelta(days=3)
        yesterday_str = yesterday.strftime('%Y-%m-%d %H:%M:%S')

        with Session() as session:
            records = session.query(New_posts).filter(New_posts.post_date >= yesterday_str).all()
            return records

    except Exception as e:
        print(f"Произошла ошибка при запросе записей из базы данных: {e}")
        return None