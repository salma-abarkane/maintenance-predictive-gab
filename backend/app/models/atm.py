from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


class ATM(Base):
    __tablename__ = 'atms'

    id = Column(Integer, primary_key=True, index=True)
    serial = Column(String, unique=True, nullable=False)
    agency_id = Column(Integer, ForeignKey('agencies.id'), nullable=False)
    location = Column(String, nullable=False)
    year_installed = Column(Integer, nullable=False)

    agency_ref = relationship('Agency', back_populates='atms')
    incidents = relationship('Incident', back_populates='atm_ref')
