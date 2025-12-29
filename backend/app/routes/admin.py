from fastapi import APIRouter, Depends
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
    return {"status": "password_reset"}
