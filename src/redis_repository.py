import redis
import pickle

redis_init = redis.Redis(host='localhost', port=6379, db=0)


def save_memory_to_redis(session_id, memory):
    memory_data = pickle.dumps(memory)
    redis_init.setex(session_id, 7200, memory_data)


def load_memory_from_redis(session_id):
    memory_data = redis_init.get(session_id)
    if memory_data:
        return pickle.loads(memory_data)
    return None


def remove_session(session_id):
    keys = redis_init.keys(session_id)

    if not keys:
        return ("No keys were found.")

    # Delete all keys for the session
    for key in keys:
        redis_init.delete(key)
        return ("Session deleted successfully")
