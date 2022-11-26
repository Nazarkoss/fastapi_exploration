import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, select
from db_sql import engine
# from local_json_storage_api.schemas_json import load_db, save_db, CarInput, CarOutput, TripInput, TripOutput
from local_sql_storage_api.schemas_sql import Car, CarInput, CarOutput, TripInput, TripOutput, Trip

app = FastAPI(title="Car Sharing")


# This is the function that will be called each time the callback functions are called, and will be injected as
# a parameter into the function. Moreover, implementing it as generator has several benefits.
# 1) Will be executed lazily, only if it's explicitly needed.
# 2) the with statement will protect against partial execution of the transaction
def get_session():
    with Session(engine) as session:
        yield session


# Tell Fast API to run this function on a startup of the project
@app.on_event("startup")
def on_startup():
    # checks if the database already exists if not it will be created
    SQLModel.metadata.create_all(engine)


@app.get("/")
def welcome():
    return {'massage': "Welcome to the Car Sharing service"}


# TODO: Check: we need to specify response_model=CarOutput, otherwise the return object will be converted to str
# we can also return a dict, fast API will do the conversion for us.
# TODO: when we ask for a car ID we do not get back automatically all the trips because these are optional and need
#  to be specifically requested (relations are Lazy!!!)
# We can solve the above by providing a specific a specific response_model=CarOutput for which the trips
# are not relations
# @app.post("/api/cars/", response_model=Car)
@app.post("/api/cars/", response_model=CarOutput)
def add_car(car_input: CarInput) -> Car:
    # this block is a DB transaction, will be pushed if executed successfully
    # all executed or none
    with Session(engine) as session:
        new_car = Car.from_orm(car_input)
        session.add(new_car)
        # will insert and create the ID
        session.commit()
        # will refresh the current object with the allocated ID
        session.refresh(new_car)
        return new_car


# Sessions are injected from here...
@app.get("/api/cars")
def get_cars(size: str | None = None, doors: int | None = None,
             session: Session = Depends(get_session)) -> list:
    query = select(Car)
    if size:
        query = query.where(Car.size == size)
    if doors:
        query = query.where(Car.doors >= doors)
    return session.exec(query).all()


@app.get("/api/cars/{id}", response_model=Car)
def car_by_id(id: int, session: Session = Depends(get_session)) -> Car:
    # get is like select but returns a single object (the first one matching the request???
    car = session.get(Car, id)
    if car:
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")



# The normal status code to output if the request have been successful is 204. We could return a string or nothing
# in which case the default status code 200 will be applied but this is a better way.
@app.delete("/api/cars/{id}", status_code=204)
def remove_car(id: int, session: Session = Depends(get_session)) -> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.put("/api/cars/{id}", response_model=Car)
def change_car(id: int, new_data: CarInput,
               session: Session = Depends(get_session)) -> Car:
    car = session.get(Car, id)
    if car:
        car.fuel = new_data.fuel
        car.transmission = new_data.transmission
        car.size = new_data.size
        car.doors = new_data.doors
        session.commit()
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.post("/api/cars/{car_id}/trips", response_model=Trip)
def add_trip(car_id: int, trip_input: TripInput,
             session: Session = Depends(get_session)) -> Trip:
    car = session.get(Car, car_id)
    if car:
        # A trip needs id of the car int belongs to
        # TripInput does not contain it, update={'car_id': car_id} tells to take all the elements from the input
        # and fill the rest of the attributes with additional provided values.
        new_trip = Trip.from_orm(trip_input, update={'car_id': car_id})
        # if new_trip.end < new_trip.start:
        #     raise BadTripException("Trip end before start")
        car.trips.append(new_trip)
        session.commit()
        session.refresh(new_trip)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


if __name__ == "__main__":
    uvicorn.run("carsharing_sql:app", reload=True)
