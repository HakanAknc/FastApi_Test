from fastapi import FastAPI, HTTPException   # TODO SON SÜRÜM 1.1
from pydantic import BaseModel
from datetime import datetime
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
    isActive = Column("isactive", Boolean, default=True)
    createdTime = Column("createdtime", TIMESTAMP, server_default=func.now())
    modifiedTime = Column("modifiedtime", TIMESTAMP, server_default=func.now(), onupdate=func.now())

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

    # Büyük/küçük harf ve boşluk kontrolü ile marka adını normalize et
    normalized_marka_ad = marka.marka_ad.strip().lower()

    # Aynı isimde bir marka olup olmadığını kontrol et
    existing_marka = db.query(Marka).filter(func.lower(Marka.marka_ad) == normalized_marka_ad).first()
    if existing_marka:
        db.close()
        raise HTTPException(status_code=400, detail="Bu marka adı zaten mevcut.")

    # Yeni marka kaydını oluştur
    db_marka = Marka(marka_ad=marka.marka_ad.strip())
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

    # marka_id girildiğinde eksik veya hatalıysa hata mesajı döndür
    db_marka = db.query(Marka).filter(Marka.marka_id == marka_id).first()
    if not db_marka:
        db.close()
        raise HTTPException(status_code=400, detail="Marka ID hatalı veya eksik girdiniz.")

    # marka_ad güncellenmek isteniyorsa ve aynı isimde bir marka zaten varsa hata mesajı döndür
    normalized_marka_ad = marka.marka_ad.strip().lower()
    existing_marka = db.query(Marka).filter(func.lower(Marka.marka_ad) == normalized_marka_ad).first()
    
    if existing_marka and existing_marka.marka_id != marka_id:
        db.close()
        raise HTTPException(status_code=400, detail="Böyle bir marka zaten mevcut.")

    # Marka adını güncelle
    db_marka.marka_ad = marka.marka_ad.strip()
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

# Araç Listeleme (GET)
@app.get("/araclar/")
def read_araclar():
    db = SessionLocal()
    araclar = db.query(AracBilgileri).all()
    db.close()
    return araclar

# Araç Ekleme (POST)
@app.post("/araclar/")
def create_arac(arac: AracBilgileriCreate):
    db = SessionLocal()

    # 1. "marka_id" doğruluğunu kontrol et
    marka = db.query(Marka).filter(Marka.marka_id == arac.marka_id).first()
    if not marka:
        db.close()
        raise HTTPException(status_code=400, detail="Marka ID eksik veya hatalı.")

    # 2-6. Girilen değerlerdeki boşlukları temizle
    arac.seri = arac.seri.strip()
    arac.renk = arac.renk.strip()
    arac.yakit = arac.yakit.strip()
    arac.durum = arac.durum.strip()
    arac.yakit_gucu = arac.yakit_gucu.strip()

    # "yil" kontrolü - İçinde bulunduğumuz yıldan büyük olamaz, negatif olamaz
    current_year = datetime.now().year
    if arac.yil > current_year or arac.yil < 0:
        db.close()
        raise HTTPException(status_code=400, detail="Yıl değeri geçersiz. Yıl, içinde bulunduğumuz yıldan büyük veya negatif olamaz.")

    # "kilometre" kontrolü - Negatif olamaz
    if arac.kilometre < 0:
        db.close()
        raise HTTPException(status_code=400, detail="Kilometre değeri negatif olamaz.")

    # Yeni araç kaydını oluştur
    db_arac = AracBilgileri(**arac.dict())
    db.add(db_arac)
    db.commit()
    db.refresh(db_arac)
    db.close()
    return db_arac
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
