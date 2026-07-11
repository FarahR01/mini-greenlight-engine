from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from app.db.database import Base

class ScanResult(Base):
    __tablename__ = "scan_results"

    job_id = Column(String, primary_key=True)
    vendor_name = Column(String, nullable=False)
    cloud_provider = Column(String, nullable=True)
    risk_score = Column(Float, nullable=False)
    total_checks = Column(Integer, nullable=False)
    passed_checks = Column(Integer, nullable=False)
    failed_checks = Column(Integer, nullable=False)
    results_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))