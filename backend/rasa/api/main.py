from __future__ import annotations

import os
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr



# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
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

# Simple in-memory user store and password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
users_db: dict[str, dict] = {}


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
    """Create a JWT with user claims (including role)."""
    from datetime import datetime, timedelta

    payload = {
        "sub": user["id"],
        "email": user["email"],
        "role": user.get("role", "user"),
        "exp": datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(authorization: str = Header(None)) -> dict:
    """Dependency that validates JWT in Authorization header (Bearer token)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc
    return payload  # Return claims


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterIn):
    """Register a new user and return a JWT."""

    if data.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    user = {
        "id": data.email,
        "email": data.email,
        "name": data.name,
        "password_hash": pwd_context.hash(data.password),
        "role": "user",
    }
    users_db[data.email] = user
    token = _create_jwt(user)
    return TokenOut(access_token=token)



@app.post("/login", response_model=TokenOut)
async def login(data: LoginIn):
    """Authenticate a user and return a JWT."""

    user = users_db.get(data.email)
    if not user or not pwd_context.verify(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = _create_jwt(user)
    return TokenOut(access_token=token)



@app.get("/me", response_model=UserOut)
async def me(claims: dict = Depends(get_current_user)):
    return UserOut(
        id=claims["sub"],
        email=claims["email"],
        name=claims.get("name"),
        role=claims.get("role", "user"),
    )
