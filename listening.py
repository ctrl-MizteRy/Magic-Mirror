import argparse
import tempfile
import queue
import sys
import sounddevice as sd
import soundfile as sf
import numpy
assert numpy
import time
import os
import vosk
import wave
import json
from greeting import Start_Speaking

class Listening:
    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit')
        self.args, self.remaining = self.parser.parse_known_args()
        if self.args.list_devices:
            print(sd.query_devices())
            self.parser.exit(0)
        self.parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[self.parser])
        self.parser.add_argument(
            'filename', nargs='?', metavar='FILENAME',
            help='audio file to store recording to')
        self.parser.add_argument(
            '-d', '--device', type=self.int_or_str,
            help='input device (numeric ID or substring)')
        self.parser.add_argument(
            '-r', '--samplerate', type=int, help='sampling rate')
        self.parser.add_argument(
            '-c', '--channels', type=int, default=1, help='number of input channels')
        self.parser.add_argument(
            '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
        self.args = self.parser.parse_args(self.remaining)

        self.q = queue.Queue()
        self.speak = Start_Speaking()

    def int_or_str(self, text):
        try:
            return int(text)
        except ValueError:
            return text
        
    def callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def start_listen(self, duration: int) -> str: #Using duration to change the setting based on user preferrence of how long you want the machine to record your speech
        try:
            if self.args.samplerate is None:
                device_info = sd.query_devices(self.args.device, 'input')
                self.args.samplerate = int(device_info['default_samplerate'])
            if self.args.filename is None:
                self.args.filename = tempfile.mktemp(prefix='listening_file', suffix='.wav', dir='')

            with sf.SoundFile(self.args.filename, mode='x', samplerate=self.args.samplerate, channels=self.args.channels, subtype= self.args.subtype) as file:
                with sd.InputStream(samplerate=self.args.samplerate, device= self.args.device, channels= self.args.channels, callback= self.callback):
                    start = time.time()
                    self.duration(start, file, duration)
            
            self.speak.speak("voice_records/speaking_respone.mp3")
            return self.translate_to_text()
        except KeyboardInterrupt:
            self.parser.exit(0)
        except Exception as e:
            print(f"Error detected: {e}")
            os.remove(self.args.filename)
            self.parser.exit(type(e).__name__ + ': ' + str(e))

    def duration(self, start, file: sf.SoundFile, duration: int) -> None:
        while int(time.time()) - start <= duration: #using time.time() as a count down timmer for the duration
            file.write(self.q.get())
    
    def translate_to_text(self) -> str:
        if not os.path.exists("vosk-model-en-us-0.22-lgraph"): #You can definitely use a different model here if you want, just follow the link before for it
            return "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder."
        wf = wave.open(self.args.filename, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            raise TypeError("Audio file must be WAV format mono PCM.")

        vosk.SetLogLevel(-1) #Disable LOG from vosk from printing to terminal
        model = vosk.Model('speech_model/vosk-model-en-us-0.22-lgraph')
        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        text_lst =[]
        p_text_lst = []
        p_str = []
        len_p_str = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                text_lst.append(rec.Result())
            else:
                p_text_lst.append(rec.PartialResult())

        if len(text_lst) !=0:
            jd = json.loads(text_lst[0])
            txt_str = jd["text"]
            
        elif len(p_text_lst) !=0: 
            for i in range(0,len(p_text_lst)):
                temp_txt_dict = json.loads(p_text_lst[i])
                p_str.append(temp_txt_dict['partial'])
        
            len_p_str = [len(p_str[j]) for j in range(0,len(p_str))]
            max_val = max(len_p_str)
            indx = len_p_str.index(max_val)
            txt_str = p_str[indx]
                
        else:
            txt_str = ""

        os.remove(self.args.filename)
        return txt_str
