from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from coffeeapp.core.dependencies import get_current_user
from coffeeapp.db.session import get_db
from coffeeapp.models.user import User, UserRole
from coffeeapp.models.product import Product
from coffeeapp.schemas.product import ProductCreate, ProductUpdate, Product as ProductSchema

router = APIRouter()

@router.post("/product", response_model=ProductSchema)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание нового продукта"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Только администратор может создавать продукты")
    
    product = Product(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/products", response_model=List[ProductSchema])
def get_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Поиск по названию"),
    category_id: Optional[int] = Query(None, description="Фильтр по категории"),
    min_price: Optional[float] = Query(None, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, description="Максимальная цена"),
    sort_by: Optional[str] = Query(None, description="Сортировка (name, price)")
):
    """Получение списка продуктов с фильтрацией, сортировкой и пагинацией"""
    query = db.query(Product)
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    
    if sort_by:
        if sort_by == "name":
            query = query.order_by(Product.name)
        elif sort_by == "price":
            query = query.order_by(Product.price)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/product/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Получение продукта по ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return product

@router.put("/product/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление продукта"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    
    for field, value in product_in.dict(exclude_unset=True).items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.patch("/product/{product_id}", response_model=ProductSchema)
def patch_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Частичное обновление продукта"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    
    for field, value in product_in.dict(exclude_unset=True).items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/product/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление продукта"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    
    db.delete(product)
    db.commit()
    return {"message": "Продукт успешно удален"} 