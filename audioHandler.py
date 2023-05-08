import datetime as dt
import pyaudio
import numpy as np
import time

# Initialize the audioHandler
audioHandler = pyaudio.PyAudio()

# Define audio audioHandlerrameters
CHANNELS = 1
RATE = 44100
CHUNK = 1024
FREQ = 1000

censor_mode = True
censor_next = True
speaking_right_now = False
word_detected = False

volume=[]

# Function to generate a sine wave
def make_sin(length):
    length=int(length * RATE)
    factor = FREQ * np.pi * 2 / RATE
    return np.sin(np.arange(length) * factor)

# Function to generate a beep sound
def censor(length):
    sin = make_sin(length)
    return sin
                 

# find the USB microphone and speaker
id_index = None
od_index = None
for i in range(audioHandler.get_device_count()):
    if "USB" in audioHandler.get_device_info_by_index(i)['name']: # USB microphone
        id_index = i
    if "External" in audioHandler.get_device_info_by_index(i)['name']: # USB speaker
        od_index = i
    if id_index is not None and od_index is not None:
        break
        
    
if id_index is None:
    print("No USB microphone found")
    exit()
    
if od_index is None:
    print("No USB speaker found")
    exit()
    
# Open audio stream for input
stream_in = audioHandler.open(format=pyaudio.paFloat32,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK, input_device_index=id_index)

# Open audio stream for output
stream_out = audioHandler.open(format=pyaudio.paFloat32,
                     channels=CHANNELS,
                     rate=RATE,
                     output=True,
                     frames_per_buffer=CHUNK, output_device_index=od_index)

# Continuously read from the input stream and write to the output stream
while True:
    try:
        data = stream_in.read(CHUNK)
        # depending on whether censor mode is on or not, either play back the audio or play back silence
        if censor_mode:
            # # --DEBUG--
            # # construct beep sound
            # beep = censor(CHUNK).astype(np.int16).toString()
            # # play back beep sound
            # stream_out.write(beep)
            
            # --MAIN--
            # if the input data has low volume it means the user is changing words
            # we need to censor random words
            # if the input data has high volume it means the user is speaking
            data_volume = np.mean(np.abs(np.frombuffer(data, dtype=np.float32)))*10000
            volume.append(data_volume)
            if data_volume > 800:
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
                # # user stops between words
                # # censor next word if censor_next is True
                
                
                # if censor_next:
                #     print("censoring")
                #     censor_next = False
                #      # construct beep sound
                #     beep = censor(CHUNK).astype(np.int16).tobytes() 
                #     # play back beep sound
                #     stream_out.write(beep)
                #     print("beep")
                # else:
                #     stream_out.write(data)
                #     print("no beep")
                # # check if word has ended
                # data_volume = np.mean(np.abs(np.fromstring(data, dtype=np.int16)))
                # volume.append(data_volume)
                # if data_volume < 1200:
                #     r = np.random.rand()
                #     # for every 1 in 5 words
                #     if r < 0.2:
                #         censor_next = True   
            else:
                if speaking_right_now:
                    print("not speaking")
            
                speaking_right_now = False
                censor_next = np.random.rand() < 0.9
                stream_out.write(data)  
                word_detected = False
             
        else:
            stream_out.write(data)
    except KeyboardInterrupt:
        print("\nStopping audioHandler")
        break

print("average volume: ", np.mean(volume))
# Clean up resources
stream_in.stop_stream()
stream_in.close()
stream_out.stop_stream()
stream_out.close()
audioHandler.terminate()
