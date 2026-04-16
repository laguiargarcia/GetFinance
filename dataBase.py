from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Accounts(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True)
    type = Column(String(100))
    sub_type = Column(String(100))

    name = Column(String(255))
    balance = Column(Float)
    currency_code = Column(String(10))
    item_id = Column(String)

    number = Column(String(50))

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    marketing_name = Column(String(255))
    tax_number = Column(String(50))
    owner = Column(String(255))

    bankData = Column(String(300))

    credit_data = Column(String(255))