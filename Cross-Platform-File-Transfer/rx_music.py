import sys
import numpy as np
import sounddevice as sd
from scipy.signal import decimate

# Ensure Python environment maps to system-wide libiio hardware drivers if needed
sys.path.append('/usr/lib/python3/dist-packages')
import adi

# 1. System Configuration
fs_audio = 44100
decim_factor = 12
fs_sdr = fs_audio * decim_factor  # 529,200 Hz
center_freq = 920000000           # 920.0 MHz

# 2. Hardware Initialization (USBIPD Sandbox Network Tunneling)
try:
    sdr = adi.Pluto("ip:192.168.2.1")
except Exception:
    print("[WARN] Fixed IP initialization failed. Falling back to default discovery...")
    try:
        sdr = adi.Pluto()
    except Exception as e:
        print(f"[ERROR] No SDR Device Found: {e}")
        sys.exit(1)

sdr.sample_rate = int(fs_sdr)
sdr.rx_rf_bandwidth = int(fs_sdr)
sdr.rx_lo = int(center_freq)
sdr.rx_buffer_size = 12288
sdr.gain_control_mode_chan0 = "manual"
sdr.rx_hardwaregain_chan0 = 20    # LNA Hardware Gain Boost

# 3. Real-time Audio Callback Function for Host Playback
def audio_callback(outdata, frames, time_info, status):
    try:
        # Capture raw high-frequency IQ samples over the air
        rx_data = sdr.rx()
        
        # Remove DC Offset
        rx_data = rx_data - np.mean(rx_data)
        
        # MATHEMATICAL FM DEMODULATION (Discrete Phase Derivative)
        demod_signal = np.angle(rx_data[1:] * np.conj(rx_data[:-1]))
        
        # 12X DECIMATION DOWN TO 44.1 KHZ (Anti-aliasing filter included)
        audio_out = decimate(demod_signal, decim_factor, zero_phase=False)
        
        # Peak Amplitude Normalization & Safety Ceiling Clamping
        max_val = np.max(np.abs(audio_out))
        if max_val > 0:
            audio_out = (audio_out / max_val) * 0.3
            
        # Write clean vector into host audio device register
        outdata[:, 0] = audio_out[:frames].astype(np.float32)
        
    except Exception as e:
        # Output silence in case of packet dropping or buffer anomalies
        outdata.fill(0)

# 4. Stream Audio to Windows Host via WSL2 Link Setup
stream = sd.OutputStream(samplerate=fs_audio, channels=1,
                         callback=audio_callback, blocksize=1024)
stream.start()

print("==================================================")
print(f"WSL2 Real-time FM Receiver Active! Listening at {center_freq / 1e6} MHz...")
print("Press Ctrl+C to exit.")
print("==================================================")

try:
    while True:
        sd.sleep(1000)
except KeyboardInterrupt:
    print("\n[INFO] Closing audio stream and cleaning up hardware links.")
finally:
    stream.stop()
    stream.close()
