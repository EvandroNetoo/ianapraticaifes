from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[str] = None
    company: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProposalItemCreate(BaseModel):
    description: str = Field(..., min_length=1)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)


class ProposalItemResponse(ProposalItemCreate):
    id: int
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class ProposalCreate(BaseModel):
    customer_id: int
    title: str = Field(..., min_length=1)
    discount_percent: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    items: List[ProposalItemCreate] = Field(..., min_length=1)


class ProposalResponse(BaseModel):
    id: int
    customer_id: int
    title: str
    status: str
    discount_percent: Decimal
    subtotal: Decimal
    discount_amount: Decimal
    total: Decimal
    public_token: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    customer: CustomerResponse
    items: List[ProposalItemResponse]

    model_config = ConfigDict(from_attributes=True)


class PublicProposalResponse(BaseModel):
    title: str
    customer_name: str
    customer_company: Optional[str] = None
    status: str
    discount_percent: Decimal
    subtotal: Decimal
    discount_amount: Decimal
    total: Decimal
    items: List[ProposalItemResponse]
    sent_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
