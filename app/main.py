from fastapi import FastAPI
from app.database.init_db import init_db
from app.auth.auth import router as auth_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()  # initialize database

app.include_router(auth_router)  # include auth routes