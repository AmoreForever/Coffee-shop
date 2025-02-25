from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from coffeeapp.models.order import OrderStatus

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int = Field(...)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total_amount: float = Field(default=0.0)

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):  
    status: Optional[OrderStatus] = None
    total_amount: Optional[float] = None

class Order(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    created_at: datetime
    items: List[OrderItem]

    class Config:
        from_attributes = True
        
    
    @classmethod
    def from_orm(cls, obj):
        
        if not hasattr(obj, 'user_id'):
            obj.user_id = getattr(obj, 'user_id', None)
        if not hasattr(obj, 'status'):
            obj.status = getattr(obj, 'status', OrderStatus.PENDING)
        if not hasattr(obj, 'total_amount'):
            obj.total_amount = getattr(obj, 'total_amount', 0.0)
        return super().from_orm(obj)