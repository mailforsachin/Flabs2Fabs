import os

# Define the complete structure with file contents
structure = {
    "flabs2fabs/": {
        "backend/": {
            "requirements.txt": """fastapi
uvicorn
python-jose
passlib[bcrypt]
sqlalchemy
pymysql
python-dotenv""",
            ".env": """DATABASE_URL=mysql+pymysql://root:password@localhost:3306/flab2fabs
JWT_SECRET=super-secret-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
ADMIN_USERNAME=admin""",
            "app/": {
                "__init__.py": "",
                "main.py": """from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, admin, system

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flab2Fabs API")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(system.router)""",
                "config.py": """from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_USERNAME: str

    class Config:
        env_file = ".env"

settings = Settings()""",
                "database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()""",
                "models.py": """from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)""",
                "schemas.py": """from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AdminCreateUser(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False

class AdminResetPassword(BaseModel):
    user_id: int
    new_password: str""",
                "auth.py": """from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_access_token(user_id: int):
    return create_token(
        {"sub": str(user_id)},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_refresh_token(user_id: int):
    return create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )""",
                "dependencies.py": """from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models import User

def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive")

    return user

def admin_required(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user""",
                "routes/": {
                    "__init__.py": "",
                    "auth.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse
from app.auth import verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id)
    }""",
                    "admin.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AdminCreateUser, AdminResetPassword
from app.models import User
from app.auth import hash_password
from app.dependencies import admin_required

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/create-user")
def create_user(data: AdminCreateUser, db: Session = Depends(get_db), _=Depends(admin_required)):
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        is_admin=data.is_admin
    )
    db.add(user)
    db.commit()
    return {"status": "user_created"}

@router.post("/reset-password")
def reset_password(data: AdminResetPassword, db: Session = Depends(get_db), _=Depends(admin_required)):
    user = db.query(User).filter(User.id == data.user_id).first()
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"status": "password_reset"}""",
                    "system.py": """from fastapi import APIRouter

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/health")
def health():
    return {"status": "ok"}"""
                }
            }
        }
    }
}

def create_structure(base_path, structure_dict):
    """Recursively create directory and file structure"""
    for item, content in structure_dict.items():
        # Remove trailing slash for directory names
        if item.endswith('/'):
            item = item.rstrip('/')
            
        path = os.path.join(base_path, item)
        
        if isinstance(content, dict):  # It's a directory
            os.makedirs(path, exist_ok=True)
            print(f"📁 Created directory: {path}/")
            create_structure(path, content)
        else:  # It's a file
            with open(path, 'w') as f:
                f.write(content)
            print(f"📄 Created file: {path}")

# Create the structure
print("🚀 Creating Flabs2Fabs project structure...\n")
create_structure("", structure)

print("\n" + "="*50)
print("✅ Project structure created successfully!")
print("="*50)
print("\nNext steps:")
print("1. cd flabs2fabs/backend")
print("2. pip install -r requirements.txt")
print("3. Make sure MySQL is running")
print("4. Create database: CREATE DATABASE flab2fabs;")
print("5. Run: uvicorn app.main:app --reload")
print("\nAPI will be available at: http://localhost:8000")
print("Docs: http://localhost:8000/docs")
