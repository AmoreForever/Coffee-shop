from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from coffeeapp.core.dependencies import get_current_user
from coffeeapp.db.session import get_db
from coffeeapp.models.user import User
from coffeeapp.models.cart import Cart, CartItem
from coffeeapp.models.product import Product
from coffeeapp.schemas.cart import CartItemCreate, Cart as CartSchema

router = APIRouter()

@router.post("/cart")
async def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Добавление товара в корзину"""
    # Получаем или создаем корзину для пользователя
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    # Проверяем существование продукта
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    
    # Проверяем, есть ли уже такой товар в корзине
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item.product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart)
    return {"message": "Товар добавлен в корзину"}

@router.get("/cart", response_model=CartSchema)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение корзины пользователя"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Корзина пуста")
    return cart

@router.delete("/cart/{item_id}")
async def remove_from_cart(item_id: int, db: Session = Depends(get_db)):
    return {"message": "Item removed from cart"}

@router.delete("/cart")
async def clear_cart(db: Session = Depends(get_db)):
    return {"message": "Cart cleared"} 