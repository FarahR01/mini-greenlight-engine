from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.models import ScanResult

def test_scan_result_can_be_persisted():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    record = ScanResult(
        job_id="test-job-1",
        vendor_name="Test Vendor",
        cloud_provider="gcp",
        risk_score=42.5,
        total_checks=10,
        passed_checks=5,
        failed_checks=5,
        results_json={"summary": {"total": 10}},
    )
    db.add(record)
    db.commit()

    fetched = db.query(ScanResult).filter_by(job_id="test-job-1").first()
    assert fetched.vendor_name == "Test Vendor"
    assert fetched.risk_score == 42.5
    db.close()