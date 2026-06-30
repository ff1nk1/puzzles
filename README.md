#PUZZLES
- Бэкэнд сайта для решения алгоритмических задач


## 🛠️ Стек технологий
* **Python 3.13**
* **FastAPI** (Веб-фреймворк)
* **SQLAlchemy 2.0 / Alembic** (ORM и миграции)
* **PostgreSQL 17** (База данных)
* **Redis / Arq** (Кэш и фоновые задачи)
* **Docker / Docker Compose** (Контейнеризация)


##  ЗАПУСК

### Требования
Убедитесь, что у вас установлены [Docker](https://docker.com) и [Docker Compose](https://docker.com).

### Запуск
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com
   cd puzzles
   ```
2. Создайте файл `.env` в корне проекта и заполните его по примеру `.env.example`.
3. Запустите контейнеры:
   ```bash
   docker compose up -d --build
   ```
4. Накатите миграции базы данных:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

После этого бэкенд будет доступен по адресу: `http://localhost:8000/docs` (Swagger UI).
