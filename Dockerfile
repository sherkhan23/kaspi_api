FROM python:3.9

WORKDIR /api
COPY requirements.txt /api
RUN pip install -r requirements.txt
COPY . /api/
ENV PYTHONPATH /api

# Собираем статические файлы в директорию STATIC_ROOT
RUN python django_app.py collectstatic --noinput