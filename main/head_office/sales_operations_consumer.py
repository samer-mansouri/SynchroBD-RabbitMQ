import pika
import json

def callback(ch, method, properties, body):
    print(f" [x] Received '{method.routing_key}':'{body.decode()}")
    ##parse the json string and get the branch office and data from the body
    json_body = json.loads(body.decode())
    branch_office = json_body['branch_office']
    data = json_body['data']
    print(f"Branch Office: {branch_office}")
    print(f"Data: {data}")

def consume_messages():
    # Parameters for RabbitMQ connection (adjusted for Docker)
    rabbitmq_host = 'localhost'  # Use the service name as the host
    exchange_name = 'sales_actions'
    exchange_type = 'topic'
    queue_name = 'sales_queue'

    # Establish a connection to RabbitMQ
    credentials = pika.PlainCredentials('user', 'password') 
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials))
    channel = connection.channel()

    # Declare a topic exchange
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)

    # Declare a queue and bind it to the exchange with a routing key pattern
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='sales.#')

    # Set up a consumer callback
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit, press CTRL+C')
    channel.start_consuming()

# Example usage
if __name__ == "__main__":
    consume_messages()
