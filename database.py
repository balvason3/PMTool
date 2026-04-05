# --- BEDROCK: ORM DATABASE MODULE ---
import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, event, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, 'bedrock.db')

engine = create_engine(f'sqlite:///{DB_FILE}', connect_args={'check_same_thread': False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

Base = declarative_base()

# --- CORE PROJECT TABLES ---
class Project(Base):
    __tablename__ = 'projects'
    internal_id = Column(Integer, primary_key=True, autoincrement=True)
    Project_ID = Column(String, unique=True, nullable=True)
    Quote_Number = Column(String, unique=True, nullable=True)
    Status = Column(String, default='Draft')
    Timestamp = Column(String)
    Project_Name = Column("Project", String)
    Client = Column(String)
    Target_Date = Column(String)
    Scope = Column(Text)
    Total_Ex_GST = Column(Float, default=0.0)
    GST = Column(Float, default=0.0)
    Total_Inc_GST = Column(Float, default=0.0)
    items = relationship("ProjectItem", back_populates="project", cascade="all, delete-orphan")

class ProjectItem(Base):
    __tablename__ = 'project_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.internal_id', ondelete="CASCADE"))
    item_type = Column(String) 
    item_data = Column(Text)   
    project = relationship("Project", back_populates="items")

# --- GLOBAL SETTINGS & SUPPLIER TABLES ---
class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    abn = Column(String, default="N/A")
    phone = Column(String, default="N/A")
    address = Column(String, default="N/A")
    payment_details = Column(String, default="N/A")

class StandardRole(Base):
    __tablename__ = 'standard_roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    rate = Column(Float, default=0.0)

class StandardMaterial(Base):
    __tablename__ = 'standard_materials'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    cost = Column(Float, default=0.0)
    unit = Column(String, default="each")
    is_assembly = Column(Boolean, default=False)
    consumables_cost = Column(Float, default=0.0)
    labor_role = Column(String, nullable=True)
    labor_hours = Column(Float, default=0.0)

class AppSetting(Base):
    __tablename__ = 'app_settings'
    key = Column(String, primary_key=True)
    value = Column(Text) # Stored as JSON string to handle both floats and dicts easily

# --- SECURITY TABLES ---
class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False) 
    permissions = Column(Text) 

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship("Role")

# Initialize
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()