from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import create_access_token
from tables import User, File
from database import get_db
from typing import List
import auth
from routes.operational_user import get_current_user

router = APIRouter()

@router.post("/signup")
def signup(username: str, email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = auth.get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password, role="client_user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Sign up successful", "user_id": user.id}

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Include both username (sub) and role in the payload
    access_token = create_access_token({"sub": user.username, "role": user.role})

    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/files")
def list_files(db: Session = Depends(get_db)):
    files = db.query(File).all()
    return files

def download_file(file_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Check if the file is owned by the client user
    if file.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to download this file")

    return {"file": file.filename, "filepath": file.filepath}