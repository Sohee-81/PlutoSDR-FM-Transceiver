import sys
import time
import os
import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wavf
import matplotlib.pyplot as plt

# [Path Mapping] Allow Python virtual environment to access system-wide libiio hardware drivers
sys.path.append('/usr/lib/python3/dist-packages')
import adi

# ==============================================================================
# 1. PARAMETER CONFIGURATION
# ==============================================================================
fs_sdr = int(1e6)          # SDR Sampling Rate: 1 MHz
carrier_freq = int(350e6)  # Transmitter Center Frequency: 350.0 MHz
fm_deviation = 75000       # Wideband FM Frequency Deviation: 75 kHz

# ==============================================================================
# 2. AUDIO BASEBAND DATA LOADING & PROCESSING
# ==============================================================================
audio_filename = 'music.wav'
fs_audio = 44100  # Default fallback audio sample rate

if os.path.exists(audio_filename):
    try:
        # Load the physical wav audio file
        fs_audio, audio_data = wavf.read(audio_filename)
        print(f"[SUCCESS] Active music file '{audio_filename}' loaded successfully.")
        print(f" -> Original Sample Rate: {fs_audio} Hz")
        
        # Convert to Mono if the audio is Stereo
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
            
        # DSP Normalization: Scale amplitude between -1.0 and +1.0
        audio_baseband = audio_data.astype(np.float32)
        audio_baseband /= np.max(np.abs(audio_baseband))
    except Exception as e:
        print(f"[ERROR] Failed to read wav file: {e}. Switching to test tone.")
        audio_filename = None

# Fallback: If 'music.wav' is missing or corrupted, generate synthetic dual-tone emergency signal
if not os.path.exists(audio_filename) or audio_filename is None:
    print(f"[WARNING] '{audio_filename}' not found or unreadable!")
    print("[FORCE] Generating active dual-tone message (1 kHz + 2 kHz) to guarantee RF waves!")
    fs_audio = 44100
    t_tone = np.arange(0, 5.0, 1.0 / fs_audio)
    # Generate 1 kHz + 2 kHz continuous sine waves
    audio_baseband = 0.5 * np.sin(2 * np.pi * 1000 * t_tone) + 0.5 * np.sin(2 * np.pi * 2000 * t_tone)

# ==============================================================================
# 3. MATHEMATICAL FM MODULATION (DSP)
# ==============================================================================
print("[DSP] Resampling baseband message from audio rate to 1 MHz SDR rate...")
# Calculate resampling ratio to scale up to 1 MHz
num_samples = int(len(audio_baseband) * fs_sdr / fs_audio)
message_resampled = signal.resample(audio_baseband, num_samples)
message_resampled /= np.max(np.abs(message_resampled))  # Re-normalize after resampling

print("[DSP] Performing continuous phase integration for FM modulation...")
# Frequency Modulation physics: Phase is the integral of the frequency message
sensitivity = 2 * np.pi * fm_deviation / fs_sdr
phase = np.cumsum(message_resampled * sensitivity)
tx_samples = np.exp(1j * phase).astype(np.complex64)  # Generate Complex IQ samples

# ==============================================================================
# 4. DSP 파형 시각화 (MATPLOTLIB VISUALIZATION)
# ==============================================================================
print("[INFO] Displaying Software DSP Waveforms. Close the plot window to start PlutoSDR hardware TX.")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

# Plot Time-domain Baseband Message
ax1.plot(message_resampled[:2000], color='blue')
ax1.set_title("Baseband Message Signal (Time Domain - Zoomed)")
ax1.set_xlabel("Samples")
ax1.set_ylabel("Amplitude")
ax1.grid(True)

# Plot Frequency Spectrum of Modulated IQ Signal
ax2.psd(tx_samples, NFFT=1024, Fs=fs_sdr/1e3, Fc=carrier_freq/1e6, color='orange')
ax2.set_title("Modulated FM Signal Spectrum (Frequency Domain)")
ax2.set_xlabel("Frequency (MHz)")
ax2.set_ylabel("Power Spectral Density (dB/Hz)")

plt.tight_layout()
plt.show()  # Execution pauses here until the user closes the graph window

# ==============================================================================
# 5. PLUTOSDR HARDWARE INITIALIZATION & TX LOOP
# ==============================================================================
print("[HARDWARE] Initializing Tx PlutoSDR Hardware connection...")
try:
    sdr = adi.Pluto("ip:192.168.2.1")
    print("[SUCCESS] Connected to Tx PlutoSDR Hardware.")
except Exception as e:
    print(f"[ERROR] SDR Connection Failed: {e}")
    sys.exit()

# Configure PlutoSDR Hardware Parameters
sdr.sample_rate = fs_sdr
sdr.tx_rf_bandwidth = int(fs_sdr)
sdr.tx_lo = carrier_freq
sdr.tx_hardwaregain_chan0 = -10  # Hardware attenuation adjustment (dB)

# Enable Cyclic Buffer for seamless, infinite continuous transmission looping
sdr.tx_cyclic_buffer = True

print("----------------------------------------------------------------------")
print(f"Wireless FM Broadcasting Active at {sdr.tx_lo / 1e6} MHz...")
print("Verify the spectral flare (FM Dome) on the Rigol Spectrum Analyzer screen!")
print("Press Ctrl+C to terminate transmission safely.")
print("----------------------------------------------------------------------")

try:
    # Push the modulated IQ block onto the SDR hardware DAC buffer
    sdr.tx(tx_samples * 10000)  # Scale integer bits for Ad9361 DAC registers
    
    # Keep the main process alive while the hardware loops the cyclic buffer
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n[INFO] Transmission stopped by user.")
finally:
    # Clean up and release PlutoSDR hardware resources safely
    sdr.tx_destroy_buffer()
    print("[INFO] Hardware TX buffers cleared successfully.")
