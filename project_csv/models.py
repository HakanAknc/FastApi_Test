from pydantic import BaseModel

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