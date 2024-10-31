from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import url

app = FastAPI(
    title="URL Shortener API",
    description="A simple URL shortener service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(url.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to URL Shortener API",
        "docs": "/docs",
        "redoc": "/redoc"
    }