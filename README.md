# Numbers ТЗ
<p>Скрипт отслеживает все изменения в 
[таблице Google](https://docs.google.com/spreadsheets/d/1jIfDMDdewd77iPKVvuvFKoNCJW69SL4y7jbyjSDgkHo/edit) 
Доступ на редактирование таблицы ограничен</p>
<p>Все изменения сохраняются в бд PostgreSQL</p>
<p>Скрипт добавляет цену в рублях РФ, переводя цену из долларов США по курсу ЦБ РФ</p>
<p>Реализован механизм уведомлений в "Телеграм" при истечении срока доставки заказа</p>

## Установка:
<p>Для реализации механизма отправки уведоблений укажите ваш Telegram user id. Его можно узнать воспользовавшись ботом @getmyid_bot</p>
<p>Id указывается в docker-compose.yml -> services -> web -> environment -> CHAT_ID</p>
<p>Далее необходимо написать любое сообщение в @numbers_test_tg_bot , именно этот бот и будет отправлять уведомления</p>
> docker-compose build
> docker-compose up
