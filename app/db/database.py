import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Ekdum strict aur pakka absolute path jo direct root ki .env ko nikalega
env_path = "D:\\watchdog n1\\.env"

# Forcefully load load_dotenv from absolute path
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print(f"\n--- DEBUG PATH INFO ---")
    print(f"Strictly looking at: {env_path}")
    print(f"Does file exist physically?: {os.path.exists(env_path)}")
    print(f"-----------------------\n")
    raise RuntimeError(f".env file mein DATABASE_URL nahi mila! Path check karein: {env_path}")

# Supabase/PostgreSQL engine create karein (Direct connection)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()