# Cross-Platform File & Audio Transmission Experiment

This directory contains the source codes and empirical demonstration videos for the cross-platform wireless communication experiment. The project establishes a functional Software-Defined Radio (SDR) link between a **Linux environment (Transmitter/TX)** and a **Windows environment (Receiver/RX)** utilizing the PlutoSDR platform.

## System Architecture
* **Transmitter (TX Node):** Linux Environment running host-side Python scripts to modulate baseband signals into Wideband FM IQ samples.
* **Receiver (RX Node):** Windows Environment executing host-side hardware capturing, software-defined Digital Signal Processing (DSP) demodulation, and real-time audio playback.
* **RF Link:** Conducted coaxial setup to prevent ambient interference and ensure signal integrity.

---

## Experimental Demonstration Videos

### 1. Initial Link Integrity Check (Sine Wave Tone)
Prior to streaming complex multimedia audio, a continuous 1 kHz mathematical sine wave was generated at the Linux TX node to verify the baseline hardware-to-software scheduling loop. The Windows RX node successfully captured the RF signal and demodulated a stable, clear audio tone.



https://github.com/user-attachments/assets/eb1ae9ab-2078-424c-a77a-cf6039b09b8f




### 2. Final Real-Time Audio Streaming (Music File)
Following the baseline tone verification, an actual digital audio file (`music.wav`) was successfully transmitted across the heterogeneous OS platforms. The Windows RX node executed real-time phase demodulation and filtering, recovering the original high-fidelity music with exceptional audio clarity.



https://github.com/user-attachments/assets/4f23d035-8e97-4d05-966f-48b94cecf33d




---

## Directory Structure
* `tx_music_2.py`: Linux-side Wideband FM audio hardware transmitter script.
* `rx_demod_final.py`: Windows-side real-time RF capture, DSP FM demodulator, and audio playback script.
* `demo_01_sine_tone_verification.mp4`: Continuous tone link validation video.
* `demo_02_realtime_audio_streaming.mp4`: Multimedia streaming confirmation video.
