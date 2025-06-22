from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr

from ..supabase_client import get_supabase_client

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE", "3600"))

origins = [
    "http://localhost",
    "http://localhost:5173",  # Vite dev server
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return payload  # Return claims


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterIn):
    supa = get_supabase_client()

    # Create Supabase user
    resp = supa.auth.sign_up({"email": data.email, "password": data.password, "options": {"data": {"name": data.name}}})
    if resp["error"]:
        raise HTTPException(status_code=400, detail=resp["error"]["message"])
    user = resp["user"]
    # Ensure a profile row with default role
    supa.table("profiles").upsert({"id": user["id"], "name": data.name, "role": "user"}).execute()

    # Issue custom JWT embedding role claim
    token = _create_jwt({"id": user["id"], "email": data.email, "role": "user"})
    return TokenOut(access_token=token)


@app.post("/login", response_model=TokenOut)
async def login(data: LoginIn):
    supa = get_supabase_client()
    resp = supa.auth.sign_in_with_password({"email": data.email, "password": data.password})
    if resp["error"]:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    user = resp["user"]
    # Fetch user role from profile table
    profile_query = supa.table("profiles").select("role, name").eq("id", user["id"]).single().execute()
    role = profile_query.data.get("role", "user") if profile_query.data else "user"
    token = _create_jwt({"id": user["id"], "email": data.email, "role": role})
    return TokenOut(access_token=token)


@app.get("/me", response_model=UserOut)
async def me(claims: dict = Depends(get_current_user)):
    return UserOut(
        id=claims["sub"],
        email=claims["email"],
        name=claims.get("name"),
        role=claims.get("role", "user"),
    )
