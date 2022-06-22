# Foodgram
Это кулинарная соцсеть, позволяет пользователям создавать и обмениваться рецептами, добавлять в избранное и корзину, подписываться на понравившихся авторов, а также выгружать список покупок для рецептов в корзине.

## Технологии
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)![CSS](https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white)

## Workflow статус
![foodgram workflow](https://github.com/HellfastUSMC/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Подготовка и запуск проекта
### Для работы с удаленным сервером (на ubuntu):
* Выполните вход на свой удаленный сервер

* Клонируйте репозиторий в рабочую папку
    ```
    https://github.com/HellfastUSMC/foodgram-project-react.git
    ```

* В папке infra/ создайте .env файл с содержанием
    ```
    DB_ENGINE=<django.db.backends.postgresql_psycopg2>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<секретный ключ проекта django>
    ```
* Проект может запускаться через Github Workflow, для этого установите переменные окружения:
    ```
    DB_ENGINE=<django.db.backends.postgresql_psycopg2>
    DB_NAME=<Имя БД>
    DB_USER=<Имя пользователя БД>
    DB_PASSWORD=<Пароль пользователя БД>
    DB_HOST=<db>
    DB_PORT=<5432>
    
    DOCKER_USERNAME=<Имя пользователя DockerHub>
    DOCKER_PASSWORD=<Пароль от DockerHub>
    
    SECRET_KEY=<Секретный ключ проекта Django>
    USER=<Имя пользователя для подключения к серверу>
    HOST=<IP или домен сервера>
    PASSPHRASE=<Пароль закрытого ключа при наличии>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>
    TELEGRAM_TO=<ID чата Telegram, в который придет сообщение>
    TELEGRAM_TOKEN=<Токен вашего бота в Telegram>
    ```

* Установите docker на сервер:
    ```
    sudo apt install docker.io 
    ```
* Установите docker-compose на сервер:
    ```
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```
    Workflow проекта состоит из 4 шагов:
     - Проверка кода по PEP8
     - Сборка и публикация образа бекенда на DockerHub.
     - Автоматический деплой на удаленный сервер.
     - Отправка уведомления о готовности в Telegram. 

* На сервере соберите docker-compose:
    ```
    sudo docker-compose up -d --build
    ```

* После успешной сборки на сервере выполните команды (только после первого деплоя):
    *В случае использования Workflow миграции и сборка статики происходят в автоматческом режиме*
    - Соберите статику:
    ```
    sudo docker-compose exec backend python manage.py collectstatic --noinput
    ```
    - Создайте и примените миграции:
    ```
    sudo docker container exec infra-web-1 python manage.py makemigrations
    ```
    ```
    sudo docker container exec infra-web-1 python manage.py migrate --noinput
    ```
    - Загрузите данные в таблицу Product:
    *Опционально*
    ```
    sudo docker container exec infra-web-1 python manage.py load_data
    ```
    - Создайте суперпользователя:
    ```
    sudo docker-compose exec backend python manage.py createsuperuser
    ```
    - Проект станет доступен по IP или домену

## Ссылка на пример работы
[foodgram.servebeer.com](http://foodgram.servebeer.com/)
[130.193.52.234](http://130.193.52.234/)

## Автор
Александр Набиев, когорта 26, факультет backend-разработки Yandex Practicum.
[![https://t.me/HellfastUSMC](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/HellfastUSMC)
