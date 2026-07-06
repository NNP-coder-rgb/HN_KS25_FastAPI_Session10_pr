
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = "mysql+pymysql://root:Ngmai2804@localhost/ecommerce_db"

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(
    autoflush = False,
    bind = engine,
    autocommit = False
)

Base = declarative_base()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()



