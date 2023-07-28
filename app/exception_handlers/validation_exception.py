from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder


def validation_exception_handler(request: Request, exc: RequestValidationError):
    readable_errors_format = []
    for error in exc.errors():
        readable_errors_format.append({
            "location": error.get("loc", ["", "unknown"])[1],
            "msg": error.get("msg", "")
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": readable_errors_format})
    )
