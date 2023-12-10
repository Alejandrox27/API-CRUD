from fastapi import APIRouter, HTTPException, status
from models.users_models import User, User_output
from db.client import client_db
from schemas.user_schema import user_schema, users_schema
from bson import ObjectId
from passlib.context import CryptContext

crypt = CryptContext(schemes=["bcrypt"])

router = APIRouter(prefix="/users",
                   tags=["users"],
                   responses={status.HTTP_404_NOT_FOUND : {"message": "User not found"}})

@router.get("/", response_model=list, status_code=status.HTTP_200_OK)
async def get_users():
    users = client_db.users.find()
    
    return users_schema(users)

@router.get("/get-user", response_model=User_output, status_code=status.HTTP_200_OK)
async def get_user(id: str):
    try:
        user = search_user("_id", ObjectId(id))
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")
    if type(user) == User_output:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist")

@router.post("/", response_model=User_output, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    if type(search_user("email", user.email)) == User_output:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="The user already exists")
    
    new_user = dict(user)
    del new_user["id"]
    new_user["email"] = str(new_user["email"]).lower()
    new_user["password"] = crypt.hash(new_user["password"])
    
    id = client_db.users.insert_one(new_user).inserted_id
    
    user_find = search_user("_id", id)
    
    return user_find
    
@router.put("/", response_model=User_output, status_code=status.HTTP_200_OK)  
async def update_user(user: User):
    found_user = search_user("email", user.email)
    if found_user != None:
        if user.email == found_user.email and user.id != found_user.id:
            raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="That email is already in use by another user")
    
    new_user = dict(user)
    del new_user["id"]
    new_user["email"] = str(new_user["email"]).lower()
    new_user["password"] = crypt.hash(new_user["password"])
    
    try:
        client_db.users.find_one_and_replace({"_id": ObjectId(user.id)}, new_user)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")
    
    return search_user("_id", ObjectId(user.id))

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str):
    try:
        client_db.users.find_one_and_delete({"_id": ObjectId(id)})
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")
    
def search_user(field: str, key):
    user_find = client_db.users.find_one({field: key})
    
    if user_find != None:
        return User_output(**user_schema(user_find))
    return None