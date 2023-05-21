import logging
import pika
from app.commons.config import settings
from app.commons.enums import MessageQueues
from app import evaluation_handler


def callback(ch, method, properties, body):
    logging.info(f"Received message: {body}")
    id = body.decode("utf-8")
    evaluation_handler.evaluate(id)


def start_consuming():
    try:
        rabbitmq_credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER,
            settings.RABBITMQ_PASSWORD
        )
        connection_params = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=rabbitmq_credentials
            ),
        connection = pika.BlockingConnection(
            connection_params
        )
    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"Error connecting to RabbitMQ: {e}")
        return
    channel = connection.channel()

    channel.queue_declare(queue=MessageQueues.EVALUATION.value)

    channel.basic_consume(
        queue=MessageQueues.EVALUATION.value, on_message_callback=callback, auto_ack=True
    )

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
