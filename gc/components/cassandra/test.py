from cassandra.cluster import Cluster

cluster = Cluster(['localhost'],port=9042)
session = cluster.connect()

session.execute("""
        CREATE KEYSPACE test 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 1}
        """)

session.set_keyspace('test')
session.execute('DROP TABLE IF EXISTS songs')

session.execute("""
    CREATE TABLE songs (
    id  int,
    name  TEXT,
    filehash  TEXT,
    PRIMARY KEY (id)
    )
""")