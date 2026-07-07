from database import Base
from sqlalchemy import Column, Integer, String, Float

class SmartHomePlanModel(Base):
    __tablename__ = 'smart_home_plans'

    id = Column(Integer, primary_key=True, index=True)
    plan_code = Column(String(50), nullable=False, unique=True, index=True)
    plan_name = Column(String(255), nullable=False)
    device_quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
