from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from models.users_models import User, User_output
from db.client import client_db
from schemas.user_schema import user_schema

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 5
SECRET = "$2a$12$7asYsMgR3Zkvp.OZXEff.uvC7UXPH5twGB9W.xOOTO8JngjxrYCyC"

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(tags=["jwtLogin"])

crypt = CryptContext(schemes=["bcrypt"])

async def auth_user(token: str = Depends(oauth2)):
    exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid auth credentials", 
            headers={"WWW-Authenticate": "Bearer"})
    
    try:
        user = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")
        print(user)
        if user is None:
            raise exception
    except JWTError:
        raise exception
    
    return search_user(user)

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = client_db.users.find_one({"username": form.username})
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not crypt.verify(form.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="wrong password")
    
    access_token = {"sub": user["username"],
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}
    
    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@router.get("/me", status_code=status.HTTP_200_OK)
async def user_me(user: User_output = Depends(auth_user)):
    return user

def search_user(username: str) -> User_output:
    user = client_db.users.find_one({"username": username})
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return User_output(**user_schema(user))