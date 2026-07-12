import pika
import os

def get_rabbitmq_connection():
    cloudamqp_url = os.getenv("CLOUDAMQP_URL")
    if cloudamqp_url:
        params = pika.URLParameters(cloudamqp_url)
        return pika.BlockingConnection(params)

    # fallback local dev (inchangé)
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    host = os.getenv("RABBITMQ_HOST", "localhost")
    credentials = pika.PlainCredentials(user, password)
    return pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials))