# database/db_config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use MySQL instead of SQLite
DATABASE_URL = "mysql+pymysql://root:@localhost/fitme_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()