import time
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LogRequestsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        req_id = request.state.request_id
        logging.info(f"rid={req_id} Start Request Path={request.url.path}")

        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        formatted_process_time = '{0:.2f}'.format(process_time)
        logging.info(f"rid={req_id} | completed_in={formatted_process_time}ms | status_code={response.status_code}")

        return response
