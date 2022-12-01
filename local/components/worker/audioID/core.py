import os,json,glob
import numpy as np
from termcolor import colored
from itertools import zip_longest
from audioID.libs.db_sqlite import SqliteDatabase
from audioID.libs.db_cassandra import CassandraDatabase
from audioID.libs.reader import FileReader
from audioID.libs import fingerprint

config = {'db.type':'sqlite','db.path':'fingerprints2.db'}
# config = {'db.type':'sqlite','db.path':'/srv/db/fingerprints2.db'}
# config = {'db.type':'cassandra','db.path':['localhost']}

if os.getenv('CASSANDRA_HOST'):
  config = {'db.type':'cassandra','db.path':[os.getenv('CASSANDRA_HOST')]}

# print(config)

def initDB(config=config):
    if config["db.type"] == "sqlite":
        return SqliteDatabase(config["db.path"])
    elif config["db.type"] == "cassandra":
        return CassandraDatabase(config["db.path"])

def reset_dataBase():
  db = initDB()
  db.reset()
  return 'Database reset completed!'

def printSongs():
  db = initDB()
  return db.printSongs()

def addAudio2DB(filepath):
  filename = os.path.basename(filepath)
  db = initDB()
  # fingerprint all files in a directory
  if filename.endswith((".mp3")):
    reader = FileReader(filepath)
    audio = reader.parse_audio()

    song = db.get_song_by_filehash(audio['file_hash'])
    song_id = db.add_song(filename, audio['file_hash'])

    msg = ' * %s %s: %s' % (
      colored('id=%s', 'white', attrs=['dark']),       # id
      colored('channels=%d', 'white', attrs=['dark']), # channels
      colored('%s', 'white', attrs=['bold'])           # filename
    )
    print(msg % (song_id, len(audio['channels']), filename))

    if song:
      hash_count = db.get_song_hashes_count(song_id)

      if hash_count > 0:
        msg = '   already exists (%d hashes), skip' % hash_count
        print(colored(msg, 'red'))

        return 'Already exists!'

    print(colored('   new song, going to analyze..', 'green'))

    hashes = set()
    channel_amount = len(audio['channels'])

    for channeln, channel in enumerate(audio['channels']):
      msg = '   fingerprinting channel %d/%d'
      print(colored(msg, attrs=['dark']) % (channeln+1, channel_amount))

      channel_hashes = fingerprint.fingerprint(channel, Fs=audio['Fs'])
      channel_hashes = set(channel_hashes)

      msg = '   finished channel %d/%d, got %d hashes'
      print(colored(msg, attrs=['dark']) % (
        channeln+1, channel_amount, len(channel_hashes)
      ))

      hashes |= channel_hashes

    msg = '   finished fingerprinting, got %d unique hashes'

    values = []
    for hash, offset in hashes:
      values.append((song_id, hash, offset))

    msg = '   storing %d hashes in db' % len(values)
    print(colored(msg, 'green'))

    db.store_fingerprints(values)
  return f"Completed! New song {filename} added: id={song_id}, hash={audio['file_hash']}"

