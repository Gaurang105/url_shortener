from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..models import models
from ..schemas import schemas
from ..utils.url_generator import create_unique_short_url
from ..utils.auth import get_current_user
from sqlalchemy.exc import IntegrityError
from starlette.responses import RedirectResponse

router = APIRouter(prefix="/urls", tags=["urls"])

@router.post("/", response_model=schemas.URL)
def create_short_url(
    url: schemas.URLCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    while True:
        short_url = create_unique_short_url()
        db_url = db.query(models.URL).filter(models.URL.short_url == short_url).first()
        if not db_url:
            break
    
    db_url = models.URL(
        original_url=str(url.original_url),
        short_url=short_url,
        clicks=0,
        user_id=current_user.id
    )
    
    try:
        db.add(db_url)
        db.commit()
        db.refresh(db_url)
        return db_url
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating URL")

@router.get("/{short_url}")
def redirect_to_url(short_url: str, db: Session = Depends(get_db)):
    db_url = db.query(models.URL).filter(models.URL.short_url == short_url).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Increment click count
    db_url.clicks += 1
    db.commit()
    
    return RedirectResponse(url=db_url.original_url)

@router.get("/stats/{short_url}", response_model=schemas.URL)
def get_url_stats(
    short_url: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_url = db.query(models.URL).filter(models.URL.short_url == short_url).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if db_url.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view these stats")
    
    return db_url

@router.get("/my-urls/", response_model=List[schemas.URL])
def list_user_urls(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    urls = db.query(models.URL)\
        .filter(models.URL.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return urls

@router.delete("/{short_url}")
def delete_url(
    short_url: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_url = db.query(models.URL).filter(models.URL.short_url == short_url).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if db_url.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this URL")
    
    db.delete(db_url)
    db.commit()
    return {"message": "URL deleted successfully"}