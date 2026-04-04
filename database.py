# --- BEDROCK: ORM DATABASE MODULE ---
import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, event
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, 'bedrock.db')

# 1. Setup the Engine
# We use check_same_thread=False so multiple NiceGUI web workers can safely use it.
engine = create_engine(f'sqlite:///{DB_FILE}', connect_args={'check_same_thread': False})

# 2. Enable WAL Mode & Foreign Keys for SQLite Concurrency
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL") # Allows concurrent read/writes!
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

Base = declarative_base()

# 3. Define the Schema (Tables) as Python Classes

class Project(Base):
    __tablename__ = 'projects'

    internal_id = Column(Integer, primary_key=True, autoincrement=True)
    Project_ID = Column(String, unique=True, nullable=True)
    Quote_Number = Column(String, unique=True, nullable=True)
    Status = Column(String, default='Draft')
    Timestamp = Column(String)
    Project_Name = Column("Project", String) # Mapped to your old dictionary key
    Client = Column(String)
    Target_Date = Column(String)
    Scope = Column(Text)
    Total_Ex_GST = Column(Float, default=0.0)
    GST = Column(Float, default=0.0)
    Total_Inc_GST = Column(Float, default=0.0)

    # Link to items
    items = relationship("ProjectItem", back_populates="project", cascade="all, delete-orphan")

class ProjectItem(Base):
    """
    Maintains compatibility with your current JSON list structures 
    while giving them a proper relational home.
    """
    __tablename__ = 'project_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.internal_id', ondelete="CASCADE"))
    item_type = Column(String) # 'Labor', 'Material', or 'Note'
    item_data = Column(Text)   # JSON string of the dictionary

    project = relationship("Project", back_populates="items")

# --- PHASE 0 PREP: SECURITY TABLES ---

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False) # e.g., 'Admin', 'User'
    permissions = Column(Text) # JSON string of allowed actions

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    
    role = relationship("Role")

# 4. Initialize Database & Session
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Yields a database session for performing queries."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()