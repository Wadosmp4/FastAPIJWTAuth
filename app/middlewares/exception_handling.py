from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from starlette.middleware.base import BaseHTTPMiddleware


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            return JSONResponse(content={"error": str(exc.detail)}, status_code=exc.status_code)
        except Exception as exc:
            return JSONResponse(content={"error": f"Internal Server Error: {exc.args[0]}"}, status_code=500)
