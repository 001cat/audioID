# from config import get_config
import sqlite3
from termcolor import colored
from itertools import zip_longest

class SqliteDatabase():
    TABLE_SONGS = 'songs'
    TABLE_FINGERPRINTS = 'fingerprints'

    def __init__(self,dbPath):
        self.connect(dbPath)

    def connect(self,dbPath):
        self.conn = sqlite3.connect(dbPath)
        self.conn.text_factory = str

        self.cur = self.conn.cursor()

        print(colored('sqlite - connection opened','white',attrs=['dark']))

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        print(colored('sqlite - connection has been closed','white',attrs=['dark']))

    def query(self, query, values = []):
        self.cur.execute(query, values)

    def reset(self):
        #
        # songs table

        self.query("DROP TABLE IF EXISTS songs;")
        print('removed db.songs');

        self.query("""
            CREATE TABLE songs (
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT,
            filehash  TEXT
            );
        """)
        print('created db.songs');

        #
        # fingerprints table

        self.query("DROP TABLE IF EXISTS fingerprints;")
        print('removed db.fingerprints');

        self.query("""
            CREATE TABLE `fingerprints` (
            `id`  INTEGER PRIMARY KEY AUTOINCREMENT,
            `song_fk` INTEGER,
            `hash`  TEXT,
            `offset`  INTEGER
            );
        """)
        print('created db.fingerprints');

        print('done');




    def executeOne(self, query, values = []):
        self.cur.execute(query, values)
        return self.cur.fetchone()

    def executeAll(self, query, values = []):
        self.cur.execute(query, values)
        return self.cur.fetchall()

    def buildSelectQuery(self, table, params):
        conditions = []
        values = []

        for k, v in enumerate(params):
            key = v
            value = params[v]
            conditions.append("%s = ?" % key)
            values.append(value)

        conditions = ' AND '.join(conditions)
        query = "SELECT * FROM %s WHERE %s" % (table, conditions)

        return {
        "query": query,
        "values": values
        }

    def findOne(self, table, params):
        select = self.buildSelectQuery(table, params)
        return self.executeOne(select['query'], select['values'])

    def findAll(self, table, params):
        select = self.buildSelectQuery(table, params)
        return self.executeAll(select['query'], select['values'])

    def insert(self, table, params):
        keys = ', '.join(params.keys())
        values = list(params.values())

        query = "INSERT INTO songs (%s) VALUES (?, ?)" % (keys);

        print(values)

        self.cur.execute(query, values)
        self.conn.commit()

        return self.cur.lastrowid

    def insertMany(self, table, columns, values):
        def grouper(iterable, n, fillvalue=None):
            args = [iter(iterable)] * n
            return (filter(None, values) for values
                in zip_longest(fillvalue=fillvalue, *args))

        for split_values in grouper(values, 1000):
            # print(list(split_values)) # debug Ayu
            # raise ValueError('debug')
            query = "INSERT OR IGNORE INTO %s (%s) VALUES (?, ?, ?)" % (table, ", ".join(columns))
            self.cur.executemany(query, split_values)

        self.conn.commit()


    def get_song_hashes_count(self, song_id):
        query = 'SELECT count(*) FROM %s WHERE song_fk = %d' % (self.TABLE_FINGERPRINTS, song_id)
        rows = self.executeOne(query)
        return int(rows[0])

    def get_song_by_filehash(self, filehash):
        return self.findOne(self.TABLE_SONGS, {
        "filehash": filehash
        })

    def get_song_by_id(self, id):
        return self.findOne(self.TABLE_SONGS, {
        "id": id
        })

    def add_song(self, filename, filehash):
        song = self.get_song_by_filehash(filehash)

        if not song:
            song_id = self.insert(self.TABLE_SONGS, {
                "name": filename,
                "filehash": filehash
            })
        else:
            song_id = song[0]

        return song_id

    def store_fingerprints(self, values):
        # print(f"{values} # debug Ayu")
        self.insertMany(self.TABLE_FINGERPRINTS,
        ['song_fk', 'hash', 'offset'], values
        )
    def match_fingerprints(self,split_values):
        # @todo move to db related files
        query = """
            SELECT hash, song_fk, offset
            FROM fingerprints
            WHERE hash IN (%s)
        """
        # split_values = [s.upper() for s in split_values]
        query = query % ', '.join('?' * len(split_values))
        x = self.executeAll(query, split_values)


        # query = """
        #     SELECT hash, song_fk, offset
        #     FROM fingerprints
        #     """                                 #debug Ayu
        # print(split_values)
        # y = self.executeAll(query)
        # print(y)


        return x

    # database summary
    def printSummary(self):
        row = self.executeOne("""
        SELECT
            (SELECT COUNT(*) FROM songs) as songs_count,
            (SELECT COUNT(*) FROM fingerprints) as fingerprints_count
        """)

        msg = ' * %s: %s (%s)' % (
        colored('total', 'yellow'),             # total
        colored('%d song(s)', 'yellow'),        # songs
        colored('%d fingerprint(s)', 'yellow')  # fingerprints
        )
        print(msg % row)

        return row[0] # total

    # get songs with details
    def printSongs(self):
        rows = self.executeAll("""
        SELECT
            s.id,
            s.name,
            (SELECT count(f.id) FROM fingerprints AS f WHERE f.song_fk = s.id) AS fingerprints_count
        FROM songs AS s
        ORDER BY fingerprints_count DESC
        """)

        for row in rows:
            msg = '   ** %s %s: %s' % (
                colored('id=%s','white',attrs=['dark']), # id
                colored('%s', 'white', attrs=['bold']),   # name
                colored('%d hashes', 'green')             # hashes
            )
            print(msg % row)
        
        songs = {}
        songs['id'] = [row[0] for row in rows]
        songs['filename'] = [row[1] for row in rows]
        songs['hashes'] = [row[2] for row in rows]
        return songs

    # find duplicates
    def printDuplicates(self):
        rows = self.executeAll("""
        SELECT a.song_fk, s.name, SUM(a.cnt)
        FROM (
            SELECT song_fk, COUNT(*) cnt
            FROM fingerprints
            GROUP BY hash, song_fk, offset
            HAVING cnt > 1
            ORDER BY cnt ASC
        ) a
        JOIN songs s ON s.id = a.song_fk
        GROUP BY a.song_fk
        """)

        msg = ' * duplications: %s' % colored('%d song(s)', 'yellow')
        print(msg % len(rows))

        for row in rows:
            msg = '   ** %s %s: %s' % (
                colored('id=%s','white',attrs=['dark']),
                colored('%s', 'white', attrs=['bold']),
                colored('%d duplicate(s)', 'red')
            )
            print(msg % row)

    # find colissions
    def printColissions(self):
        rows = self.executeAll("""
        SELECT sum(a.n) FROM (
            SELECT
            hash,
            count(distinct song_fk) AS n
            FROM fingerprints
            GROUP BY `hash`
            ORDER BY n DESC
        ) a
        """)

        msg = ' * colissions: %s' % colored('%d hash(es)', 'red')
        val = 0
        if rows[0][0] is not None:
            val = rows[0]

        print(msg % val)

