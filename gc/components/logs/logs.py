import os,sys,pika,time

def callback(ch, method, properties, body):
    # print(body)
    # print(body.decode())
    # print(body.encode())
    print(f" [x] {method.routing_key}:{body.decode()}", file=sys.stdout, flush=True)
    # sys.stdout.flush()
    # sys.stderr.flush()

rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
print("Using host", rabbitMQHost)

timeStamp = time.time()
while time.time()-timeStamp < 60:
    try:
        rabbitMQ = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
        rabbitMQChannel = rabbitMQ.channel()
        rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
        queue_name = rabbitMQChannel.queue_declare('', exclusive=True).method.queue
        # result = rabbitMQChannel.queue_declare('', exclusive=True)
        # queue_name = result.method.queue

        binding_keys = sys.argv[1:]
        if not binding_keys:
            binding_keys = [ "#"] # Wildcard key will listen to anything

        for key in binding_keys:
            rabbitMQChannel.queue_bind(exchange='logs',queue=queue_name,routing_key=key)

        rabbitMQChannel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        rabbitMQChannel.start_consuming()
    except:
        pass
