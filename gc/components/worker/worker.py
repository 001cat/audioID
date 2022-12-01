import os,sys,time,platform
import json,pika
import audioID.core

cassandraHost = os.getenv("CASSANDRA_HOST") or "host.docker.internal"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "host.docker.internal"

def toLogs(message,key='info'):
    key = f"{platform.node()}.worker.{key}"
    print("DEBUG:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(exchange='logs', routing_key=key, body=message)
def toRest(data,key):
    rabbitMQChannel.basic_publish(exchange='rest', routing_key=key, body=json.dumps(data))
    


def callback(ch, method, properties, body):
    data = json.loads(body.decode())
    print(data)
    
    if data['cmd'] == 'addNewSong':
        toLogs(f"Request received, adding {data['path']}")
        msg = audioID.core.addAudio2DB(data['path'])
        toLogs(msg)
        toRest({'msg':msg},data['taskID'])
        os.system(f"""rm "{data['path']}" """)
    elif data['cmd'] == 'recogFile':
        toLogs(f"Request received, recognizing {data['path']}")
        recogResult = audioID.core.recognize_file(data['path'])
        toLogs(recogResult.pop('msg'))
        toRest(recogResult,data['taskID'])
        os.system(f"""rm "{data['path']}" """)
    elif data['cmd'] == 'checkDB':
        songs,msgs = audioID.core.printSongs()
        toLogs(msgs)
        # toRest({'msg':msg,'songs':songs},songs['taskID'])
    elif data['cmd'] == 'reset':
        msgs = audioID.core.reset_dataBase()
        toLogs(msgs)
    else:
        raise ValueError('Unknown command type')
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    sys.stdout.flush()
    sys.stderr.flush()



timeStamp = time.time()
while time.time()-timeStamp < 60:
    try:
        db = audioID.core.initDB()
        try:
            db.query('SELECT * FROM songs')
        except:
            audioID.core.reset_dataBase()

        rabbitMQ = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
        rabbitMQChannel = rabbitMQ.channel()
        rabbitMQChannel.queue_declare(queue='toWorker')
        # rabbitMQChannel.queue_declare(queue='toLog')
        rabbitMQChannel.exchange_declare(exchange='rest',exchange_type='topic')
        rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
        rabbitMQChannel.basic_qos(prefetch_count=1)
        rabbitMQChannel.basic_consume(queue='toWorker', on_message_callback=callback)
        rabbitMQChannel.start_consuming()
    except:
        pass




# import audioID.core
# audioID.core.reset_dataBase()
# db = audioID.core.initDB()

# from audioID.libs.reader import FileReader
# reader = FileReader('/srv/uploads/Lyn - Life Will Change.mp3')
# audio = reader.parse_audio()

# # db.get_song_by_filehash(audio['file_hash'])
# placeholders = ' AND '.join([f'{k}=%s' for k in {"filehash": audio['file_hash']}.keys()])
# params = {"filehash": audio['file_hash']}.values()
# query = f'SELECT * FROM songs WHERE {placeholders} limit 10000'
# db.session.execute(query,params)

# audioID.core.addAudio2DB('/srv/uploads/Lyn - Life Will Change.mp3')