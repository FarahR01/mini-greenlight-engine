import os
import pika
from dotenv import load_dotenv

load_dotenv()


def get_rabbitmq_connection():
    """Uses CLOUDAMQP_URL in production (Northflank), falls back to local
    guest/guest-style credentials for local development."""
    cloudamqp_url = os.getenv("CLOUDAMQP_URL")
    if cloudamqp_url:
        params = pika.URLParameters(cloudamqp_url)
        return pika.BlockingConnection(params)

    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    host = os.getenv("RABBITMQ_HOST", "localhost")
    credentials = pika.PlainCredentials(user, password)
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=host, credentials=credentials)
    )