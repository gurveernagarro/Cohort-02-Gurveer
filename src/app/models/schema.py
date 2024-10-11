from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class MagazineBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_price: float
    discount_quarterly: Optional[float] = None
    discount_half_yearly: Optional[float] = None
    discount_annual: Optional[float] = None


class MagazineRead(MagazineBase):
    id: int

    class Config:
        from_attributes = True


class PlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    renewal_period: int = Field(..., gt=0)


class PlanCreate(PlanBase):
    pass


class PlanRead(PlanBase):
    id: int

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    price: float
    next_renewal_date: Optional[date] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(SubscriptionBase):
    is_active: bool = True


class SubscriptionRead(SubscriptionBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
