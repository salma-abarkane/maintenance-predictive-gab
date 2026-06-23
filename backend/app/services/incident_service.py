from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


class Incident(Base):
    __tablename__ = 'incidents'

    id = Column(Integer, primary_key=True, index=True)
    atm_id = Column(Integer, ForeignKey('atms.id'), nullable=False)
    agency_id = Column(Integer, ForeignKey('agencies.id'), nullable=False)
    city = Column(String, nullable=False)
    category = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    reported_at = Column(DateTime, nullable=False)

    atm_ref = relationship('ATM', back_populates='incidents')