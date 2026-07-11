import os
import pika
import json

from dotenv import load_dotenv

from app.rules.engine import run_engine
from app.reports.docx_report import generate_docx_report
from app.db.database import SessionLocal
from app.db.models import ScanResult as ScanResultModel


load_dotenv()


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
            port=5672,
            credentials=credentials
        )
    )


def save_to_db(
    job_id: str,
    vendor_name: str,
    cloud_provider: str,
    report: dict
):

    db = SessionLocal()

    try:
        record = ScanResultModel(
            job_id=job_id,
            vendor_name=vendor_name,
            cloud_provider=cloud_provider,
            risk_score=report["risk_score"],
            total_checks=report["summary"]["total"],
            passed_checks=report["summary"]["passed"],
            failed_checks=report["summary"]["failed"],
            results_json=report,
        )

        db.merge(record)
        db.commit()

    finally:
        db.close()



def callback(ch, method, properties, body):

    job = json.loads(body)

    print(
        f"Processing job {job['job_id']}"
    )

    report = run_engine(
        job["cloud_state"]
    )


    with open(
        f"results/{job['job_id']}_report.json",
        "w"
    ) as f:

        json.dump(
            report,
            f,
            indent=2
        )


    generate_docx_report(
        report,
        f"results/{job['job_id']}_report.docx",
        job.get(
            "vendor_name",
            "Test Vendor"
        )
    )


    save_to_db(
        job_id=job["job_id"],
        vendor_name=job.get(
            "vendor_name",
            "Unknown Vendor"
        ),
        cloud_provider=job.get(
            "cloud_state",
            {}
        ).get(
            "cloud_provider",
            "unknown"
        ),
        report=report,
    )


    print(
        f"Job {job['job_id']} done: {report['summary']}"
    )


    ch.basic_ack(
        delivery_tag=method.delivery_tag
    )



def main():

    connection = get_rabbitmq_connection()

    channel = connection.channel()

    channel.queue_declare(
        queue="scan_jobs"
    )

    channel.basic_consume(
        queue="scan_jobs",
        on_message_callback=callback
    )


    print(
        "Worker waiting for jobs..."
    )

    channel.start_consuming()



if __name__ == "__main__":
    main()