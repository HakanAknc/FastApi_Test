from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Veritabanı bağlantı bilgileri
DATABASE_URL = ""

# SQLAlchemy motorunu ve oturumu ayarlama
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Marka modeli
class Brand(Base):
    __tablename__ = "markalar"
    marka_id = Column(Integer, primary_key=True, autoincrement=True)
    marka_ad = Column(String, unique=True, index=True)

# Araç modeli
class Car(Base):
    __tablename__ = "arac_bilgi"
    arac_id = Column(Integer, primary_key=True, autoincrement=True)
    marka_id = Column(Integer, ForeignKey("markalar.marka_id", ondelete="CASCADE"))
    seri = Column(String)
    renk = Column(String)
    yil = Column(Integer)
    yakit = Column(String)
    durum = Column(String)
    kilometre = Column(Integer)
    yakit_gucu = Column(Integer)
    isActive = Column(Boolean, default=True)
    brand = relationship("Brand", back_populates="cars")

Brand.cars = relationship("Car", back_populates="brand")

# Veritabanını başlat
Base.metadata.create_all(bind=engine)

# FastAPI uygulaması
app = FastAPI()

# Pydantic modelleri
class BrandCreate(BaseModel):
    marka_ad: str

class CarCreate(BaseModel):
    marka_id: int
    seri: str
    renk: str
    yil: int
    yakit: str
    durum: str
    kilometre: int
    yakit_gucu: int
    isActive: bool = True

# Veritabanı oturumu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Marka ekleme (POST)
@app.post("/markalar/", response_model=BrandCreate)
def create_brand(brand: BrandCreate, db: sessionmaker = Depends(get_db)):
    db_brand = Brand(marka_ad=brand.marka_ad)
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

# Marka listeleme (GET)
@app.get("/markalar/")
def read_brands(db: sessionmaker = Depends(get_db)):
    return db.query(Brand).all()

# Marka güncelleme (PUT)
@app.put("/markalar/{marka_id}")
def update_brand(marka_id: int, brand: BrandCreate, db: sessionmaker = Depends(get_db)):
    db_brand = db.query(Brand).filter(Brand.marka_id == marka_id).first()
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Marka bulunamadı")
    db_brand.marka_ad = brand.marka_ad
    db.commit()
    db.refresh(db_brand)
    return db_brand

# Marka silme (DELETE)
@app.delete("/markalar/{marka_id}")
def delete_brand(marka_id: int, db: sessionmaker = Depends(get_db)):
    db_brand = db.query(Brand).filter(Brand.marka_id == marka_id).first()
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Marka bulunamadı")
    db.delete(db_brand)
    db.commit()
    return {"message": "Marka başarıyla silindi"}

# Araç ekleme (POST)
@app.post("/araclar/", response_model=CarCreate)
def create_car(car: CarCreate, db: sessionmaker = Depends(get_db)):
    db_car = Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# Araç listeleme (GET)
@app.get("/araclar/")
def read_cars(db: sessionmaker = Depends(get_db)):
    return db.query(Car).all()

# Araç güncelleme (PUT)
@app.put("/araclar/{arac_id}")
def update_car(arac_id: int, car: CarCreate, db: sessionmaker = Depends(get_db)):
    db_car = db.query(Car).filter(Car.arac_id == arac_id).first()
    if db_car is None:
        raise HTTPException(status_code=404, detail="Araç bulunamadı")
    for key, value in car.dict().items():
        setattr(db_car, key, value)
    db.commit()
    db.refresh(db_car)
    return db_car

# Araç silme (DELETE)
@app.delete("/araclar/{arac_id}")
def delete_car(arac_id: int, db: sessionmaker = Depends(get_db)):
    db_car = db.query(Car).filter(Car.arac_id == arac_id).first()
    if db_car is None:
        raise HTTPException(status_code=404, detail="Araç bulunamadı")
    db.delete(db_car)
    db.commit()
    return {"message": "Araç başarıyla silindi"}

# Uygulamayı başlatma
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
