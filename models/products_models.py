from pydantic import BaseModel

class Product(BaseModel):
    id: str | None = None
    name: str
    stock: int
    supplier: str