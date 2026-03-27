from app.database.db import engine
from app.database.base import Base

# import models here
from app.models import user, note, tag  # IMPORTANT

def init_db():
    Base.metadata.create_all(bind=engine)