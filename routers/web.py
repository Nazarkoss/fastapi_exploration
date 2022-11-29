from fastapi import APIRouter, Request, Form, Depends, Cookie
from sqlmodel import Session
# starlette is the library the Fast api uses in order to serve the HTTP/HTML.
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db import get_session
from routers.cars import get_cars

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, cars_cookie: str|None = Cookie(None)):
    print(cars_cookie)
    return templates.TemplateResponse("home.html",
                                      {"request": request})


# * is a new feature for python, normally arguments without the default value should come first.
# * allows us to do it, because it turns everything that comes after into a keyword arguments.
# type(...) is a python object of class ellipsis, ... tels that the fields are required.
@router.post("/search", response_class=HTMLResponse)
def search(*, size: str = Form(...), doors: int = Form(...),
           request: Request,
           session: Session = Depends(get_session)):
    cars = get_cars(size=size, doors=doors, session=session)
    return templates.TemplateResponse("search_results.html",
                                      {"request": request, "cars": cars})