from datetime import datetime
from sqlalchemy.orm import Session
from coffeeapp.db.session import get_db
from coffeeapp.models.user import User

async def cleanup_unverified_users():
    db = next(get_db())
    try:
        current_time = datetime.utcnow()
        unverified_users = (
            db.query(User)
            .filter(
                User.is_verified == False,
                User.verification_expires < current_time
            )
            .all()
        )
        
        for user in unverified_users:
            db.delete(user)
        
        db.commit()
    finally:
        db.close()

    pass 