from fastapi import Request, status
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, type: str, message: str):
        self.type = type
        self.message = message
        super().__init__(self.message)

ERROR_TYPE_MAP = {
    'VALIDATION_ERROR': status.HTTP_400_BAD_REQUEST,
    'BAD_REQUEST': status.HTTP_400_BAD_REQUEST,
    'UNAUTHORIZED': status.HTTP_401_UNAUTHORIZED,
    'UPDATE_ERROR': status.HTTP_403_FORBIDDEN,
    'FORBIDDEN_ERROR': status.HTTP_403_FORBIDDEN,
    'NOT_FOUND': status.HTTP_404_NOT_FOUND,
    'CONFLICT': status.HTTP_409_CONFLICT,
    'TOO_MANY_REQUESTS': status.HTTP_429_TOO_MANY_REQUESTS,
    'DATABASE_ERROR': status.HTTP_500_INTERNAL_SERVER_ERROR,
    'INTERNAL_SERVER_ERROR': status.HTTP_500_INTERNAL_SERVER_ERROR,
}

async def app_exception_handler(request: Request, exc: AppException):
    status_code = ERROR_TYPE_MAP.get(exc.type, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        message = 'Ocorreu um erro interno no servidor.'
    else:
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error": message},
    )