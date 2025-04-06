from fastapi import FastAPI

# Import uniquement le routeur de copie
from app.routes.copy import router as copy_router

app = FastAPI(title="Toolbox API (Test)", version="1.0.0")

# Inclure uniquement le routeur de copie
app.include_router(copy_router)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Toolbox (Test)"} 