from sqlalchemy import Column, Integer, String, Text
from database import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    muscle_group = Column(String, index=True, nullable=False) # np. Klatka, Plecy, Nogi, Barki, Biceps, Triceps, Brzuch
    category = Column(String, index=True) # np. Złożone, Izolowane
    equipment = Column(String, index=True, default="gym") # np. gym, dumbbells, bodyweight, bands
    description = Column(Text, nullable=True)
    images = Column(Text, nullable=True)
    gif_url = Column(String, nullable=True)
    instructions = Column(Text, nullable=True)
    name_pl = Column(String, nullable=True)
    instructions_pl = Column(Text, nullable=True)


