from __future__ import print_function

import logging
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from deepdiff import DeepDiff
from datetime import datetime, timedelta
import time
import re

import config
from db import Orders, session
from usd_to_rub import convert
from bot import send_notice


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = config.settings.spreadsheet_id
RANGE_NAME = config.settings.range_name

NOTIFICATION_TIME = datetime.now()
DELTA = timedelta(hours=0)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

s = session()

def get_sheet_data():
    '''
    Аyтентификация пользователя,
    если пользователь не авторизован
    он будет перенаправлен на страницу для авторизации,
    будет создан токен
    '''
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    '''
    Получение данных из таблицы Google и возврат данных в виде  списка словарей
    '''

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])

        data_list = []

        if not values:
            print('No data found.')
            return data_list

        for row in values:
            data_list.append(
                {
                    "id": int(row[0]), "order_n": int(row[1]), "price_usd": float(row[2]),
                    "delivery_date": datetime.strptime(row[3], "%d.%m.%Y").date(),
                }
            )
        return data_list
    except HttpError as err:
        print(err)


def check_dates(data_list):

    today_date = datetime.now().date()

    for el in data_list:
        if el['delivery_date'] < today_date:
            send_notice(el['delivery_date'], el['order_n'])

    return



def get_db_data():
    '''
    Получение данных из локальной базы данных и возврат данных в виде  списка словарей
    '''
    db_list = []
    for el in s.query(Orders).order_by(Orders.id):
        db_list.append(
            {"id": el.id, "order_n": el.order_n, "price_usd": el.price_usd,
             "delivery_date": el.delivery_date, "price_rub": el.price_rub}
        )
    return db_list


def main():
    '''
    Получение данных из таблицы Google и из локальной базы данных
    Сравнение полученных данных DeepDiff
    Добавление, удаление и/или изменение данных в локальной бд при наличии изменений в таблице Google
    '''

    data_db_list = get_db_data()
    data_sheet_list = get_sheet_data()

    diff = DeepDiff(data_db_list, data_sheet_list)

    added = diff.get('iterable_item_added')
    changed = diff.get('values_changed')
    removed = diff.get('iterable_item_removed')

    '''
    Добавление данных в локальную бд
    '''
    if added:

        for el in added:
            if isinstance(added[el]['price_usd'], float):
                rub = convert(added[el]['price_usd'])
            else:
                rub = 0.0
            note = Orders(
                id=added[el]['id'],
                order_n=added[el]['order_n'],
                price_usd=added[el]['price_usd'],
                delivery_date=added[el]['delivery_date'],
                price_rub=rub
            )

            s.add(note)
            s.commit()

            print('Added: ', added[el]['id'])


    '''
    Изменение данных в локальной бд
    '''
    if changed:

        for el in changed:
            '''
            DeepDiff возвращает словарь, где ключ - порядковый элемент в списке сравнения,
            значение - элемент, который имеет отличия
            Пример: {"root[49]['price_usd']": {'new_value': 1997.0, 'old_value': 0.0}}
            Далее проводится получение индекса и ключа из строки "root[49]['price_usd']"
            '''
            # получение индекса из строки
            index = int(*[index for index in re.findall(r'-?\d+\.?\d*', el)]) + 1

            # получение ключа из строки
            key = el.split("'")[1]

            note = s.query(Orders).filter_by(id=index).one()

            if key == 'order_n':
                note.order_n = changed[el]['new_value']

            elif key == 'price_usd':
                note.price_usd = changed[el]['new_value']

                if isinstance(changed[el]['new_value'], float):
                    rub = convert(changed[el]['new_value'])
                else:
                    rub = 0.0

                note.price_rub = rub

            elif key == 'delivery_date':
                note.delivery_date = changed[el]['new_value']

            s.add(note)
            s.commit()

            print('Updated: ', index)


    '''
    Удаление данных в локальной бд
    '''
    if removed:

        for el in removed:
            s.query(Orders).filter_by(id=removed[el]['id']).delete()
            s.commit()
            
            print('Removed: ', removed[el]['id'])


    '''
    В случае если срок доставки истек и у пользователя настроена отправка уведомлений
    будет отправлено сообщение в телеграмм, но не чаще, чем 1 раз в час
    '''
    global NOTIFICATION_TIME
    global DELTA

    time_now = datetime.now()
    diff_time = time_now - NOTIFICATION_TIME

    if diff_time >= DELTA:
        NOTIFICATION_TIME = datetime.now()
        DELTA = timedelta(hours=1)
        check_dates(data_sheet_list)


if __name__ == '__main__':
    while True:
        main()
        print("Waiting...")
        time.sleep(15)
