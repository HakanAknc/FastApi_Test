from fastapi import FastAPI, HTTPException
from typing import List
from models import Arac
from crud import create_csv_file, read_csv_file, write_csv_file

app = FastAPI()

# Uygulama başladığında CSV dosyasını oluştur
create_csv_file()

@app.get("/cars/", response_model=List[Arac])
def list_cars():
    cars = read_csv_file()
    return cars

@app.post("/cars/")
def add_car(car: Arac):
    cars = read_csv_file()
    for existing_car in cars:
        if existing_car.id == car.id:
            raise HTTPException(status_code=400, detail="A car with this ID already exists.")
    cars.append(car)
    write_csv_file(cars)
    return {"message": "Car successfully added."}

@app.delete("/cars/{car_id}")
def delete_car(id: int):
    cars = read_csv_file()
    cars = [car for car in cars if car.id != id]
    write_csv_file(cars)
    return {"message": "Car successfully deleted."}

@app.put("/cars/{car_id}")
def update_car(id: int, updated_car: Arac):
    cars = read_csv_file()
    for i, car in enumerate(cars):
        if car.id == id:
            cars[i] = updated_car
            write_csv_file(cars)
            return {"message": "Car successfully updated."}
    raise HTTPException(status_code=404, detail="Car not found.")
