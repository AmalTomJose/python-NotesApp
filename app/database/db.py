from sqlalchemy import create_engine
from sqlalchemy.orm  import sessionmaker

DATABASE_URL = (
    "mssql+pyodbc://SA:'MyStrongPassword123!'@localhost:1433/NotesApp"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)




engine = create_engine(
    DATABASE_URL,
    echo=True,         
    future=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()