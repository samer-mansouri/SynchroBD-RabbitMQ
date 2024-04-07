import pika
import threading
import json
import os

class RabbitMQConsumer:
    def __init__(self, message_callback):
        self.config = {
            'user': os.getenv('RABBITMQ_USER'),
            'password': os.getenv('RABBITMQ_PASSWORD'),
            'host': os.getenv('RABBITMQ_HOST'),
            'exchange': os.getenv('RABBITMQ_EXCHANGE'),
            'exchange_type': os.getenv('RABBITMQ_EXCHANGE_TYPE')
        }
        self.message_callback = message_callback
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.config['host'],
                credentials=pika.PlainCredentials(self.config['user'], self.config['password'])
            )
        )
        channel = connection.channel()
        channel.exchange_declare(exchange=self.config['exchange'], exchange_type=self.config['exchange_type'], durable=True)
        result = channel.queue_declare('persistant_queue', durable=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=self.config['exchange'], queue=queue_name, routing_key='sales.#')
        channel.basic_consume(queue=queue_name, on_message_callback=self.on_message, auto_ack=False)
        channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        action = method.routing_key.split('.')[1]
        message = json.loads(body)
        self.message_callback(action, message)
        ch.basic_ack(delivery_tag=method.delivery_tag)