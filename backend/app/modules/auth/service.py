from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.schemas import TokenResponse, UserCreate, UserLogin


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, payload: UserCreate) -> TokenResponse:
        existing = self.db.scalar(select(User).where(User.email == payload.email.lower()))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

        user = User(
            full_name=payload.full_name,
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._token_for_user(user)

    def login(self, payload: UserLogin) -> TokenResponse:
        user = self.db.scalar(select(User).where(User.email == payload.email.lower()))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
        return self._token_for_user(user)

    def _token_for_user(self, user: User) -> TokenResponse:
        access_token = create_access_token(str(user.id))
        return TokenResponse(access_token=access_token, user=user)

