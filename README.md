# Foodgram: Продуктовый помощник
 
# Описание проекта:
 
**Foodgram** — это онлайн-сервис с API, предназначенный для любителей кулинарии.
Он позволяет пользователям делиться рецептами, следить за обновлениями других авторов, сохранять понравившиеся рецепты в избранное и легко планировать покупки, загружая списки необходимых продуктов перед походом в магазин.

**Основные возможности Foodgram:**\
**Просмотр рецептов**: Исследуйте разнообразие рецептов, опубликованных пользователями.\
**Добавление в избранное**: Сохраняйте понравившиеся рецепты в специальный раздел для быстрого доступа.\
**Список покупок**: Формируйте списки необходимых продуктов для выбранных рецептов.\
**Создание и управление рецептами**: Создавайте свои рецепты, редактируйте и удаляйте их при необходимости.\
**Скачивание списка покупок**: Экспортируйте сводный список продуктов для удобства покупок в магазине.
 
## Технологии: 
 
- Python 3.11
- Django 5.0.7
- DRF 3.15.2
- React 
 
## Посмотреть проект можно по адресу: 
 
[Сайт](https://foodgramnicro.zapto.org)\
[Документация API](https://foodgramnicro.zapto.org/api/docs/)

## Пример env файла: 
 
``` 
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
DEBUG=False
USE_SQLITE=True
ALLOWED_HOSTS=100.100.100.100,example.org,127.0.0.1,localhost
``` 
 
## Руководство по запуску проекта из DockerHub: 
 
1. создать папку foodgram 
 
```bash 
mkdir foodgram 
cd foodgram 
``` 
 
2. В папку скопировать файл `docker-compose.production.yml` и запустите его: 
 
```bash 
sudo docker compose -f docker-compose.production.yml up 
``` 
 
## Запуск проекта из GitHub 
 
1. Клонируем ропозиторий:
 
```bash  
git@github.com:nicros22/foodgram.git 
``` 
 
2. Выполняем запуск докера из исходников в папке: 
 
```bash 
sudo docker compose -f docker-compose.yml up 
``` 
 
3. Миграции и сбор статики:
 
```bash 
sudo docker compose -f [имя-файла-docker-compose.yml] exec backend python manage.py migrate 
 
sudo docker compose -f [имя-файла-docker-compose.yml] exec backend python manage.py collectstatic 
 
sudo docker compose -f [имя-файла-docker-compose.yml] exec backend cp -r /app/collected_static/. /static/static/ 
```
4. Финальный этап (загрузка ингредиентов в бд):

Переходим в директорию, где находится manage.py и выполняем команду - 

```bash 
python manage.py load_csv_data
```
 
## Проект будет доступен на: 
 
``` 
http://localhost:9000/ 
``` 
 
## Автор 
 
Пономаренко Никита 
