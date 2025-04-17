from sqlalchemy import Column,BigInteger, Numeric, Integer, String, ARRAY, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship



Base = declarative_base()


class User(Base):
  __tablename__ = "users"

  user_id = Column(BigInteger, primary_key=True)
  user_segment = Column(String)
  quiz_result = Column(ARRAY(String))
  created_at = Column(DateTime, default=func.now())
  udated_at = Column(DateTime, default=func.now(), onupdate=func.now())

  payments = relationship("Payment", back_populates="user")

  def __repr__(self):
    return f"<User(user_id={self.user_id}, user_segment={self.user_segment}, quiz_result={self.quiz_result})>"
  


class Payment(Base):
  __tablename__ = "payments"

  payment_id = Column(Integer, primary_key=True, autoincrement=True)
  user_id = Column(BigInteger, ForeignKey("user.user_id"))
  payment_date = Column(DateTime, default=func.now())
  payment_amount = Column(Numeric)
  payment_status = Column(String)
  yokassa_payment_id = Column(String, unique=True)
  created_at = Column(DateTime, default=func.now())

  user = relationship("User", back_populates="payments")

  def __repr__(self):
        return f"<Payment(payment_id={self.payment_id}, amount={self.payment_amount}, status='{self.payment_status}')>"