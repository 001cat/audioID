import requests,os
import sys,base64,json


if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <server ip> <cmd> ...")
    print(f"where <cmd> is one of add, rawImage, sum or jsonImage")
    print(f"and <reps> is the integer number of repititions for measurement")

host = sys.argv[1]
cmd = sys.argv[2]

addr = f"http://{host}"

print(f"Sending request...")

def requestAddNewSong(addr, filepath, debug=False):
    with open(filepath, "rb") as mp3:
        jsonSong = {'mp3':base64.b64encode(mp3.read()).decode(),'filename':os.path.basename(filepath)}
    headers = {'content-type': 'application/json'}
    jsonSong_url = addr + "/api/addNewSong"
    response = requests.post(jsonSong_url, json=jsonSong, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(response.text)
        # print(json.loads(response.text))
    pass
def requestRecogFile(addr, filepath, debug=False):
    with open(filepath, "rb") as mp3:
        jsonSong = {'mp3':base64.b64encode(mp3.read()).decode(),'filename':os.path.basename(filepath)}
    headers = {'content-type': 'application/json'}
    recogFile_url = addr + "/api/recogFile"
    response = requests.post(recogFile_url, json=jsonSong, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(response.text)
        # print(json.loads(response.text))
    pass
def checkDB(addr,debug=False):
    headers = {'content-type': 'application/json'}
    checkDB_url = addr + "/api/checkDB"
    response = requests.post(checkDB_url, json={}, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(response.text)
        # print(json.loads(response.text))
    pass
def resetDB(addr,debug=False):
    headers = {'content-type': 'application/json'}
    resetDB_url = addr + "/api/RESET"
    response = requests.post(resetDB_url, json={}, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(response.text)
        # print(json.loads(response.text))
    pass
if cmd == 'add':
    requestAddNewSong(addr,sys.argv[3],debug=True)
elif cmd == 'recog':
    requestRecogFile(addr,sys.argv[3],debug=True)
elif cmd == 'reset':
    resetDB(addr,debug=True)
elif cmd == 'check':
    checkDB(addr,debug=True)
else:
    print("Unknown option", cmd)
