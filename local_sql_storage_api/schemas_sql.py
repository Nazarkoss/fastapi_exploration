# SQLModel inherits from the pydantic, therefore the previously developed APIs for classes should work
# it also adds new features enabling working with SQL tables
from sqlmodel import SQLModel, Field, Relationship


class TripInput(SQLModel):
    start: int
    end: int
    description: str


class TripOutput(TripInput):
    id: int


class Trip(TripInput, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # set up a foreign key to the data table
    car_id: int = Field(foreign_key="car.id")
    # 1) we use "Car" and not Car because the class is defined below and this is a syntax to handle this type of sit...
    # 2) The table does not contain the car related to the trip but SQL model can back propagate and extract the
    # information about the Car object and inject it here.
    car: "Car" = Relationship(back_populates="trips")


# The input does not need an ID because it's not up to the client to know our DB
# The output should contain an ID
class CarInput(SQLModel):
    size: str
    fuel: str | None = "electric"
    doors: int
    transmission: str | None = "auto"


# table=True needs to be added to work with tables classes.
# this is the real data object CarOutput is the schema for the output
class Car(CarInput, table=True):
    # we want to let the possibility to the ID to be empty and automatically be added by database
    # Field configures the columns
    id: int | None = Field(primary_key=True, default=None)
    # A second part to define the many-to-one relation between trips and the car
    trips: list[Trip] = Relationship(back_populates="car")


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

