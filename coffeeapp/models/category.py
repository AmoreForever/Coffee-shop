from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from coffeeapp.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    products = relationship("Product", back_populates="category") 