from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, DateTime
import datetime

Base = declarative_base()

class New_posts(Base):
    __tablename__ = 'new_posts'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    post_message_id = Column(String(10))
    post_text = Column(String(700))
    author_username = Column(String(50))
    post_date = Column(DateTime, default=datetime.datetime.utcnow)