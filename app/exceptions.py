from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        self.headers = {"WWW-Authenticate": "Bearer"}


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
