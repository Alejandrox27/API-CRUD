from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from models.products_models import Product
from db.client import client_db
from schemas.product_schema import product_schema, products_schema

router = APIRouter(prefix="/products",
                   tags=["products"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "product not found"}}
                   )

@router.get("/", response_model=list, status_code=status.HTTP_200_OK)
async def get_products():
    products_ = client_db.products.find()
    
    products = products_schema(products_)
    
    return products

@router.get("/get-product", response_model=Product, status_code=status.HTTP_200_OK)
async def get_product(name: str = "", id: str = "", supplier: str = ""):
    exception_var = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if name == "" and id == "" and supplier == "":
        raise exception_var
    
    parameters_ = {"name": name, "_id": id, "supplier": supplier}
    parameters = dict()
    for key, value in parameters_.items():
        if value != "":
            parameters[key] = value
    
    try:
        if "_id" in parameters.keys():
            parameters["_id"] = ObjectId(parameters["_id"])
    except:
        raise exception_var
    
    try:
        product = client_db.products.find_one(parameters)
    except:
        raise exception_var
        
    if product is None:
        raise exception_var
    
    product_sch = product_schema(product)
    product_mod = Product(**product_sch)
    
    return product_mod

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: Product):
    product = dict(product)
    del product["id"]
    
    id = client_db.products.insert_one(product).inserted_id
    
    return search_product("_id", id)
    
def search_product(field: str, key) -> Product:
    product_db = client_db.products.find_one({field: key})
    
    if product_db != None:
        return Product(**product_schema(product_db))
    return product_db