from __future__ import annotations

import os
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
# JWT auth disabled – removing dependency on jose

from pydantic import BaseModel, EmailStr



# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET")
# Auth disabled – no secret validation required
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE", "3600"))

origins = [
    "http://localhost",
    "http://localhost:5173",  # Vite dev server
    
]

app = FastAPI(title="Customer-Care AI Auth API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    role: str = "user"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_jwt(user: dict) -> str:
    """Auth disabled – return static token placeholder."""
    return "auth-disabled"


async def get_current_user(*_args, **_kwargs) -> dict:
    """Auth disabled – always returns an anonymous user object."""
    return {"id": "anonymous", "email": "anonymous@example.com", "role": "anonymous"}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterIn):

    raise HTTPException(status_code=501, detail="User registration is not implemented.")



@app.post("/login", response_model=TokenOut)
async def login(data: LoginIn):

    raise HTTPException(status_code=501, detail="User login is not implemented.")



@app.get("/me", response_model=UserOut)
async def me() -> UserOut:
    return UserOut(id="anonymous", email="anonymous@example.com", role="anonymous")
