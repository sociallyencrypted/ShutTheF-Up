import datetime as dt
import pyaudio
import numpy as np
import time
import config
import requests

# Initialize the audioHandler
audioHandler = pyaudio.PyAudio()

# Define audio audioHandlerrameters
CHANNELS = config.CHANNELS
RATE = config.RATE
CHUNK = config.CHUNK
FREQ = config.BEEP_FREQUENCY
URL = 'http://localhost:' + str(config.PORT) + '/status'

inputIndex = None
outputIndex = None

censor_mode =False
censor_next = True
speaking_right_now = False
word_detected = False

volume=[]

# ----------------- HELPERS -----------------
# Function to generate a sine wave
def makeSin(length):
    length=int(length * RATE)
    factor = FREQ * np.pi * 2 / RATE
    return np.sin(np.arange(length) * factor)

# Function to generate a beep sound
def censor(length):
    sin = makeSin(length)
    return sin

# Function to find the index of a device given a substring of its name
def findDeviceIndex(device_name_substring):
    for i in range(audioHandler.get_device_count()):
        if device_name_substring in audioHandler.get_device_info_by_index(i)['name']:
            return i
    return None

def makeStream(index, isInput):
    if isInput:
        return audioHandler.open(format=pyaudio.paFloat32,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK, input_device_index=index)
    else:
        return audioHandler.open(format=pyaudio.paFloat32,
                     channels=CHANNELS,
                     rate=RATE,
                     output=True,
                     frames_per_buffer=CHUNK, output_device_index=index)
        
def closeStream(stream):
    stream.stop_stream()
    stream.close()

def getVolume(stream):
    data = stream.read(CHUNK)
    data_volume = np.mean(np.abs(np.frombuffer(data, dtype=np.float32)))*10000
    return data_volume

# ----------------- MAIN -----------------

def startAudioCensorship():
    global inputIndex, outputIndex, censor_mode, censor_next, speaking_right_now, word_detected, volume
    inputIndex = findDeviceIndex(config.INPUT_DEVICE_NAME_SUBSTRING)
    outputIndex = findDeviceIndex(config.OUTPUT_DEVICE_NAME_SUBSTRING)
    
    if inputIndex is None:
        print("Input device not found")
        return
    if outputIndex is None:
        print("Output device not found")
        return
    
    # Open input and output streams
    stream_in = makeStream(inputIndex, True)
    stream_out = makeStream(outputIndex, False)

    # Continuously read from the input stream and write to the output stream
    while True:
        try:
            if not censor_mode:
                if (requests.get(URL).text == "Censoring"):
                    censor_mode = True
            data = stream_in.read(CHUNK, exception_on_overflow = False)
            # depending on whether censor mode is on or not, either play back the audio or play back silence
            if censor_mode:
                # if the input data has low volume it means the user is changing words
                # we need to censor random words
                # if the input data has high volume it means the user is speaking
                data_volume = np.mean(np.abs(np.frombuffer(data, dtype=np.float32)))*10000
                volume.append(data_volume)
                if data_volume > 1000:
                    if not speaking_right_now:
                        print("speaking")
                        speaking_right_now = True
                    if censor_next and not word_detected:
                        print(data_volume)
                        # censor till this word ends and then set censor_next to False
                        wave = censor(CHUNK/RATE).astype(np.float32).tobytes()
                        stream_out.write(wave)
                        word_detected = True
                    else:
                        stream_out.write(data)
                        word_detected = False
                else:
                    if speaking_right_now:
                        print("not speaking")
                
                    speaking_right_now = False
                    censor_next = np.random.rand() < 0.4
                    stream_out.write(data)  
                    word_detected = False
                
            else:
                stream_out.write(data)
        except KeyboardInterrupt:
            print("\nStopping audioHandler")
            break

    print("average volume: ", np.mean(volume))
    # Clean up resources
    closeStream(stream_in)
    closeStream(stream_out)
    audioHandler.terminate()
    
startAudioCensorship()