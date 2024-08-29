import csv
import os
from typing import List
from project_csv.models import Arac

# CSV dosyasının adı
CSV_FILE = "araclar.csv"

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