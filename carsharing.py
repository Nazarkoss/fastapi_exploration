import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from db import engine
from routers import cars, web, auth
from routers.cars import BadTripException

app = FastAPI(title="Car Sharing")
app.include_router(web.router)
app.include_router(cars.router)
app.include_router(auth.router)

# the reason for these ports is explained below...
origins = [
    "http://localhost:8000",
    "http://localhost:8080",
]

# Modern browsers follow the policy of the same origin (same browser), they allow javascript to call services only,
# when they have the same origin as the web page calling them
# => if the web page calls a port 8080, we have page with javascript button calling another resource on 8000,
# the browser will block the request...
# to avoid this, we need to add CORSMiddleware to the middleware (see below the definition)
# If we have a website on another domain (server or just port) that needs to consume our API , we need to allow
# the access using the CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# If we want to avoid writing the same return every time the BadTripException is raised, we can create a function,
# decorated with the exception @app.exception_handler(BadTripException) which will be called every time the exception
# occurs and will generate a proper output
@app.exception_handler(BadTripException)
async def unicorn_exception_handler(request: Request, exc: BadTripException):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Bad Trip"},
    )

# middleware is the function that works with any requests before it gets processes! And also with
# the responses before it gets returned.
# For the time of the course only the HTTP is supported
@app.middleware("http")
async def add_cars_cookie(request: Request, call_next):
    response = await call_next(request)
    response.set_cookie(key="cars_cookie", value="you_visited_the_carsharing_app")
    return response


if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)
