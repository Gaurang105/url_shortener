from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List

class URLBase(BaseModel):
    original_url: HttpUrl

class URLCreate(URLBase):
    pass

class URL(URLBase):
    id: int
    short_url: str
    clicks: int
    created_at: datetime
    user_id: int
    is_active: bool

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    urls: List[URL] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None