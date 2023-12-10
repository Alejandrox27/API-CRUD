from fastapi import FastAPI
from routers import users, products, jwt_Oauth

app = FastAPI()

app.include_router(users.router)
app.include_router(products.router)

app.include_router(jwt_Oauth.router)

@app.get("/")
async def root():
    return "Correct"