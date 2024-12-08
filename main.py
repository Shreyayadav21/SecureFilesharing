from fastapi import FastAPI
from routes import operational_user, client_user
from database import base, engine

base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(operational_user.router, prefix="/ops", tags=["Ops User"])
app.include_router(client_user.router, prefix="/client", tags=["Client User"])
