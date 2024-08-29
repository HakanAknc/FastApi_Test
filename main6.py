from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uuid

# Veritabanı bağlantı bilgileri
DATABASE_URL = "postgresql://postgres:12345@127.0.0.1:5432/db_car"

# SQLAlchemy motorunu ve oturumu ayarlama
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Markalar modeli
class Marka(Base):
    __tablename__ = "markalar"
    marka_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    marka_ad = Column(String, nullable=False, unique=True)

# Arac Bilgileri modeli
class AracBilgileri(Base):
    __tablename__ = "arac_bilgileri"
    arac_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    marka_id = Column(String, ForeignKey("markalar.marka_id", ondelete="CASCADE"))
    seri = Column(String, nullable=False)
    renk = Column(String, nullable=False)
    yil = Column(Integer, nullable=False)
    yakit = Column(String, nullable=False)
    durum = Column(String, nullable=False)
    kilometre = Column(Integer, nullable=False)
    yakit_gucu = Column(String, nullable=False)
    isActive = Column(Boolean, default=True)
    createdTime = Column(TIMESTAMP, server_default=func.now())
    modifiedTime = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    marka = relationship("Marka", back_populates="araclar")

Marka.araclar = relationship("AracBilgileri", back_populates="marka", cascade="all, delete-orphan")

# Veritabanını başlat
Base.metadata.create_all(bind=engine)

# FastAPI uygulaması
app = FastAPI()

# Pydantic modelleri
class MarkaCreate(BaseModel):
    marka_ad: str

class MarkaUpdate(BaseModel):
    marka_ad: str

class AracBilgileriCreate(BaseModel):
    marka_id: str
    seri: str
    renk: str
    yil: int
    yakit: str
    durum: str
    kilometre: int
    yakit_gucu: str
    isActive: bool

class AracBilgileriUpdate(BaseModel):
    marka_id: str
    seri: str
    renk: str
    yil: int
    yakit: str
    durum: str
    kilometre: int
    yakit_gucu: str
    isActive: bool

# CRUD İşlemleri

# Marka Ekleme (POST)
@app.post("/markalar/")
def create_marka(marka: MarkaCreate):
    db = SessionLocal()
    db_marka = Marka(**marka.dict())
    db.add(db_marka)
    db.commit()
    db.refresh(db_marka)
    db.close()
    return db_marka

# Marka Listeleme (GET)
@app.get("/markalar/")
def read_markalar():
    db = SessionLocal()
    markalar = db.query(Marka).all()
    db.close()
    return markalar

# Marka Güncelleme (PUT)
@app.put("/markalar/{marka_id}")
def update_marka(marka_id: str, marka: MarkaUpdate):
    db = SessionLocal()
    db_marka = db.query(Marka).filter(Marka.marka_id == marka_id).first()
    if not db_marka:
        raise HTTPException(status_code=404, detail="Marka bulunamadı")
    db_marka.marka_ad = marka.marka_ad
    db.commit()
    db.refresh(db_marka)
    db.close()
    return db_marka

# Marka Silme (DELETE)
@app.delete("/markalar/{marka_id}")
def delete_marka(marka_id: str):
    db = SessionLocal()
    db_marka = db.query(Marka).filter(Marka.marka_id == marka_id).first()
    if not db_marka:
        raise HTTPException(status_code=404, detail="Marka bulunamadı")
    db.delete(db_marka)
    db.commit()
    db.close()
    return {"message": "Marka başarıyla silindi"}

# Araç Ekleme (POST)
@app.post("/araclar/")
def create_arac(arac: AracBilgileriCreate):
    db = SessionLocal()
    db_arac = AracBilgileri(**arac.dict())
    db.add(db_arac)
    db.commit()
    db.refresh(db_arac)
    db.close()
    return db_arac

# Araç Listeleme (GET)
@app.get("/araclar/")
def read_araclar():
    db = SessionLocal()
    araclar = db.query(AracBilgileri).all()
    db.close()
    return araclar

# Araç Güncelleme (PUT)
@app.put("/araclar/{arac_id}")
def update_arac(arac_id: str, arac: AracBilgileriUpdate):
    db = SessionLocal()
    db_arac = db.query(AracBilgileri).filter(AracBilgileri.arac_id == arac_id).first()
    if not db_arac:
        raise HTTPException(status_code=404, detail="Araç bulunamadı")
    for key, value in arac.dict().items():
        setattr(db_arac, key, value)
    db.commit()
    db.refresh(db_arac)
    db.close()
    return db_arac

# Araç Silme (DELETE)
@app.delete("/araclar/{arac_id}")
def delete_arac(arac_id: str):
    db = SessionLocal()
    db_arac = db.query(AracBilgileri).filter(AracBilgileri.arac_id == arac_id, AracBilgileri.isActive == False).first()
    if not db_arac:
        raise HTTPException(status_code=404, detail="Araç bulunamadı veya isActive durumu 'false' değil")
    db.delete(db_arac)
    db.commit()
    db.close()
    return {"message": "Araç başarıyla silindi"}

# Uygulamayı çalıştır
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
