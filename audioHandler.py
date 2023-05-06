import pyaudio

# Initialize the audioHandler
audioHandler = pyaudio.PyAudio()

# Define audio audioHandlerrameters
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# find the USB microphone and speaker
id_index = None
od_index = None
for i in range(audioHandler.get_device_count()):
    print(audioHandler.get_device_info_by_index(i))
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
stream_in = audioHandler.open(format=pyaudio.audioHandlerInt16,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK, input_device_index=id_index)

# Open audio stream for output
stream_out = audioHandler.open(format=pyaudio.audioHandlerInt16,
                     channels=CHANNELS,
                     rate=RATE,
                     output=True,
                     frames_per_buffer=CHUNK, output_device_index=od_index)

# Continuously read from the input stream and write to the output stream
while True:
    data = stream_in.read(CHUNK)
    stream_out.write(data)

# Clean up resources
stream_in.stop_stream()
stream_in.close()
stream_out.stop_stream()
stream_out.close()
audioHandler.terminate()
