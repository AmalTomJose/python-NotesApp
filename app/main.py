from fastapi import FastAPI
from app.database.init_db import init_db
from app.auth.auth import router as auth_router
from app.routes.notes import router as notes_router
from app.routes.favourite import router as favourites_router
from app.routes.share import router as share_router
from app.routes.admin_router import router as admin_router
app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()  

app.include_router(auth_router)  
app.include_router(notes_router) 
app.include_router(favourites_router)
app.include_router(share_router)
app.include_router(admin_router)