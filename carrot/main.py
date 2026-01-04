from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from carrot.api import api_router
from carrot.common.exceptions import CarrotException, MissingRequiredFieldException

app = FastAPI()
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return "Hello, Waffle Project!"


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for error in exc.errors():
        if error["type"] == "missing":
            raise MissingRequiredFieldException()
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(CarrotException)
async def carrot_exception_handler(request: Request, exc: CarrotException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "error_msg": exc.error_msg},
    )
