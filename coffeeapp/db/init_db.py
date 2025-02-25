from sqlalchemy.orm import Session
from coffeeapp.db.base import Base
from coffeeapp.db.session import engine, SessionLocal
from coffeeapp.core.security import get_password_hash
from coffeeapp.models.user import User, UserRole

def init_db():
    # Создаем все таблицы заново
    Base.metadata.create_all(bind=engine)
    
    # Создаем админа если его нет
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            admin = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            print("Admin created successfully")
    finally:
        db.close() 