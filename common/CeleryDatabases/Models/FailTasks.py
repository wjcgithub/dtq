from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Text

Base = declarative_base()

class FailTasks(Base):
    __tablename__ = 'fail_tasks'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(45), nullable=False)
    queue = Column(String(45), nullable=False)
    type = Column(Integer)
    taskname = Column(String(45), nullable=False)
    taskid = Column(String(50), nullable=False)
    payload = Column(String(500), nullable=False)
    exception = Column(String(100), nullable=False)
    trace = Column(Text)
    stime = Column(DateTime, nullable=False)
    ctime = Column(DateTime, nullable=False)
