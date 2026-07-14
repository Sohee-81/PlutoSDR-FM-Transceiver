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

##  3. End-to-End System Architecture Diagram

The conceptual diagram below illustrates the cross-platform signal flow, tracking the multimedia baseband conversions down through the virtualized network interface layer into physical electromagnetic waves[cite: 1, 2]:

+-----------------------------------+             +-----------------------------------+
  |   [Tx Node: Native Linux Host]    |             |    [Rx Node: Windows WSL2 Guest]  |
  |  - Audio Source: music.wav        |             |  - Host Sound Engine: Playback    |
  |  - 12x Interpolation (529.2 kHz)  |             |  - 12x Decimation Filter Layer    |
  |  - Continuous Phase Integration   |             |  - Vector Derivative Demodulation |
  +-----------------------------------+             +-----------------------------------+
                   |                                                 ^
         (USB DMA Buffer Sync)                             (USBIPD Network Tunnel)
                   v                                                 |
  +-----------------------------------+             +-----------------------------------+
  |   PlutoSDR Active Transmitter     | ----------> |     PlutoSDR Active Receiver      |
  |   - AD9361 RF Front-End (DAC)     |  920.0 MHz  |   - AD9361 RF Front-End (ADC)     |
  |   - Power Level: -10 dBm          |  Over-the-  |   - Manual LNA Gain Boost: 20 dB  |
  +-----------------------------------+     Air     +-----------------------------------+

## 4. Low-Level Environment Diagnostics & Hardware Verification
## 4.1. Isolated Environment Initialization
To isolate hardware drivers and dependency packages from system-wide libraries, run the following workspace initialization steps inside the host terminal[cite: 1]:

# Workspace setup and package installation sequence
mkdir -p ~/pluto_V2
cd ~/pluto_V2
sudo apt update && sudo apt install python3-venv python3-full -y
python3 -m venv sdr_env
source sdr_env/bin/activate
pip install pyadi-iio numpy scipy sounddevice

## 4.2. Pre-Execution Network Ping Check
Before triggering python abstraction layers, run an ICMP echo verification test to confirm low-latency hardware routing transparency over the default interface gateway[cite: 1]:

ping -c 4 192.168.2.1

Expected Diagnostic Output Profile:
PING 192.168.2.1 (192.168.2.1) 56(84) bytes of data.
64 bytes from 192.168.2.1: icmp_seq=1 ttl=64 time=0.499 ms
64 bytes from 192.168.2.1: icmp_seq=2 ttl=64 time=0.231 ms
64 bytes from 192.168.2.1: icmp_seq=3 ttl=64 time=0.229 ms
64 bytes from 192.168.2.1: icmp_seq=4 ttl=64 time=0.244 ms

--- 192.168.2.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3064ms
rtt min/avg/max/mdev = 0.229/0.300/0.499/0.114 ms

Achieving an average round-trip latency ($\text{rtt}_{\text{avg}}$) of $0.300\text{ ms}$ with 0% packet drop rates verifies physical USB data-link integrity before runtime executions[cite: 1].

## 5. Directory Structure Reference
tx_music.py: Linux-side Wideband FM audio hardware transmitter script with buffer pacing[cite: 1].

rx_wsl.py: Windows-side real-time RF capture, DSP FM demodulator, and audio playback script[cite: 1].

demo_01_sine_tone_verification.mp4: Continuous tone link validation video.

demo_02_realtime_audio_streaming.mp4: Multimedia streaming confirmation video.
