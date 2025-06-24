import datetime
import enum
from typing import Annotated, List, Optional
from sqlalchemy import Column, BigInteger, Numeric, Integer, String, ARRAY, DateTime, ForeignKey, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column



class Base(DeclarativeBase):
   pass


created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now(datetime.timezone.utc))]

class UserSegment(enum.Enum):
   breakfast = "breakfast"
   kitchen = "kitchen"
   overeating = "overeating"
   appetit = "appetit"
   deficits = "deficits"


class User(Base):
  __tablename__ = "users"

  user_id: Mapped[str] = mapped_column(primary_key=True)
  user_segment = Mapped[Optional[UserSegment]]
  quiz_result = Mapped[List[str]]
  last_interaction = Mapped[updated_at]
  created_at = Mapped[created_at]
  updated_at = Mapped[updated_at]

  # payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="users")

  def __repr__(self) -> str:
    return f"<User(user_id={self.user_id!r}, user_segment={self.user_segment!r}, quiz_result={self.quiz_result!r}, last_interaction={self.last_interaction!r})>"
  


class Payment(Base):
  __tablename__ = "payments"

  payment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
  payment_date: Mapped[datetime.datetime]
  payment_amount: Mapped[int]
  payment_status: Mapped[str]
  yokassa_payment_id: Mapped[str] = mapped_column(unique=True)
  created_at: Mapped[created_at]

  # user: Mapped[User] = relationship("User", back_populates="payments")

  def __repr__(self) -> str:
        return f"<Payment(payment_id={self.payment_id!r}, amount={self.payment_amount!r}, status='{self.payment_status!r}')>"
  


