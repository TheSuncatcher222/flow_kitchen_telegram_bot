from redis import Redis

db_redis = Redis(
    host='bot-telegram-redis',
    port=6379,
    db=0,
    decode_responses=True,
)
