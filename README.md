# __🕺Flow Kitchen Telegram Bot 💃__

Официальный бот проекта "Flow Kitchen"

___

### ТЕХНОЛОГИИ

- [Python] (v.3.12) - целевой язык программирования backend
- [Aiogram] (v.3.6) - асинхронный фреймворк для Telegram Bot API
- [Celery] (v.5.4) - распределенная очередь задач
- [Redis] (v.5.0) - резидентная система управления NoSQL базами данных, брокер сообщений Celery
- [Docker] (v.24.0) - инструмент для автоматизирования процессов разработки, доставки и запуска приложений в контейнерах

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Celery](https://a11ybadges.com/badge?logo=celery)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

[Python]: <https://www.python.org/>
[Aiogram]: <https://aiogram.dev/>
[Celery]: <https://docs.celeryq.dev/en/stable/>
[Redis]: <https://redis.io/>
[Docker]: <https://www.docker.com/>

___

### РАЗВЕРТКА

✅ Загрузить актуальную версию проекта

```
git clone git@github.com:TheSuncatcher222/flow_kitchen_bot_telegram.git
```

✅ Перейти в директорию конфигураций проекта config:

```
cd src/config
```

✅ Создать файл переменных окружения из примера

```
cp .env.example .env
```

✅ Изменить переменные окружения (если необходимо)

```
(на примере редактора Nano)
nano .env
```

✅ Перейти в директорию docker

```
cd ../../docker
```

✅ Запустить Docker (убедитесь, что `docker daemon` запущен в системе!) (ОПЦИОНАЛЬНО: запустить контейнер с Redis, если не планируется использовать свой)

```
docker-compose -f docker-compose-redis.yml up --build
docker-compose -f docker-compose-backend.yml up --build
```

___

### ЛИЦЕНЗИЯ

MIT

**Ура, халява!**

___

### КОМАНДА BACKEND && QA

❤️ [Кирилл](https://github.com/TheSuncatcher222/)

🩷 [Оля](https://github.com/OlgaKopaeva/)
