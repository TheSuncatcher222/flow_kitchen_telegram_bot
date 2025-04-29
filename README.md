# __🕺Flow Kitchen Telegram Bot 💃__

Официальный бот проекта "Flow Kitchen" / "Dance Kitchen"

___

### ТЕХНОЛОГИИ

- [Python] (v.3.12) - целевой язык программирования backend
- [Aiogram] (v.3.6) - асинхронный фреймворк для Telegram Bot API
- [APScheduler] (v. 3.11) - планировщик заданий с поддержкой асинхронного кода
- [PostgreSQL] (v.17.4) - реляционная база данных
- [SQLAlchemy] (v.2.0) - библиотека для ORM работы с PostgreSQL
- [Redis] (v.5.2) - NoSQL in-memory база данных
- [Pydantic] (v.2.11) - библиотека для валидации данных
- [Docker] (v.24.0) - инструмент для автоматизирования процессов разработки, доставки и запуска приложений в контейнерах

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

[Python]: <https://www.python.org/>
[Aiogram]: <https://aiogram.dev/>
[APScheduler]: <https://apscheduler.readthedocs.io/en/latest/>
[PostgreSQL]: <https://www.postgresql.org/>
[SQLAlchemy]: <https://www.sqlalchemy.org/>
[Redis]: <https://redis.io/>
[Pydantic]: <https://docs.pydantic.dev/latest/>
[Docker]: <https://www.docker.com/>

___

### РАЗВЕРТКА

✅ Загрузить актуальную версию проекта

```
git clone git@github.com:TheSuncatcher222/flow_kitchen_bot_telegram.git
```

✅ Создать файл переменных окружения из примера

```
cp app/src/config/.env.example app/src/config/.env
```

✅ Изменить переменные окружения (если необходимо)

```
# на примере редактора Nano:
nano app/src/config/.env
```

✅ Запустить Docker (убедитесь, что `docker daemon` запущен в системе!)

```
docker-compose -f docker/docker-compose-develop.yml --env-file app/src/config/.env up -d
```

___

### ЛИЦЕНЗИЯ

MIT

**Ура, халява!**

___

### КОМАНДА BACKEND && QA

❤️ [Кирилл](https://github.com/TheSuncatcher222/)

🩷 [Оля](https://github.com/OlgaKopaeva/)
