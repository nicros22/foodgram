# Foodgram 
 
# Описание проекта. 
 
Проект на котором можно создавать свои рецепты, добавлять в избранное и всё реализовано как соцсеть. 
 
## Технологии: 
 
- Python 3.11
- Django 5.0.7
- DRF 3.15.2
- React 
 
## Посмотреть проект можно по адресу: 
 
``` 
https://foodgramnicro.zapto.org
```

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
 
1. Клонируем ропозиторий. 
 
```bash  
git@github.com:nicros22/foodgram.git 
``` 
 
Выполняем запуск докера из исходников в папке: 
 
```bash 
sudo docker compose -f docker-compose.yml up 
``` 
 
## Финальный этап (Миграции и сбор статики). 
 
```bash 
sudo docker compose -f [имя-файла-docker-compose.yml] exec backend python manage.py migrate 
 
sudo docker compose -f [имя-файла-docker-compose.yml] exec backend python manage.py collectstatic 
 
sudo docker compose -f [имя-файла-docker-compose.yml] exec backend cp -r /app/collected_static/. /static/static/ 
``` 
 
## Проект будет доступен на: 
 
``` 
http://localhost:9000/ 
``` 
 
## Автор 
 
Пономаренко Никита 
