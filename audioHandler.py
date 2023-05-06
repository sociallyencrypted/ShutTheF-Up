import pyaudio
import os
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
WAVE_OUTPUT_FILENAME = "/tmp/input.audio.fifo"

audioController = pyaudio.PyAudio()
device_index = None
for i in range(audioController.get_device_count()):
    if "USB" in audioController.get_device_info_by_index(i)['name']: # USB microphone
        device_index = i
        break
    
if device_index is None:
    print("No USB microphone found")
    exit()

microphoneStream = audioController.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024, input_device_index=device_index)

os.system("mkfifo " + WAVE_OUTPUT_FILENAME)

print("* recording")

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audioController.get_sample_size(FORMAT))
wf.setframerate(RATE)

while True:
    try:
        for i in range(0, int(RATE / CHUNK)):
            data = microphoneStream.read(CHUNK)
            data = bytes(data)
            wf.writeframes(data)

    except KeyboardInterrupt:
        print("* recording stopped")
        break
        
wf.close()

