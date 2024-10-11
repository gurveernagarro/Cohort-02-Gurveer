from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

import sys
import os

# Add the src directory to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.models import User, Magazine, Plan, Subscription
from app.db.session import engine, SessionLocal
from app.db.base import Base  # Import Base from base.py
from fastapi.security import OAuth2PasswordBearer

# Create the database tables
Base.metadata.create_all(bind=engine)


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# # Root route
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the API"}


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class PlanCreate(BaseModel):
    title: str
    description: str
    renewal_period: int


class MagazineCreate(BaseModel):
    name: str
    description: str
    base_price: float
    discount_quarterly: float
    discount_half_yearly: float
    discount_annual: float


class SubscriptionCreate(BaseModel):
    plan_id: int


class PasswordResetRequest(BaseModel):
    email: str


# Utility functions
def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# User registration
@router.post("/users/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# User login
@router.post("/users/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# Token refresh
@router.post("/users/token/refresh", response_model=Token)
def refresh_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        db_user = db.query(User).filter(User.username == username).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    access_token = create_access_token(data={"sub": username})
    refresh_token = create_refresh_token(data={"sub": username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# Password reset
@router.post("/users/reset-password")
def reset_password(email: str = Query(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Implement your password reset logic here (e.g., send email with reset link)
    return {"message": "Password reset link sent"}


# User deactivation
@router.delete("/users/deactivate/{username}")
def deactivate_user(username: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.is_active = (
        False  # Assuming there is an 'is_active' field in the User model
    )
    db.commit()
    return {"message": "User deactivated"}


# Get current user
@router.get("/users/me")
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        db_user = db.query(User).filter(User.username == username).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": db_user.username, "email": db_user.email}


# Check user status
@router.get("/users/{username}")
def get_user_status(username: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user or not db_user.is_active:
        raise HTTPException(status_code=404, detail="User not found or deactivated")
    return {
        "username": db_user.username,
        "email": db_user.email,
        "is_active": db_user.is_active,
    }


# Create a new magazine
@router.post("/magazines/")
def create_magazine(
    magazine: MagazineCreate,
    db: Session = Depends(get_db),
):
    db_magazine = Magazine(
        name=magazine.name,
        description=magazine.description,
        base_price=magazine.base_price,
        discount_quarterly=magazine.discount_quarterly,
        discount_half_yearly=magazine.discount_half_yearly,
        discount_annual=magazine.discount_annual,
    )
    db.add(db_magazine)
    db.commit()
    db.refresh(db_magazine)
    return db_magazine


from models.schema import (
    MagazineRead,
    MagazineBase,
    PlanRead,
    PlanBase,
    SubscriptionCreate,
    SubscriptionUpdate,
)


# Get all magazines
@router.get("/magazines/", response_model=List[MagazineRead])
def get_magazines(db: Session = Depends(get_db)):
    return db.query(Magazine).all()


# Get a single magazine by ID
@router.get("/magazines/{magazine_id}", response_model=MagazineRead)
def get_magazine(
    magazine_id: int,
    db: Session = Depends(get_db),
):
    db_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    return db_magazine


# Update a magazine
@router.put("/magazines/{magazine_id}", response_model=MagazineRead)
def update_magazine(
    magazine_id: int,
    magazine: MagazineBase,
    db: Session = Depends(get_db),
):
    db_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")

    db_magazine.name = magazine.name
    db_magazine.description = magazine.description
    db_magazine.base_price = magazine.base_price
    db_magazine.discount_quarterly = magazine.discount_quarterly
    db_magazine.discount_half_yearly = magazine.discount_half_yearly
    db_magazine.discount_annual = magazine.discount_annual

    db.commit()
    db.refresh(db_magazine)
    return db_magazine


# Delete a magazine
@router.delete("/magazines/{magazine_id}", response_model=MagazineRead)
def delete_magazine(
    magazine_id: int,
    db: Session = Depends(get_db),
):
    db_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")

    db.delete(db_magazine)
    db.commit()
    return db_magazine


# Create a new plan
@router.post("/plans/")
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    try:
        db_plan = Plan(
            title=plan.title,
            description=plan.description,
            renewal_period=plan.renewal_period,
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan
    except Exception as e:
        raise HTTPException(status_code=422, detail="Internal Server Error")


# Get all plans
@router.get("/plans/", response_model=List[PlanRead])
def get_plans(db: Session = Depends(get_db)):
    return db.query(Plan).all()


# Get a single plan by ID
@router.get("/plans/{plan_id}", response_model=PlanRead)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan


# Update a plan
@router.put("/plans/{plan_id}", response_model=PlanRead)
def update_plan(
    plan_id: int,
    plan: PlanBase,
    db: Session = Depends(get_db),
):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    db_plan.title = plan.title
    db_plan.description = plan.description
    db_plan.renewal_period = plan.renewal_period

    db.commit()
    db.refresh(db_plan)
    return db_plan


# Delete a plan
@router.delete("/plans/{plan_id}", response_model=PlanRead)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    db.delete(db_plan)
    db.commit()
    return db_plan


from models.schema import SubscriptionRead


@router.post("/subscriptions/", response_model=SubscriptionRead)
def create_subscription(
    subscription: SubscriptionCreate, db: Session = Depends(get_db)
):
    db_subscription = Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@router.get("/subscriptions/", response_model=List[SubscriptionRead])
def get_subscriptions(db: Session = Depends(get_db)):
    return db.query(Subscription).all()


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionRead)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionRead)
def update_subscription(
    subscription_id: int,
    subscription: SubscriptionUpdate,
    db: Session = Depends(get_db),
):
    db_subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    for key, value in subscription.dict().items():
        setattr(db_subscription, key, value)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@router.delete("/subscriptions/{subscription_id}", response_model=SubscriptionRead)
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    db_subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db_subscription.is_active = False
    db.commit()
    db.refresh(db_subscription)
    return db_subscription
