from fastapi import FastAPI, HTTPException
import redis
from pydantic import BaseModel
import time
from uuid import uuid4

r = redis.Redis()
REDIS_TIMERS_KEY = "timers"

app = FastAPI(title="SendCloudTimer")


class TimerRequestBody(BaseModel):
    hours: int
    minutes: int
    seconds: int
    url: str


@app.get("/timer/{id}")
def get_timer(id: str):
    timer_value = r.zscore(REDIS_TIMERS_KEY, id)
    if timer_value is None:
        raise HTTPException(404, "Timer not found")
    now = time.time()
    time_left = max(0, timer_value - now)
    return {"id": id, "time_left": time_left}


@app.post("/timer")
def set_timer(req: TimerRequestBody):
    now = time.time()
    timer_seconds = req.hours * 3600 + req.minutes * 60 + req.seconds
    expires = now + timer_seconds
    timer_id = str(uuid4())
    r.zadd(REDIS_TIMERS_KEY, {timer_id: expires})
    r.set(f"timer:{timer_id}", req.url)
    return timer_id
