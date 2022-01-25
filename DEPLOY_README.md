# Полное руководство по деплою на сервер
---
1. Для начала арендуйте сервер (желательно иметь сервер от 1gb ram), я использовал сервер на Debian-10
2. Создайте пользователя, дайте ему sudo права и работайте из под него
3. Сделайте все тоже самое что описано в установке локально в файле ```README.md```
5. Удалите файл ```vape_shop/local_settings.py```
6. Переименуйте файл ```vape_shop/prod_settings.py.exemple``` на  ```vape_shop/prod_settings.py``` и заполните свои данные в полях
  - ALLOWED_HOSTS - "Ваш ip или домен"
  - SECRET_KEY = "Любая последовательность символов"
  - Данные от postgres, которые мы позже создадим
7. Установим на сервер нужное нам ПО командой ```sudo apt install nginx git supervisor postgresql```
8. Сначала займемся Postgresql:
  - Зайдите в оболочку postgres командой ```sudo -u postgres psql```
    Дальше работает в оболчке:
      - ```CREATE DATABASE <ИМЯ БАЗЫ ДАННЫХ>;``` - Создаем базу данных
      - ```CREATE USER <ИМЯ ПОЛЬЗОВАТЕЛЯ> WITH PASSWORD '<ПАРОЛЬ ПОЛЬЗОВАТЕЛЯ>';``` - Придумайте имя пользователя и пароль для него, эти данные должны быть указаны в ```prod_settings.py``` 
      - ```ALTER ROLE <ИМЯ ПОЛЬЗОВАТЕЛЯ> SET client_encoding TO 'utf8';``` - Настраиваем кодировки
      - ```ALTER ROLE <ИМЯ ПОЛЬЗОВАТЕЛЯ> SET default_transaction_isolation TO 'read committed';``` - Устанавливаем уровень изоляции
      - ```ALTER ROLE vape_site SET timezone TO 'UTC';``` - Устанавливаем часовой пояс
      - ```\q``` - Выходим оболчки Postgres
9. Примините миграции: ```python3 manage.py migrate```
10 . Создайте папки ```media``` и ```logs``` в корне проекта
11. Создайте суперпользователя командой ```python3 manage.py createsuperuser```
12. Если вы все сделали правильно, вы уже можете попробовать запустить сервер командой ```gunicorn vape_shop.wsgi:application --bind <IP Сервера>:8000```,
он должен быть доступен по адресу http://<IP ВАШЕГО СЕРВЕРА>:8000
13. Теперь займемся nginx
  - Редактируем конфиг Nginx командой ```sudo nano /etc/nginx/sites-available/default```
  - Удаляем все командой ```ALT + T``` и вставляем конфиг:
    ```
    server {
    listen 80;
    server_name ; # здесь прописать или IP-адрес или доменное имя сервера
    access_log  /var/log/nginx/example.log;
 
    location /static/ {
        root /home/vape_site/telebot_django;
        expires 30d;
    }

    location /media/ {
        root /home/vape_site/telebot_django;
        expires 30d;
    }
 
    location / {
        proxy_pass http://127.0.0.1:8000; 
        proxy_set_header Host $server_name;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    }
    ```
14. Перезапустите nginx сервер командой ```sudo service nginx restart```
15. Что бы получить SSL сертификат легко и быстро, воспользуйтесь утилитой ```LetsEncrypt SSL```, подробнее в https://www.youtube.com/watch?v=1wnOw1vwPEo
16. Установим наши демоны, что бы все наши приложения могли сами себя поднимать
   - В папке ```conf``` лежит 4 файла: ```vape_shop.conf```, ```celery_worker.conf```, ```celery_beat.conf``` и ```bot.conf```
   - Отредактируйте их, вписав свой username в пути и перемстите эти файлы по пути : ```/etc/supervisor/conf.d/``` 
   - Выполните команду ```sudo supervisord reread``` и ```sudo supervisord update```
   - Проверьте статус выполняемых задач командой ```sudo supervisord status```
