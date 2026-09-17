from fastapi import HTTPException


class AppException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, details: dict | None = None):
        super().__init__(status_code=status_code, detail={"error": {"code": code, "message": message, "details": details} if details else {"code": code, "message": message}})
        self.code = code
        self.message = message
        self.details = details


class NotFoundException(AppException):
    def __init__(self, code: str = "NOT_FOUND", message: str = "Resource not found", details=None):
        super().__init__(404, code, message, details)


class UnauthorizedException(AppException):
    def __init__(self, code: str = "UNAUTHORIZED", message: str = "Authentication required", details=None):
        super().__init__(401, code, message, details)


class ForbiddenException(AppException):
    def __init__(self, code: str = "FORBIDDEN", message: str = "Not authorized", details=None):
        super().__init__(403, code, message, details)


class ConflictException(AppException):
    def __init__(self, code: str = "CONFLICT", message: str = "Conflict", details=None):
        super().__init__(409, code, message, details)


class BadRequestException(AppException):
    def __init__(self, code: str = "BAD_REQUEST", message: str = "Invalid request", details=None):
        super().__init__(400, code, message, details)


class UnprocessableException(AppException):
    def __init__(self, code: str = "UNPROCESSABLE", message: str = "Validation failed", details=None):
        super().__init__(422, code, message, details)
