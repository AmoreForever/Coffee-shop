from pydantic import BaseModel
from typing import List

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItem(CartItemBase):
    id: int
    
    class Config:
        from_attributes = True

class Cart(BaseModel):
    id: int
    items: List[CartItem]
    
    class Config:
        from_attributes = True 