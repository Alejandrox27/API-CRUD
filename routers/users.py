from fastapi import APIRouter, HTTPException, status
from models.users_models import User
from db.client import client_db
from schemas.user_schema import user_schema
from bson import ObjectId

router = APIRouter(prefix="/users",
                   tags=["users"],
                   responses={status.HTTP_404_NOT_FOUND : {"message": "User not found"}})

@router.get("/")
async def get_users():
    pass

@router.post("/")
async def create_user(user: User, response_model=User ,status_code=status.HTTP_201_CREATED):
    if type(search_user("email", user.email)) == User:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe")
    
    new_user = dict(user)
    del new_user["id"]
    
    id = client_db.users.insert_one(new_user).inserted_id
    
    new_user = search_user("_id", id)
    
    return new_user
    
def search_user(field: str, key):
    user_find = client_db.users.find_one({field: key})
    
    if user_find != None:
        return User(**user_schema(user_find))
    return False