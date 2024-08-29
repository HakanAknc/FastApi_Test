from pydantic import BaseModel

class Person(BaseModel):
    id : int
    name : str
    surname : str
    job : str
    age : int

# Person modelini kullanarak bir nesne oluşturalım
person = Person(id=1, name="Hakan", surname="Akıncı", job="Developer", age=30)

# Nesneyi yazdıralım
print(person)

