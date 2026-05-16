from datetime import datetime, timedelta, timezone
import hashlib
import os
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.db import Base, engine
from src.database.models import AuthSession, AuthUser
from src.database.schema import GoogleLoginRequest,RegisterRequest,LoginRequest

router = APIRouter()


def _ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"{salt}${digest.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, hex_digest = stored_hash.split("$", 1)
    except ValueError:
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return secrets.compare_digest(digest.hex(), hex_digest)


def _create_session(db: Session, user_id: int) -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    token = secrets.token_urlsafe(48)

    session = AuthSession(user_id=user_id, token=token, expires_at=expires_at)
    db.add(session)
    db.commit()

    return token, expires_at


def _get_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None

    return authorization[len(prefix):].strip() or None


def get_current_auth_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AuthUser:
    token = _get_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    session = db.query(AuthSession).filter(AuthSession.token == token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session token")

    now = datetime.now(timezone.utc)
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=401, detail="Session expired")

    user = db.query(AuthUser).filter(AuthUser.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user





@router.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    _ensure_tables()

    email = _normalize_email(req.email)
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = db.query(AuthUser).filter(AuthUser.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = AuthUser(
        name=req.name.strip() or "User",
        email=email,
        password_hash=_hash_password(req.password),
        auth_provider="password",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token, expires_at = _create_session(db=db, user_id=user.id)

    return {
        "token": token,
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "auth_provider": user.auth_provider,
        },
    }


@router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    _ensure_tables()

    email = _normalize_email(req.email)
    user = db.query(AuthUser).filter(AuthUser.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.auth_provider != "password":
        raise HTTPException(status_code=400, detail="This account uses Google sign-in")

    if not user.password_hash or not _verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token, expires_at = _create_session(db=db, user_id=user.id)

    return {
        "token": token,
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "auth_provider": user.auth_provider,
        },
    }


@router.post("/auth/google")
def google_login(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    _ensure_tables()

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID is not configured")

    try:
        token_payload = google_id_token.verify_oauth2_token(
            req.id_token,
            google_requests.Request(),
            audience=client_id,
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google ID token")

    issuer = token_payload.get("iss")
    if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
        raise HTTPException(status_code=401, detail="Invalid Google token issuer")

    if not bool(token_payload.get("email_verified", False)):
        raise HTTPException(status_code=401, detail="Google email is not verified")

    email = _normalize_email(token_payload.get("email", ""))
    google_sub = str(token_payload.get("sub", "")).strip()
    name = str(token_payload.get("name", "")).strip() or "Google User"

    if not email:
        raise HTTPException(status_code=400, detail="Email missing in Google token")
    if not google_sub:
        raise HTTPException(status_code=400, detail="sub missing in Google token")

    user = db.query(AuthUser).filter(AuthUser.email == email).first()

    if user and user.auth_provider == "password":
        raise HTTPException(status_code=409, detail="Email already exists with password login")

    if user and user.auth_provider == "google":
        if user.google_sub and user.google_sub != google_sub:
            raise HTTPException(status_code=409, detail="Google account mismatch for this email")
        user.google_sub = google_sub
        user.name = name or user.name
    else:
        existing_sub = db.query(AuthUser).filter(AuthUser.google_sub == google_sub).first()
        if existing_sub and existing_sub.email != email:
            raise HTTPException(status_code=409, detail="google_sub already used by another account")

        user = AuthUser(
            name=name,
            email=email,
            auth_provider="google",
            google_sub=google_sub,
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    token, expires_at = _create_session(db=db, user_id=user.id)

    return {
        "token": token,
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "auth_provider": user.auth_provider,
        },
    }


@router.get("/auth/me")
def me(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    _ensure_tables()

    token = _get_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    session = db.query(AuthSession).filter(AuthSession.token == token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session token")

    now = datetime.now(timezone.utc)
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=401, detail="Session expired")

    user = db.query(AuthUser).filter(AuthUser.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "auth_provider": user.auth_provider,
        }
    }


@router.post("/auth/logout")
def logout(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    _ensure_tables()

    token = _get_bearer_token(authorization)
    if not token:
        return {"status": "ok"}

    session = db.query(AuthSession).filter(AuthSession.token == token).first()
    if session:
        db.delete(session)
        db.commit()

    return {"status": "ok"}
