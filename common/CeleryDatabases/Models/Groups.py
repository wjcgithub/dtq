from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,String, Integer, DateTime

Base = declarative_base()

class Groups(Base):
    __tablename__ = 'groups'

    id = Column('id', Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    mastername = Column(String(45), nullable=False)
    ctime = Column(DateTime, nullable=False)
    lastmasterid = Column(Integer)
    status = Column(String(1))