import uvicorn
from fastapi import FastAPI, HTTPException
from local_json_storage_api.schemas_json import load_db, save_db, CarInput, CarOutput, TripInput, TripOutput

app = FastAPI(title="Car Sharing")
db = load_db()


@app.get("/")
def welcome():
    return {'massage': "Welcome to the Car Sharing service"}


@app.get("/api/cars")
def get_cars(size: str | None = None, doors: int | None = None) -> list:
    results = db
    if size:
        results = [car for car in results if car.size == size]
    if doors:
        results = [car for car in results if car.doors >= doors]
    return results


@app.get("/api/cars/{id}")
def get_cars(id: int) -> dict:
    results = [car for car in db if car.id == id]
    if results:
        return results[0]
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


# we need to specify response_model=CarOutput, otherwise the return object will be converted to str
# we can also return a dict, fast API will do the conversion for us.
@app.post("/api/cars/", response_model=CarOutput)
def add_car(car: CarInput) -> CarOutput:
    new_car = CarOutput(size=car.size, doors=car.doors, fuel=car.fuel, transmission=car.transmission, id=len(db) + 1)
    db.append(new_car)
    save_db(db)
    return new_car


# The normal status code to output if the request have been successful is 204. We could return a string or nothing
# in which case the default status code 200 will be applied but this is a better way.
@app.delete("/api/cars/{id}", status_code=204)
def remove_car(id: int) -> None:
    matches = [car for car in db if car.id == id]
    if matches:
        car = matches[0]
        db.remove(car)
        save_db(db)
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.put("/api/cars/{id}", response_model=CarOutput)
def change_car(id: int, new_data: CarInput) -> CarOutput:
    matches = [car for car in db if car.id == id]
    if matches:
        car = matches[0]
        car.fuel = new_data.fuel
        car.transmission = new_data.transmission
        car.size = new_data.size
        car.doors = new_data.doors
        save_db(db)
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.post("/api/cars/{car_id}/trips", response_model=TripOutput)
def add_trip(car_id: int, trip: TripInput) -> TripOutput:
    matches = [car for car in db if car.id == car_id]
    if matches:
        car = matches[0]
        new_trip = TripOutput(id=len(car.trips) + 1, start=trip.start, end=trip.end, description=trip.description)
        car.trips.append(new_trip)
        save_db(db)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


if __name__ == "__main__":
    uvicorn.run("carsharing_json:app", reload=True)
