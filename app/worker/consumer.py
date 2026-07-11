import pika, json
from app.rules.engine import run_engine
from dotenv import load_dotenv
from app.reports.docx_report import generate_docx_report

import os

def callback(ch, method, properties, body):
    job = json.loads(body)
    print(f"Processing job {job['job_id']}")
    report = run_engine(job["cloud_state"])
    with open(f"results/{job['job_id']}_report.json", "w") as f:
        json.dump(report, f, indent=2)
        generate_docx_report(report, f"results/{job['job_id']}_report.docx", job.get("vendor_name", "Test Vendor"))

    print(f"Job {job['job_id']} done: {report['summary']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

load_dotenv()


def main():

    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER"),
        os.getenv("RABBITMQ_PASSWORD")
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=5672,
            credentials=credentials
        )
    )

    channel = connection.channel()

    channel.queue_declare(queue="scan_jobs")

    channel.basic_consume(
        queue="scan_jobs",
        on_message_callback=callback
    )

    print("Worker waiting for jobs...")
    channel.start_consuming()

if __name__ == "__main__":
    main()