import sys
import time
import numpy as np
import scipy.signal as signal
from scipy.io import wavfile

# Ensure Python environment maps to system-wide libiio hardware drivers if needed
sys.path.append('/usr/lib/python3/dist-packages')
import adi

try:
    # 1. Load and Pre-process WAV File
    fs_audio, audio_data = wavfile.read("music.wav")
except FileNotFoundError:
    print("ERROR: 'music.wav' file not found in the current directory!")
    sys.exit(1)

# Stereo to Mono downmixing if necessary
if len(audio_data.shape) > 1:
    audio_data = audio_data[:, 0]

# Normalize baseband audio
audio_data = audio_data.astype(np.float32)
audio_data /= np.max(np.abs(audio_data))

# 2. Resampling to Match SDR Sample Rate
decim_factor = 12
fs_sdr = 44100 * decim_factor  # 529,200 Hz

if fs_audio != 44100:
    num_samples = int(len(audio_data) * fs_sdr / fs_audio)
    tx_signal = signal.resample(audio_data, num_samples)
else:
    tx_signal = signal.resample(audio_data, len(audio_data) * decim_factor)

# Convert to Complex IQ data format and amplify for RF front-end
tx_signal = (tx_signal * 5000).astype(np.complex64)

# 3. Hardware Initialization
try:
    sdr = adi.Pluto("ip:192.168.2.1")
except Exception as e:
    print(f"Hardware Connection Failed: {e}")
    sys.exit(1)

sdr.sample_rate = int(fs_sdr)
sdr.tx_rf_bandwidth = int(fs_sdr)
sdr.tx_lo = int(920000000)        # Center Frequency: 920.0 MHz
sdr.tx_hardwaregain_chan0 = -10   # Power back-off to prevent saturation

# 4. Stream Audio over Air with Buffer Overflow Protection
buffer_size = 16384 * 2           # 32,768 samples per chunk
num_chunks = len(tx_signal) // buffer_size
chunk_duration = buffer_size / fs_sdr

print("==================================================")
print("Streaming 'music.wav' over the air...")
print("Frequency: 920.0 MHz | Buffer Protection Active")
print("==================================================")

try:
    while True:
        for i in range(num_chunks):
            # Precise block slicing
            chunk = tx_signal[i * buffer_size : (i + 1) * buffer_size]
            sdr.tx(chunk)
            
            # CRITICAL ANTI-OVERFLOW TIMING MARGIN
            time.sleep(chunk_duration * 0.95)
            
        print("[INFO] Audio playback finished. Looping from the beginning.")
except KeyboardInterrupt:
    print("\n[INFO] Transmission stopped by user.")
