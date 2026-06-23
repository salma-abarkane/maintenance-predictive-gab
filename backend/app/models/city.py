from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


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
