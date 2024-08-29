from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Veritabanı bağlantı bilgileri
DATABASE_URL = "postgresql://postgres:12345@127.0.0.1:5432/Car_db"

# SQLAlchemy motorunu ve oturumu ayarlama
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Marka modelini oluşturma
class Brand(Base):
    __tablename__ = "brands"
    brand_id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String, unique=True, index=True)

# Araç modelini oluşturma
class Car(Base):
    __tablename__ = "cars"
    car_id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer)
    model_name = Column(String)
    color = Column(String)
    year = Column(Integer)
    fuel_type = Column(String)
    condition = Column(String)
    mileage = Column(Integer)
    engine_power = Column(Integer)

# Veritabanını başlat
Base.metadata.create_all(bind=engine)

# FastAPI uygulaması
app = FastAPI()

# Pydantic model sınıfı
class CarCreate(BaseModel):
    brand_id: int
    model_name: str
    color: str
    year: int
    fuel_type: str
    condition: str
    mileage: int
    engine_power: int

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ekleme (POST) işlemi
@app.post("/cars/", response_model=CarCreate)
def create_car(car: CarCreate, db: Session = Depends(get_db)):
    db_car = Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# Listeleme (GET) işlemi
@app.get("/cars/")
def read_cars(db: Session = Depends(get_db)):
    cars = db.query(Car).all()
    return cars

# Güncelleme (PUT) işlemi
@app.put("/cars/{car_id}")
def update_car(car_id: int, car: CarCreate, db: Session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.car_id == car_id).first()
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    for key, value in car.dict().items():
        setattr(db_car, key, value)
    db.commit()
    db.refresh(db_car)
    return db_car

# Silme (DELETE) işlemi
@app.delete("/cars/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.car_id == car_id).first()
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    db.delete(db_car)
    db.commit()
    return {"message": "Car deleted successfully"}

# Uygulamayı sürekli konsolda başlatmak yerine çalıştırdığında direkt çalışması için
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
