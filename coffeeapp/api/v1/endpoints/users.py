from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from coffeeapp.db.session import get_db
from coffeeapp.models.user import User
from coffeeapp.core.dependencies import get_current_user

router = APIRouter()

@router.get("/")
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка, является ли текущий пользователь администратором
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для доступа к этому ресурсу"
        )
    print(current_user)
    users = db.query(User).all()
    return users    