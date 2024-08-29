from fastapi import FastAPI, HTTPException   # TODO SON SÜRÜM 1.3
from pydantic import BaseModel
from enum import Enum
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

# Yakit Enum 
class Yakit(int, Enum):
    benzin = 1
    dizel = 2
    elektrik = 3
    lpg = 4

# Durum Enum 
class Durum(int, Enum):
    sifir = 1
    ikinci_el = 2

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
    yakit = Column(Integer, nullable=False)
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
    yakit: Yakit  # Enum sınıfını burada kullanıyoruz
    durum: Durum  # Enum sınıfını burada kullanıyoruz
    kilometre: int
    yakit_gucu: str
    isActive: bool

class AracBilgileriUpdate(BaseModel):
    marka_id: str
    seri: str
    renk: str
    yil: int
    yakit: Yakit  # Enum sınıfını burada kullanıyoruz
    durum: Durum  # Enum sınıfını burada kullanıyoruz
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

    # 1. "marka_id" doğruluğunu kontrol et
    marka = db.query(Marka).filter(Marka.marka_id == arac.marka_id).first()
    if not marka:
        db.close()
        raise HTTPException(status_code=400, detail="Marka ID eksik veya hatalı.")

    db_arac = db.query(AracBilgileri).filter(AracBilgileri.arac_id == arac_id).first()
    if not db_arac:
        db.close()
        raise HTTPException(status_code=404, detail="Araç bulunamadı")

    # 2-6. Girilen değerlerdeki boşlukları temizle
    arac.seri = arac.seri.strip()
    arac.renk = arac.renk.strip()
    arac.yakit_gucu = arac.yakit_gucu.strip()

    # 7. "yil" kontrolü - İçinde bulunduğumuz yıldan büyük olamaz, negatif olamaz
    current_year = datetime.now().year
    if arac.yil > current_year or arac.yil < 0:
        db.close()
        raise HTTPException(status_code=400, detail="Yıl değeri geçersiz. Yıl, içinde bulunduğumuz yıldan büyük veya negatif olamaz.")

    # 8. "kilometre" kontrolü - Negatif olamaz
    if arac.kilometre < 0:
        db.close()
        raise HTTPException(status_code=400, detail="Kilometre değeri negatif olamaz.")

    # Güncellemeleri uygula
    db_arac.marka_id = arac.marka_id
    db_arac.seri = arac.seri
    db_arac.renk = arac.renk
    db_arac.yil = arac.yil
    db_arac.yakit = arac.yakit
    db_arac.durum = arac.durum
    db_arac.kilometre = arac.kilometre
    db_arac.yakit_gucu = arac.yakit_gucu
    db_arac.isActive = arac.isActive

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
