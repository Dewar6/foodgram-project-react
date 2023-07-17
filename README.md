https://foodgramator.sytes.net/
логин: admin@mail.ru
пароль: adminadmin

Данный проект представляет из себя кулинарный сайт с функционалом создания рецептов, подпиской на авторов рецептов, добавлением рецептов в избранное, в список покупок с возможностью
его скачивания.

### Как запустить проект:

#### Для нативного запуска:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Dewar6/foodgram-project-react.git
```

```
cd foodgram-project-react/backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

- Если у вас Linux/macOS

  ```
  source env/bin/activate
  ```

- Если у вас windows

  ```
  source env/scripts/activate
  ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

#### Для запуска через Docker:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Dewar6/foodgram-project-react.git
```

```
cd foodgram-project-react/backend
```

Запустить сборку compose:

```
sudo docker compose -f docker-compose.production.yml up -d
```

Перейти в папку с backend-ом

`cd backend`

Выполнить миграции, собрать статику и перенести её в volumes backend-a

```
python manage.py migrate
python manage.py collectstatic
python manage.py cp -r /app/collected_static/. /backend_static/static/
```
