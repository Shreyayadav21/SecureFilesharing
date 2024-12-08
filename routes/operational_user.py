from fastapi import APIRouter, Depends, HTTPException, UploadFile, security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from auth import verify_token  # Your JWT verification function
from tables import File, User
from database import get_db
import os

router = APIRouter()
security = HTTPBearer()

UPLOAD_DIR = "uploads"

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Custom dependency to extract and verify JWT token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials  # Extract the token from the Authorization header
    user = verify_token(token, db)  # Your token verification logic
    return user

@router.post("/upload")
def upload_file(
    file: UploadFile,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)  # JWT authentication dependency
):
    if user.role != "ops_user":  # Only ops_user can upload
        raise HTTPException(status_code=403, detail="Not authorized to upload files")

    # Validate file type
    if file.content_type not in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",        # .xlsx
        "application/vnd.openxmlformats-officedocument.presentationml.presentation" # .pptx
    ]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Save file to the server
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Save file metadata to the database
    db_file = File(filename=file.filename, filepath=file_path, owner_id=user.id)
    db.add(db_file)
    db.commit()

    return {"message": "File uploaded successfully"}
