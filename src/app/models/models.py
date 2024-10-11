from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

import sys
import os

# Add the src directory to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Integer, default=1)


class Magazine(Base):
    __tablename__ = "magazines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    base_price = Column(Float, nullable=False)
    discount_quarterly = Column(Float)
    discount_half_yearly = Column(Float)
    discount_annual = Column(Float)

    def __init__(
        self,
        name,
        description,
        base_price,
        discount_quarterly=0.0,
        discount_half_yearly=0.0,
        discount_annual=0.0,
    ):
        if base_price <= 0:
            raise ValueError("base_price must be greater than zero")
        self.name = name
        self.description = description
        self.base_price = base_price
        self.discount_quarterly = discount_quarterly
        self.discount_half_yearly = discount_half_yearly
        self.discount_annual = discount_annual


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    renewal_period = Column(Integer, nullable=False)
    # discount = Column(Float, nullable=False)
    # tier = Column(Integer, nullable=False)

    def __init__(self, title, description, renewal_period):
        if renewal_period <= 0:
            raise ValueError("renewal_period must be greater than zero")
        self.title = title
        self.description = description
        self.renewal_period = renewal_period
        # self.discount = discount
        # self.tier = tier


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    magazine_id = Column(Integer, ForeignKey("magazines.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    price = Column(Float, nullable=False)
    next_renewal_date = Column(Date)
    is_active = Column(Boolean, default=True)

    magazine = relationship("Magazine")
    plan = relationship("Plan")

    # def __init__(self, user_id, magazine_id, plan_id, renewal_date, is_active=True):
    #     self.user_id = user_id
    #     self.magazine_id = magazine_id
    #     self.plan_id = plan_id
    #     self.renewal_date = renewal_date
    #     self.is_active = is_active
    #     self.price = self.calculate_price()

    def calculate_price(self):
        magazine = self.magazine
        plan = self.plan
        return magazine.base_price * (1 - plan.discount)

    def deactivate(self):
        self.is_active = False
