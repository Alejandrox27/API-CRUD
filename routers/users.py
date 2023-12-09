from fastapi import APIRouter, HTTPException, status
from models.users_models import User, User_output
from db.client import client_db
from schemas.user_schema import user_schema, users_schema
from bson import ObjectId

router = APIRouter(prefix="/users",
                   tags=["users"],
                   responses={status.HTTP_404_NOT_FOUND : {"message": "User not found"}})

@router.get("/")
async def get_users():
    users = client_db.users.find()
    
    return users_schema(users)

@router.post("/", response_model=User_output, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    if type(search_user("email", user.email)) == User_output:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe")
    
    new_user = dict(user)
    del new_user["id"]
    new_user["email"] = str(new_user["email"]).lower()
    
    id = client_db.users.insert_one(new_user).inserted_id
    
    user_find = search_user("_id", id)
    
    return user_find
    
def search_user(field: str, key):
    user_find = client_db.users.find_one({field: key})
    
    if user_find != None:
        return User_output(**user_schema(user_find))
    return False