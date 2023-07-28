import logging

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from datetime import timedelta

from app.cache import redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit, interval):
        super().__init__(app)
        self.limit = limit
        self.interval = timedelta(seconds=interval)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        logging.info(f"RateLimitMiddleware: request_id={request.state.request_id}")
        current = await redis_client.get(key)

        if current is None:
            await redis_client.setex(key, self.interval, 1)
        elif int(current) >= self.limit:
            return HTTPException(status_code=429, detail="Too Many Requests")
        else:
            await redis_client.incr(key)

        return await call_next(request)
