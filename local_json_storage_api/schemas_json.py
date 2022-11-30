import json

from pydantic import BaseModel


# The input does not need an ID because it's not up to the client to know our DB
# The output should contain an ID
class TripInput(BaseModel):
    start: int
    end: int
    description: str


class TripOutput(TripInput):
    id: int


# The input does not need an ID because it's not up to the client to know our DB
# The output should contain an ID
class CarInput(BaseModel):
    size: str
    fuel: str | None = "electric"
    doors: int
    transmission: str | None = "auto"


class CarOutput(CarInput):
    id: int
    trips: list[TripOutput] = []


# Will be used by the FastApi in order to predefine input car objects (in put request for example).
class Config:
    schema_extra = {
        "example": {
            "size": "m",
            "doors": 5,
            "transmission": "manual",
            "fuel": "hybrid",
        }
    }


def load_db() -> list[CarOutput]:
    #import os
    #raise ValueError(os.getcwd())
    with open("cars.json") as f:
#     with open("../cars.json") as f:
        return [CarOutput.parse_obj(obj) for obj in json.load(f)]


def save_db(cars: list[CarInput]):
    with open("../cars.json", 'w') as f:
        json.dump([car.dict() for car in cars], f, indent=4)
