from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import pika
import json
import uuid
import os
from dotenv import load_dotenv
from app.reports.drift import compute_drift
load_dotenv()
from app.gateway.auth import verify_api_key
from fastapi.responses import HTMLResponse
# Database imports
from app.db.database import SessionLocal
from app.db.models import ScanResult as ScanResultModel
from app.gateway.dashboard_template import DASHBOARD_HTML

app = FastAPI(title="Mini Greenlight Engine")


def get_rabbitmq_connection():

    user = os.getenv(
        "RABBITMQ_USER",
        "guest"
    )

    password = os.getenv(
        "RABBITMQ_PASSWORD",
        "guest"
    )

    host = os.getenv(
        "RABBITMQ_HOST",
        "localhost"
    )

    credentials = pika.PlainCredentials(
        user,
        password
    )

    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            credentials=credentials
        )
    )


def publish_job(job_id: str, payload: dict):

    connection = get_rabbitmq_connection()

    channel = connection.channel()

    channel.queue_declare(
        queue="scan_jobs"
    )

    channel.basic_publish(
        exchange="",
        routing_key="scan_jobs",
        body=json.dumps({
            "job_id": job_id,
            **payload
        })
    )

    connection.close()

class ScanRequest(BaseModel):
    vendor_name: str
    cloud_state: dict


@app.post("/scan", dependencies=[Depends(verify_api_key)])
def submit_scan(req: ScanRequest):

    job_id = str(uuid.uuid4())

    publish_job(
        job_id,
        req.model_dump()
    )

    return {
        "job_id": job_id,
        "status": "queued"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# ======================================================
# Scan consultation endpoints
# ======================================================


@app.get(
    "/scans",
    dependencies=[Depends(verify_api_key)]
)
def list_scans(vendor_name: str | None = None):

    db = SessionLocal()

    try:
        query = db.query(ScanResultModel)

        if vendor_name:
            query = query.filter(
                ScanResultModel.vendor_name == vendor_name
            )

        records = (
            query
            .order_by(
                ScanResultModel.created_at.desc()
            )
            .all()
        )

        return [
            {
                "job_id": r.job_id,
                "vendor_name": r.vendor_name,
                "risk_score": r.risk_score,
                "created_at": r.created_at.isoformat()
            }
            for r in records
        ]

    finally:
        db.close()



@app.get(
    "/scans/{job_id}",
    dependencies=[Depends(verify_api_key)]
)
def get_scan(job_id: str):

    db = SessionLocal()

    try:
        record = (
            db.query(ScanResultModel)
            .filter(
                ScanResultModel.job_id == job_id
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=404,
                detail="Scan not found"
            )

        return {
            "job_id": record.job_id,
            "vendor_name": record.vendor_name,
            "risk_score": record.risk_score,
            "results": record.results_json,
            "created_at": record.created_at.isoformat()
        }

    finally:
        db.close()

@app.get("/scans/drift", dependencies=[Depends(verify_api_key)])
def get_drift(from_job: str, to_job: str):

    db = SessionLocal()
    try:
        old = db.query(ScanResultModel).filter(ScanResultModel.job_id == from_job).first()
        new = db.query(ScanResultModel).filter(ScanResultModel.job_id == to_job).first()
        if not old or not new:
            raise HTTPException(status_code=404, detail="One or both scans not found")
        return compute_drift(old.results_json, new.results_json)
    finally:
        db.close()

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_HTML