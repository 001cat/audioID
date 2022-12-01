import requests,os,glob
import sys,base64,json
import pandas as pd

class ShazamInit():
    def __init__(self,addr):
        self.addr = addr
    def requestAddNewSong(self, filepath, debug=False, wait4feedback=False):
        with open(filepath, "rb") as mp3:
            jsonSong = {'mp3':base64.b64encode(mp3.read()).decode(),'filename':os.path.basename(filepath)}
        headers = {'content-type': 'application/json'}
        if wait4feedback:
            jsonSong_url = self.addr + "/api/addNewSong"
        else:
            jsonSong_url = self.addr + "/api/addNewSongNoback"
        response = requests.post(jsonSong_url, json=jsonSong, headers=headers)
        if debug:
            # decode response
            print("Response is", response)
            print(response.text)
            # print(json.loads(response.text))
        pass
    def requestRecogFile(self, filepath, debug=False):
        with open(filepath, "rb") as mp3:
            jsonSong = {'mp3':base64.b64encode(mp3.read()).decode(),'filename':os.path.basename(filepath)}
        headers = {'content-type': 'application/json'}
        recogFile_url = self.addr + "/api/recogFile"
        response = requests.post(recogFile_url, json=jsonSong, headers=headers)
        if debug:
            # decode response
            print("Response is", response)
            print(response.text)
            # print(json.loads(response.text))
        pass
    
    def checkSongs(self,debug=False):
        headers = {'content-type': 'application/json'}
        checkDB_url = self.addr + "/songs"
        response = requests.get(checkDB_url, json={}, headers=headers)
        if debug:
            print("Response is", response)
        try:
            df = pd.read_html(response.text)
            return df
        except ValueError as e:
            print(e)
            return None
    def checkRecogs(self,debug=False):
        headers = {'content-type': 'application/json'}
        checkDB_url = self.addr + "/recogs"
        response = requests.get(checkDB_url, json={}, headers=headers)
        if debug:
            print("Response is", response)
        try:
            df = pd.read_html(response.text)
            return df
        except ValueError as e:
            print(e)
            return None
    def resetDB(self,debug=False):
        headers = {'content-type': 'application/json'}
        resetDB_url = self.addr + "/api/RESET"
        response = requests.post(resetDB_url, json={}, headers=headers)
        if debug:
            # decode response
            print("Response is", response)
            print(response.text)
            # print(json.loads(response.text))
        pass

if __name__ == '__main__':
    shazam = ShazamInit('http://localhost')

    # for f in glob.glob('../../mp3Raw/*.mp3'):
    #     print(f)
    #     shazam.requestAddNewSong(f,debug=False)

    print(shazam.checkSongs())
    print(shazam.checkRecogs())

    # shazam.requestRecogFile('../../mp3Raw/Anna F - Too Far.mp3',debug=True)
    # shazam.requestRecogFile('../../mp3Test/Lady A - Need You Now (iTunes Session) (mp3cut.net).mp3',debug=True)
    # shazam.requestRecogFile('../../mp3Test/Recording-1.m4a',debug=True)



    # shazam.resetDB(debug=True)


