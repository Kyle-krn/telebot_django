FROM python:3.8.6-alpine

# рабочая директория внутри проекта
WORKDIR /home/kyle

# переменные окружения для python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# устанавливаем зависимости
RUN apk add --no-cache \
    build-base cairo-dev cairo cairo-tools
RUN apk add zlib-dev jpeg-dev

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
COPY ./requirements.txt /home/kyle/requirements.txt
RUN pip install -r requirements.txt



# копируем содержимое текущей папки в контейнер
COPY . /home/kyle
RUN mkdir /home/kyle/static
RUN mkdir /home/kyle/media
# copy entrypoint.sh
# COPY ./entrypoint.sh /home/kyle
# COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /home/kyle/entrypoint.sh
RUN chmod +x /home/kyle/entrypoint.sh

ENTRYPOINT ["/home/kyle/entrypoint.sh"]
