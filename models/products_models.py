from pydantic import BaseModel

class Product(BaseModel):
    id: str | None = None
    name: str
    stock: str
    supplier: str