import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.database import Base


class ProposalStatus(str, enum.Enum):
    RASCUNHO = "rascunho"
    ENVIADA = "enviada"
    ACEITA = "aceita"
    RECUSADA = "recusada"


def utc_now():
    return datetime.now(timezone.utc)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    proposals = relationship("Proposal", back_populates="customer", cascade="all, delete-orphan")


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(
        String(50),
        default=ProposalStatus.RASCUNHO.value,
        nullable=False,
        index=True,
    )
    discount_percent = Column(Numeric(5, 2), default=0, nullable=False)
    subtotal = Column(Numeric(12, 2), default=0, nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0, nullable=False)
    total = Column(Numeric(12, 2), default=0, nullable=False)
    public_token = Column(String(64), unique=True, index=True, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer", back_populates="proposals")
    items = relationship(
        "ProposalItem",
        back_populates="proposal",
        cascade="all, delete-orphan",
        order_by="ProposalItem.id",
    )


class ProposalItem(Base):
    __tablename__ = "proposal_items"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)

    proposal = relationship("Proposal", back_populates="items")
