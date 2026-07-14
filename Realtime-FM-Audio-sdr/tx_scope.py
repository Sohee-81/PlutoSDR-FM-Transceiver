import sys
import time
import numpy as np
import scipy.signal as signal

# Ensure Python environment maps to system-wide libiio hardware drivers
sys.path.append('/usr/lib/python3/dist-packages')
import adi

# Parameter Configurations
fs_sdr = int(1e6)          # SDR Sample Rate: 1 MHz
carrier_freq = int(350e6)  # Target Center Frequency: 350 MHz
fm_deviation = 75000       # Wideband FM Deviation: 75 kHz

# Baseband Test Signal Generation (1 kHz Continuous Sine Wave)
fs_signal = 44100
t = np.arange(0, 2.0, 1.0 / fs_signal)
baseband_tone = np.sin(2 * np.pi * 1000 * t).astype(np.float32)

# DSP Resampling & FM Phase Integration
num_samples = int(len(baseband_tone) * fs_sdr / fs_signal)
message_resampled = signal.resample(baseband_tone, num_samples)
message_resampled /= np.max(np.abs(message_resampled))

sensitivity = 2 * np.pi * fm_deviation / fs_sdr
phase = np.cumsum(message_resampled * sensitivity)
tx_samples = np.exp(1j * phase).astype(np.complex64)

# Hardware Streaming Setup
try:
    sdr = adi.Pluto("ip:192.168.2.1")
    sdr.sample_rate = fs_sdr
    sdr.tx_rf_bandwidth = int(fs_sdr)
    sdr.tx_lo = carrier_freq
    sdr.tx_hardwaregain_chan0 = 0  # Initial maximum power configuration
    sdr.tx_cyclic_buffer = True    # Enable continuous looping
    
    print(f"[INFO] Initial test tone broadcasting active at {carrier_freq/1e6} MHz...")
    sdr.tx(tx_samples * 10000)     # Load to DAC registers
    
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[INFO] Test script terminated safely.")
finally:
    sdr.tx_destroy_buffer()
