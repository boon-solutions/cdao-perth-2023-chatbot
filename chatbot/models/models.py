from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase
from marshmallow_sqlalchemy import SQLAlchemySchema
from datetime import datetime
import pytz

# Define tables via SQLAlchemy ORM
class Base(DeclarativeBase):
    pass

class competition(Base):
    __tablename__ = "competition"
    __table_args__ = (
        UniqueConstraint("participant_id"),
        UniqueConstraint("guess"),
        {"schema":"cdao"}
    )
    participant_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable = False)
    phone = Column(String(20))
    email = Column(String(50), nullable=False)
    company = Column(String(50))
    guess = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=False), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=False), default=datetime.now, nullable=False)
