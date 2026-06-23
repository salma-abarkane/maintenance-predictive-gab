from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    population = Column(Integer, nullable=False)
    male = Column(Integer, nullable=False)
    female = Column(Integer, nullable=False)
    pct_under15 = Column(Float, nullable=False)
    pct_15_59 = Column(Float, nullable=False)
    pct_over60 = Column(Float, nullable=False)
    agencies = relationship('Agency', back_populates='city_ref')

class Agency(Base):
    __tablename__ = 'agencies'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, ForeignKey('cities.name'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    atms = relationship('ATM', back_populates='agency_ref')
    city_ref = relationship('City', back_populates='agencies')

class ATM(Base):
    __tablename__ = 'atms'
    id = Column(Integer, primary_key=True, index=True)
    serial = Column(String, unique=True, nullable=False)
    agency_id = Column(Integer, ForeignKey('agencies.id'), nullable=False)
    location = Column(String, nullable=False)
    year_installed = Column(Integer, nullable=False)
    agency_ref = relationship('Agency', back_populates='atms')
    incidents = relationship('Incident', back_populates='atm_ref')

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
