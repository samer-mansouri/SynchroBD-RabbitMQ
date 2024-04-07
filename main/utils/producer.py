import pika
import os 

class RabbitMQProducer :
    
    def __init__(self) -> None:
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST')
        self.rabbitmq_user = os.getenv('RABBITMQ_USER')
        self.rabbitmq_password = os.getenv('RABBITMQ_PASSWORD')
        self.exchange_name = os.getenv('RABBITMQ_EXCHANGE')
        self.exchange_type = os.getenv('RABBITMQ_EXCHANGE_TYPE')

    def publish_message(self, action, message):
        
        print(f" [x] Publishing message: {message}")

        credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rabbitmq_host, credentials=credentials))
        channel = connection.channel()

        channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

        routing_key = f"sales.{action}"
        channel.basic_publish(exchange=self.exchange_name, routing_key=routing_key, body=message)

        print(f" [x] Sent '{routing_key}':'{message}'")

        connection.close()
