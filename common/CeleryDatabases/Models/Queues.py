from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,String, Integer, Text, DateTime

Base = declarative_base()
class Queues(Base):
    __tablename__ = 'queues'

    id = Column('id', Integer, primary_key=True)
    gid = Column(Integer)
    masterid = Column(Integer)
    name = Column(String(45), nullable=False)
    concurrency = Column(Integer)
    timeout = Column(Integer)
    executor = Column(String(45))
    tasks_number = Column(Integer)
    memory = Column(Integer)
    desc = Column(Text(length=200))
    lastmasterid = Column(Integer)
    status = Column(String(1))
    lasttime = Column(DateTime)
    ctime = Column(DateTime)