from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_pg_session
from app.schemas.user import UserCreate, UserResponse, Token
from app.models.user import User
from app.services.auth_service import (
    get_user_by_email,
    get_password_hash,
    verify_password,
    create_access_token
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_pg_session)):
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Make the first user an admin, others regular users
    # In a real app, this logic would be more sophisticated
    # But for this demo, we'll just check if there are any users
    from sqlalchemy.future import select
    from sqlalchemy import func
    
    count_stmt = select(func.count()).select_from(User)
    count_result = await db.execute(count_stmt)
    user_count = count_result.scalar()
    
    role = "admin" if user_count == 0 else "user"
    
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_pg_session)):
    user = await get_user_by_email(db, form_data.username) # OAuth2 uses 'username' field for email
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}
