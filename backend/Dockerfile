FROM python:3.13-slim


# Запрещает Python писать файлы .pyc на диск (экономит место)
ENV PYTHONDONTWRITEBYTECODE=1
# Гарантирует, что логи приложения сразу выводятся в консоль, а не буферизируются
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
WORKDIR /app/www/puzzle_site
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .


