from fastapi import HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse

class VelosException(Exception):
    """Base exception for all Velos custom exceptions."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(VelosException):
    def __init__(self, message: str):
        super().__init__(message, code="NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)

class AuthorizationException(VelosException):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, code="UNAUTHORIZED", status_code=status.HTTP_401_UNAUTHORIZED)
        
class RateLimitException(VelosException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, code="RATE_LIMIT", status_code=status.HTTP_429_TOO_MANY_REQUESTS)

def setup_exception_handlers(app):
    @app.exception_handler(VelosException)
    async def velos_exception_handler(request: Request, exc: VelosException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
