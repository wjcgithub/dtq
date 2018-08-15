from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,String, Integer, Text, DateTime

Base = declarative_base()
class WorkConfig(Base):
    __tablename__ = 'worker_config'

    id = Column('id', Integer, primary_key=True)
    name = Column(String(191), nullable=False)
    value = Column(String(191), nullable=False)
    description = Column(Text(length=200))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)