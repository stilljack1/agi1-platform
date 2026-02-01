import os
import time
from sqlalchemy import create_engine, Column, String, Float, Integer, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# In Cloud Shell, we can use a local SQLite for testing, 
# but the code is PostgreSQL-ready.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agi1_persistence.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class TaskEvent(Base):
    __tablename__ = "task_events"
    id = Column(Integer, primary_key=True)
    role = Column(String)
    task_input = Column(String)
    status = Column(String)  # PASS, FAIL, IMPROVE
    kpi_score = Column(Float)
    latency = Column(Float)
    arbitration_winner = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
