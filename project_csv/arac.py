from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import csv
import os

app = FastAPI()

# Veri modelini tanımla
class Arac(BaseModel):
    id: int
    marka: str
    seri: str
    renk: str
    yil: int
    yakit: str
    durum: str
    kilometre: int
    motor_gucu: int

# CSV dosyasının adı
CSV_FILE = "test/araclar.csv"

# CSV dosyasını oluştur
def create_csv_file():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'marka', 'seri', 'renk', 'yil', 'yakit', 'durum', 'kilometre', 'motor_gucu'])

# CSV dosyasını oku
def read_csv_file() -> List[Arac]:
    araclar = []
    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            arac = Arac(
                id=int(row['id']),
                marka=row['marka'],
                seri=row['seri'],
                renk=row['renk'],
                yil=int(row['yil']),
                yakit=row['yakit'],
                durum=row['durum'],
                kilometre=int(row['kilometre']),
                motor_gucu=int(row['motor_gucu'])
            )
            araclar.append(arac)
    return araclar

# CSV dosyasına yaz
def write_csv_file(araclar: List[Arac]):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'marka', 'seri', 'renk', 'yil', 'yakit', 'durum', 'kilometre', 'motor_gucu'])
        for arac in araclar:
            writer.writerow([arac.id, arac.marka, arac.seri, arac.renk, arac.yil, arac.yakit, arac.durum, arac.kilometre, arac.motor_gucu])

# Uygulama başladığında CSV dosyasını oluştur
create_csv_file()

# Araçları listeleme endpoint'i
@app.get("/araclar/", response_model=List[Arac])
def list_araclar():
    araclar = read_csv_file()
    return araclar

# Araç ekleme endpoint'i
@app.post("/araclar/")
def add_arac(arac: Arac):
    araclar = read_csv_file()
    for existing_arac in araclar:
        if existing_arac.id == arac.id:
            raise HTTPException(status_code=400, detail="Bu ID'ye sahip bir araç zaten mevcut.")
    araclar.append(arac)
    write_csv_file(araclar)
    return {"message": "Araç başarıyla eklendi."}

# Araç silme endpoint'i
@app.delete("/araclar/{arac_id}")
def delete_arac(arac_id: int):
    araclar = read_csv_file()
    araclar = [arac for arac in araclar if arac.id != arac_id]
    write_csv_file(araclar)
    return {"message": "Araç başarıyla silindi."}

# Araç güncelleme endpoint'i
@app.put("/araclar/{arac_id}")
def update_arac(arac_id: int, updated_arac: Arac):
    araclar = read_csv_file()
    for i, arac in enumerate(araclar):
        if arac.id == arac_id:
            araclar[i] = updated_arac
            write_csv_file(araclar)
            return {"message": "Araç başarıyla güncellendi."}
    raise HTTPException(status_code=404, detail="Araç bulunamadı.")

# 