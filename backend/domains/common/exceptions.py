"""
Common exceptions for the service layer.
Services can use HTTPException directly or define custom exceptions here.
"""

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """Raised when a resource is not found."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedError(HTTPException):
    """Raised when user is not authorized."""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictError(HTTPException):
    """Raised when there's a state conflict."""
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
