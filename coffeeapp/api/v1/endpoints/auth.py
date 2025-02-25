from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Any, List

from coffeeapp.core.security import create_access_token, verify_password, get_password_hash
from coffeeapp.core.config import settings
from coffeeapp.db.session import get_db
from coffeeapp.models.user import User
from coffeeapp.schemas.user import Token, UserCreate, UserInDB, UserUpdate, UserRole
from coffeeapp.core.dependencies import get_current_user

router = APIRouter()

@router.post("/registration", response_model=UserInDB)
async def registration(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )
    
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        verification_expires=datetime.utcnow() + timedelta(days=2)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/authentication", response_model=Token)
async def authentication(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя и получение токена
    """
    print(f"Login attempt for user: {form_data.username}")
    
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user:
        print(f"User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        print(f"Invalid password for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Верифицируем пользователя при успешном входе
    if not user.is_verified:
        user.is_verified = True
        user.verification_expires = None  # Убираем срок истечения верификации
        db.commit()
        print(f"User verified: {form_data.username}")
    
    # Создаем токен
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    print(f"Login successful for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/verification")
async def verification(db: Session = Depends(get_db)):
    return {"message": "User verified"}

@router.post("/me", response_model=UserInDB)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=List[UserInDB])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка, является ли текущий пользователь администратором
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для доступа к этому ресурсу"
        )
    print(current_user)
    users = db.query(User).all()
    return users    

@router.get("/user/{user_id}", response_model=UserInDB)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return {"id": user_id}

@router.put("/user/{user_id}", response_model=UserInDB)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return {"id": user_id}

@router.patch("/user/{user_id}", response_model=UserInDB)
async def patch_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return {"id": user_id}

@router.delete("/user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    return {"message": "User deleted"}

@router.post("/access", response_model=Token)
async def get_access_token():
    return {"access_token": "new_token", "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_token():
    return {"access_token": "new_token", "token_type": "bearer"}

@router.post("/login")
async def login():
    return {"message": "Login endpoint"}

@router.patch("/user/{user_id}/role", response_model=UserInDB)
async def update_user_role(
    user_id: int,
    role_data: dict = Body(..., example={"role": "admin"}),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Изменение роли пользователя (только для админа)"""
    print(f"Current user role: {current_user.role}")  # Логируем роль текущего пользователя
    print(f"Requested role change: {role_data}")      # Логируем данные запроса
    
    if current_user.role != UserRole.ADMIN:
        print(f"Access denied: user {current_user.email} is not admin")  # Логируем отказ
        raise HTTPException(
            status_code=403,
            detail="Только администратор может изменять роли"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )
    
    try:
        new_role = UserRole(role_data["role"])
        print(f"Setting new role: {new_role} for user {user.email}")  # Логируем изменение
        user.role = new_role
        db.commit()
        db.refresh(user)
        print("Role updated successfully")  # Логируем успех
        return user
    except ValueError as e:
        print(f"Invalid role value: {role_data['role']}")  # Логируем ошибку
        raise HTTPException(
            status_code=422,
            detail=f"Недопустимая роль. Допустимые значения: {[role.value for role in UserRole]}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Логируем неожиданные ошибки
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера"
        ) 