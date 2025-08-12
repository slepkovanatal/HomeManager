import os
import json
import redis

REDIS_URL_BOT = os.getenv("REDIS_URL_BOT")
_r = redis.Redis.from_url(REDIS_URL_BOT, decode_responses=True)

def _uk(chat_id: int) -> str: return f"user:{chat_id}"

def set_user_state(chat_id: int, ttl=None, **fields):
    mapping = {k: json.dumps(v) for k, v in fields.items()}
    _r.hset(_uk(chat_id), mapping=mapping)
    if ttl:
        _r.expire(_uk(chat_id), ttl)

def get_user_state(chat_id: int, *names):
    if names:
        vals = _r.hmget(_uk(chat_id), *names)
        return {n: (json.loads(v) if v is not None else None) for n, v in zip(names, vals)}
    raw = _r.hgetall(_uk(chat_id))
    return {k: json.loads(v) for k, v in raw.items()}
