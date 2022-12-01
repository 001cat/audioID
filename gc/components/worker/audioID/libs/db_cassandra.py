
import tqdm
from datetime import datetime
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement
from termcolor import colored
from itertools import zip_longest


class CassandraDatabase():
    # TABLE_SONGS = 'songs'
    # TABLE_FINGERPRINTS = 'fingerprints'

    def __init__(self,dbPath):
        self.connect(dbPath)

    def connect(self,dbPath):
        self.cluster = Cluster(dbPath,port=9042)
        self.session = self.cluster.connect()
        self.session.execute("""
        CREATE KEYSPACE IF NOT EXISTS audioid
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 1}
        """)
        self.session.set_keyspace('audioid')

        print(colored('cassandra - connection opened','white',attrs=['dark']))

    def __del__(self):
        self.cluster.shutdown()
        print(colored('cassandra - connection has been closed','white',attrs=['dark']))

    def query(self, query, values=None):
        return self.session.execute(query,values)

    def reset(self):
        # songs table
        self.query("DROP TABLE IF EXISTS songs;")
        print('removed table songs')

        self.query(f""" CREATE TABLE songs (
                    id  timestamp,
                    name  TEXT,
                    filehash  TEXT,
                    PRIMARY KEY (id)
                    )""")
        self.query("""CREATE INDEX filehashIndex on songs(filehash)""")
        self.query("""CREATE INDEX nameIndex on songs(name)""")
        print('created table songs')

        # fingerprints table
        self.query("DROP TABLE IF EXISTS fingerprints;")
        print('removed table fingerprints')

        self.query(""" CREATE TABLE fingerprints (
                    song_fk timestamp,
                    hash  text,
                    offset  int,
                    PRIMARY KEY (song_fk,hash)
                    )""")
        # self.query("""CREATE INDEX song_fkIndex on fingerprints(song_fk)""")
        # self.query("""CREATE INDEX hashIndex on fingerprints(hash)""")
        print('created table fingerprints')

        # recogs table
        self.query("DROP TABLE IF EXISTS recogs;")
        print('removed table recogs')
        self.query(""" CREATE TABLE recogs (
            id timestamp,
            upload text,
            match  text,
            confidence  int,
            PRIMARY KEY (id)
            )""")

        print('done')


    def insert(self,table,keyValues,ignore=False):
        cols = ','.join(keyValues.keys())
        placeholders = ','.join(['%s']*len(keyValues))
        params = keyValues.values()
        query = f'INSERT INTO {table} ({cols}) VALUES ({placeholders})'
        self.query(query,params).all()

    def insertBulk(self, table, keyValues):
        cols = ','.join(keyValues.keys())
        placeholders = ','.join(['?']*len(keyValues))
        insert_user = self.session.prepare(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})")
        for i,values in enumerate(zip(*(keyValues.values()))):
            if i % 50000 == 0:
                batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
            batch.add(insert_user, values)
            if (i+1) % 50000 == 0:
                self.session.execute(batch)
        if (i+1) % 50000 != 0:
            self.session.execute(batch)

    def find(self, table, keyValues,limit=10000):
        placeholders = ' AND '.join([f'{k}=%s' for k in keyValues.keys()])
        params = keyValues.values()
        query = f'SELECT * FROM {table} WHERE {placeholders} limit {limit}'
        return self.query(query,params)


    def add_song(self, filename, filehash):
        song = self.get_song_by_filehash(filehash)
        if not song:
            song_id = datetime.utcnow()
            self.insert('songs', {
                'id': song_id,
                "name": filename,
                "filehash": filehash
            })
        else:
            song_id = song[0].id
        return song_id

    def store_fingerprints(self, values):
        # for value in tqdm.tqdm(values):
        #     self.insert('fingerprints',{'song_fk':value[0],
        #         'hash':value[1],'offset':value[2]})#'id':datetime.utcnow().isoformat(),
        keyValues = {'song_fk':[],'hash':[],'offset':[]}
        for value in values:
            keyValues['song_fk'].append(value[0])
            keyValues['hash'].append(value[1])
            keyValues['offset'].append(value[2])
        self.insertBulk('fingerprints',keyValues)
                                        
    def get_song_hashes_count(self, song_id):
        query = 'SELECT count(*) FROM fingerprints WHERE song_fk = %s'
        rows = self.query(query,[song_id])
        return int(rows[0].count)
    def get_song_by_id(self, id):
        rows = self.find('songs', {"id": id},limit=1).all()
        try:
            return rows[0]
        except IndexError:
            return rows
    def get_song_by_filehash(self, filehash):
        return self.find('songs', {"filehash": filehash},limit=1).all()

    def match_fingerprints(self,split_values):
        split_values = [v.lower() for v in split_values]
        placeholders = ','.join(['%s']*len(split_values))
        query = f"SELECT hash, song_fk, offset FROM fingerprints \
                  WHERE song_fk > '2000-01-01 00:00:00' AND hash IN ({placeholders}) ALLOW FILTERING " 
        # for r in self.query(query,split_values):
        #     print(f"DEBUG {r}")
        # for v in split_values[:10]:
        #     print(v)
        return self.query(query,split_values).all()

        # @todo move to db related files
        # query = """
        #     SELECT upper(hash), song_fk, offset
        #     FROM fingerprints
        #     WHERE upper(hash) IN (%s)
        # """
        # query = query % ', '.join('?' * len(split_values))

        # x = self.executeAll(query, split_values)
        # return x

    def saveRecog(self,fileUpload,fileMatch,confidence):
        self.insert('recogs',{'id':datetime.utcnow(),'upload':fileUpload,
                              'match':fileMatch,'confidence':confidence})



    # database summary
    def printSummary(self):
        song_count = self.query('SELECT COUNT(*) FROM songs').all()[0].count
        fingerprint_count = self.query('SELECT COUNT(*) FROM fingerprints').all()[0].count
        
        msg = ' * %s: %s (%s)' % (
        colored('total', 'yellow'),             # total
        colored('%d song(s)', 'yellow'),        # songs
        colored('%d fingerprint(s)', 'yellow')  # fingerprints
        )
        print(msg % (song_count,fingerprint_count))

        return (song_count,fingerprint_count) # total

    # get songs with details
    def printSongs(self):
        rows,msgs = [],[]
        for song in self.query('SELECT * FROM songs'):
            fp = self.query(f"SELECT COUNT(*) FROM fingerprints WHERE song_fk='{song.id}'")
            rows.append((song.id,song.name,fp.all()[0].count))

        for row in rows:
            msg = '   ** %s %s: %s' % (
                colored(f'id={row[0]}','white',attrs=['dark']), # id
                colored(f'{row[1]}', 'white', attrs=['bold']),   # name
                colored(f'{row[2]} hashes', 'green')             # hashes
            )
            print(msg)
        
        songs = {}
        songs['id'] = [row[0] for row in rows]
        songs['filename'] = [row[1] for row in rows]
        songs['hashes'] = [row[2] for row in rows]
        return songs,msgs


if __name__ == '__main__':
    db = CassandraDatabase(['localhost'])
    # db.__del__()
    db.reset()
    from datetime import datetime
    
    db.session.execute(f""" 
        INSERT INTO songs (id,name,filehash) VALUES ('{datetime.utcnow().isoformat()}', 'test1', 'test1')
        """,)
    params = (datetime.utcnow().isoformat(),'test2','test2')
    db.session.execute('INSERT INTO songs (id,name,filehash) VALUES (%s,%s,%s)',params)
    db.insert('songs',{'id':datetime.utcnow().isoformat(),
                       'name':'test2',
                       'filehash':'test2'})
    
    print(db.find('songs',{'filehash':'test2'}).all()[0])
    row = db.find('songs',{'filehash':'test2'}).all()[0]