from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, Integer, Column, Date, Float
import os
import config

POSTGRES_BASE = config.settings.database_url

Base = declarative_base()
engine = create_engine(POSTGRES_BASE)
session = sessionmaker(bind=engine)


class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, unique=True)
    order_n = Column("заказ №", Integer)
    price_usd = Column("стоимость,$", Float)
    delivery_date = Column("срок поставки", Date)
    price_rub = Column("стоимость, руб", Float)


def create_table():
    Base.metadata.create_all(engine)
