import os,sys,glob

host = 'localhost'
if len(sys.argv) > 1:
    host = sys.argv[1]

for f in glob.glob('../mp3-recording/*.mp3'):
    os.system(f""" python rest-client.py {host} recog "{f}" """)