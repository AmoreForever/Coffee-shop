from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from coffeeapp.core.dependencies import get_current_user
from coffeeapp.db.session import get_db
from coffeeapp.models.user import User, UserRole
from coffeeapp.models.order import Order, OrderItem, OrderStatus
from coffeeapp.models.cart import Cart
from coffeeapp.schemas.order import Order as OrderSchema, OrderCreate, OrderUpdate

router = APIRouter()

@router.post("/", response_model=OrderSchema)
def create_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание заказа из корзины"""
    # Получаем корзину пользователя
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Корзина пуста")
    
    # Создаем заказ
    order = Order(user_id=current_user.id)
    db.add(order)
    db.commit()  
    db.refresh(order)
    
    total_amount = 0.0
    
    # Переносим товары из корзины в заказ
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=order.id,  
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        total_amount += order_item.price * order_item.quantity
        db.add(order_item)
    
    order.total_amount = total_amount
    
    
    for item in cart.items:
        db.delete(item)
    
    db.commit()
    db.refresh(order)
    return order

@router.get("/orders", response_model=List[OrderSchema])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Получение списка заказов пользователя"""

    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    

    return orders

@router.get("/{order_id}", response_model=OrderSchema)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение информации о заказе"""
    
    order = db.query(Order).options(joinedload(Order.items)).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order

@router.put("/order/{order_id}", response_model=OrderSchema)
async def update_order(order_id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    return {"id": order_id, "created_at": "2024-03-20T12:00:00", "items": []}

@router.delete("/order/{order_id}")
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    return {"message": "Order deleted"}

@router.patch("/order/{order_id}", response_model=OrderSchema)
async def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление статуса заказа (только для администраторов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостаточно прав")


    
    order = db.query(Order).filter(Order.id == order_id).first()    
    
    if not order.user_id or not order.status or not order.total_amount:
        raise ValueError("Missing required order fields")
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    order.status = status
    db.commit()
    db.refresh(order)
    return order