def recognize_file(filepath,L=None): # randomly choose L sec segment 
    def grouper(iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return (filter(None, values) for values in zip_longest(fillvalue=fillvalue, *args))
    def find_matches(samples, Fs=fingerprint.DEFAULT_FS):
        hashes = fingerprint.fingerprint(samples, Fs=Fs)
        return return_matches(hashes)
    def return_matches(hashes):
        mapper = {}
        for hash, offset in hashes:
            # print(offset)
            mapper[hash] = offset
        values = mapper.keys()

        for split_values in grouper(values, 1000):
            split_values = list(split_values)
            x = db.match_fingerprints(split_values)
            matches_found = len(x)

            if matches_found > 0:
                msg = '   ** found %d hash matches (step %d/%d)'
                print(colored(msg, 'green') % (
                matches_found,
                len(split_values),
                len(values)
                ))
            else:
                msg = '   ** not matches found (step %d/%d)'
                print(colored(msg, 'red') % (
                len(split_values),
                len(values)
                ))

            for hash, sid, offset in x:
                if config['db.type'] == 'sqlite':
                  offset = int.from_bytes(offset,'little')
                # (sid, db_offset - song_sampled_offset)
                # print(sid, offset, mapper[hash], hashes) # debug Ayu
                yield (sid, offset - mapper[hash])
    def align_matches(matches):
        diff_counter = {}
        largest = 0
        largest_count = 0
        song_id = -1

        for tup in matches:
            sid, diff = tup

            if diff not in diff_counter:
                diff_counter[diff] = {}

            if sid not in diff_counter[diff]:
                diff_counter[diff][sid] = 0

            diff_counter[diff][sid] += 1

            if diff_counter[diff][sid] > largest_count:
                largest = diff
                largest_count = diff_counter[diff][sid]
                song_id = sid

        songM = db.get_song_by_id(song_id)
        print(song_id)
        print(songM)

        nseconds = round(float(largest) / fingerprint.DEFAULT_FS *
                        fingerprint.DEFAULT_WINDOW_SIZE *
                        fingerprint.DEFAULT_OVERLAP_RATIO, 5)

        return {
            "SONG_ID" : song_id,
            "SONG_NAME" : songM.name if config['db.type'] == 'cassandra' else songM[1],
            "CONFIDENCE" : largest_count,
            "OFFSET" : int(largest),
            "OFFSET_SECS" : nseconds
        }

    db = initDB()

    reader = FileReader(filepath)
    audio = reader.parse_audio()

    data = []
    # for c in audio['channels']:
    #     iStart = np.random.randint((len(c)-L*audio['Fs']))
    #     iEnd   = iStart + L*audio['Fs']
    #     data.append(c[iStart:iEnd])
    L = L or min(15,len(audio['channels'][0])//audio['Fs'])
    iStart = np.random.randint((len(audio['channels'][0])-L*audio['Fs']))
    iEnd   = iStart + L*audio['Fs']
    for c in audio['channels']:
        data.append(c[iStart:iEnd])
    # data = audio['channels']
    Fs = audio['Fs']
    channel_amount = len(data)

    result = set()
    matches = []

    for channeln, channel in enumerate(data):
        # TODO: Remove prints or change them into optional logging.
        msg = '   fingerprinting channel %d/%d'
        print(colored(msg, attrs=['dark']) % (channeln+1, channel_amount))

        matches.extend(find_matches(channel,Fs))

        msg = '   finished channel %d/%d, got %d hashes'
        print(colored(msg, attrs=['dark']) % (
        channeln+1, channel_amount, len(matches)
        ))

    total_matches_found = len(matches)

    if total_matches_found > 0:
        try:
            msg = ' ** totally found %d hash matches'
            print(colored(msg, 'green') % total_matches_found)

            song = align_matches(matches)
            song['CONFIDENCE'] //= L*5

            if config['db.type'] == 'cassandra':
                db.saveRecog(os.path.basename(filepath),song['SONG_NAME'],song['CONFIDENCE'])

            msg = ' => song: %s (id=%s)\n'
            msg += '    offset: %d (%d secs)\n'
            msg += '    confidence: %d'

            print(colored(msg, 'green') % (
                song['SONG_NAME'], song['SONG_ID'],
                song['OFFSET'], song['OFFSET_SECS'],
                song['CONFIDENCE']
                ))
        except:
            import sys
            sys.stdout.flush()
            sys.stderr.flush()
            return {'msg':'Something Wrong!', 'found':'Unclear'}

    if song['CONFIDENCE'] >= 1:
        return {'msg':msg % (
                song['SONG_NAME'], song['SONG_ID'],
                song['OFFSET'], song['OFFSET_SECS'],
                song['CONFIDENCE']), 'found':'True','song':song['SONG_NAME'],
                'confidence': song['CONFIDENCE']}
    else:
        msg = ' ** not matches found at all'
        print(colored(msg, 'red'))
        return {'msg':msg,'found':'False'}

if __name__ == '__main__':
  # reset_dataBase()
  # for mp3file in glob.glob('/Users/ayu/Study/Courses/CSCI5253/TermProject/mp3/*.mp3')[:4]:
  #   addAudio2DB(mp3file)
  # recognize_file('/Users/ayu/Study/Courses/CSCI5253/TermProject/mp3/Eagles - Hotel California.mp3')
  recognize_file('/Users/ayu/Study/Courses/CSCI5253/TermProject/mp3-recording/record-02.mp3')

  # printSongs()





