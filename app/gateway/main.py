from fastapi import FastAPI
from pydantic import BaseModel
import pika, json, uuid

app = FastAPI(title="Mini Greenlight Engine")

def publish_job(job_id: str, payload: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="scan_jobs")
    channel.basic_publish(
        exchange="", routing_key="scan_jobs",
        body=json.dumps({"job_id": job_id, **payload})
    )
    connection.close()
class ScanRequest(BaseModel):
    vendor_name: str
    cloud_state: dict

@app.post("/scan")
def submit_scan(req: ScanRequest):
    job_id = str(uuid.uuid4())
    # Pour l'instant : écrit direct un fichier "job" (le RabbitMQ arrive à l'étape suivante)
    # with open(f"results/{job_id}.json", "w") as f:
        #json.dump(req.model_dump(), f)
    publish_job(job_id, req.model_dump())
    return {"job_id": job_id, "status": "queued"}

@app.get("/health")
def health():
    return {"status": "ok"}