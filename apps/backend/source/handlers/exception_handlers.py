from fastapi import Request
from fastapi.exceptions import RequestValidationError, ValidationException
from fastapi.responses import JSONResponse

"""
This is to change any default behaviours of FastAPI handling

i.e. validation errors would normally throw 422 which I dont like
"""


def setup_exception_handlers(app):

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(
        request: Request, exc: ValidationException
    ):
        return JSONResponse(
            status_code=400,
            content={"message": "400 Bad Request", "error": exc._errors},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=400,
            content={"message": "400 Bad Request", "error": exc._errors},
        )
