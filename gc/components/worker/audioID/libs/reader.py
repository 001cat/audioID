import os
import numpy as np
from hashlib import sha1
from pydub import AudioSegment
from pydub.utils import audioop

class FileReader():
  """
    Reads any file supported by pydub (ffmpeg) and returns the data contained
    within. If file reading fails due to input being a 24-bit wav file,
    wavio is used as a backup.

    Can be optionally limited to a certain amount of seconds from the start
    of the file by specifying the `limit` parameter. This is the amount of
    seconds from the start of the file.

    returns: (channels, samplerate)
    """
  def __init__(self, filename):
    # super(FileReader, self).__init__(a)
    self.filename = filename

  # pydub does not support 24-bit wav files, use wavio when this occurs
  def parse_audio(self):
    limit = None
    # limit = 10

    songname, extension = os.path.splitext(os.path.basename(self.filename))

    try:
      audiofile = AudioSegment.from_file(self.filename)

      if limit:
        audiofile = audiofile[:limit * 1000]

      data = np.fromstring(audiofile._data, np.int16)

      channels = []
      for chn in range(audiofile.channels):
        channels.append(data[chn::audiofile.channels])

      fs = audiofile.frame_rate
    except audioop.error:
      print('audioop.error')
      pass
        # fs, _, audiofile = wavio.readwav(filename)

        # if limit:
        #     audiofile = audiofile[:limit * 1000]

        # audiofile = audiofile.T
        # audiofile = audiofile.astype(np.int16)

        # channels = []
        # for chn in audiofile:
        #     channels.append(chn)

    return {
      "songname": songname,
      "extension": extension,
      "channels": channels,
      "Fs": audiofile.frame_rate,
      "file_hash": self.parse_file_hash()
    }

  def parse_file_hash(self, blocksize=2**20):
    """ Small function to generate a hash to uniquely generate
    a file. Inspired by MD5 version here:
    http://stackoverflow.com/a/1131255/712997

    Works with large files.
    """
    s = sha1()

    with open(self.filename , "rb") as f:
      while True:
        buf = f.read(blocksize)
        if not buf: break
        s.update(buf)

    return s.hexdigest().upper()

# import pyaudio,wave
# class MicrophoneReader():
#   default_chunksize = 8192
#   default_format = pyaudio.paInt16
#   default_channels = 1
#   default_rate = 44100
#   default_seconds = 0

#   # set default
#   def __init__(self, a):
#     super(MicrophoneReader, self).__init__(a)
#     self.audio = pyaudio.PyAudio()
#     self.stream = None
#     self.data = []
#     self.channels = MicrophoneReader.default_channels
#     self.chunksize = MicrophoneReader.default_chunksize
#     self.rate = MicrophoneReader.default_rate
#     self.recorded = False

#   def start_recording(self, channels=default_channels,
#                       rate=default_rate,
#                       chunksize=default_chunksize,
#                       seconds=default_seconds):
#     self.chunksize = chunksize
#     self.channels = channels
#     self.recorded = False
#     self.rate = rate

#     if self.stream:
#       self.stream.stop_stream()
#       self.stream.close()

#     self.stream = self.audio.open(
#       format=self.default_format,
#       channels=channels,
#       rate=rate,
#       input=True,
#       frames_per_buffer=chunksize,
#     )

#     self.data = [[] for i in range(channels)]

#   def process_recording(self):
#     data = self.stream.read(self.chunksize)

#     # http://docs.scipy.org/doc/numpy/reference/generated/numpy.fromstring.html
#     # A new 1-D array initialized from raw binary or text data in a string.
#     nums = np.fromstring(data, np.int16)

#     for c in range(self.channels):
#       self.data[c].extend(nums[c::self.channels])
#       # self.data[c].append(data)

#     return nums

#   def stop_recording(self):
#     self.stream.stop_stream()
#     self.stream.close()
#     self.stream = None
#     self.recorded = True

#   def get_recorded_data(self):
#     return self.data

#   def save_recorded(self, output_filename):
#     wf = wave.open(output_filename, 'wb')
#     wf.setnchannels(self.channels)
#     wf.setsampwidth(self.audio.get_sample_size(self.default_format))
#     wf.setframerate(self.rate)

#     # values = ','.join(str(v) for v in self.data[1])
#     # numpydata = numpy.hstack(self.data[1])

#     chunk_length = len(self.data[0]) / self.channels
#     result = np.reshape(self.data[0], (chunk_length, self.channels))
#     # wf.writeframes(b''.join(numpydata))
#     wf.writeframes(result)
#     wf.close()

#   def play(self):
#     pass

#   def get_recorded_time(self):
#     return len(self.data[0]) / self.rate
