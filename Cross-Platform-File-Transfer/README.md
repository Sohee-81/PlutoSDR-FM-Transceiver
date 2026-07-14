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

## 🔍 3. Troubleshooting & Virtualization Root Cause Analysis

During the initial development framework, the transceiver link encountered critical system failures due to hardware timing and abstraction limitations in virtualized sandboxes. Below are the engineering diagnostics and solutions implemented to achieve a stable production state:

### 3.1. Hardware Buffer Overflow (`ConnectionResetError` / `Broken Pipe / Errno 104`)
* **Symptom:** The transmission pipeline terminated abruptly after 2 to 3 seconds of execution.
* **Root Cause:** The host CPU pushed digital IQ blocks into the PlutoSDR internal DMA buffer at raw processing speed without hardware pacing. Because the software ingestion velocity outpaced the physical RF radiation rate ($\text{Duration} = \frac{\text{Buffer Size}}{\text{Sample Rate}}$), the onboard cyclic rings experienced a catastrophic overflow, triggering a sudden USB bus tear down.
* **Engineering Solution:** Implemented a deterministic rate-matched friction lock using an explicit hardware-software sync loop:
  ```python
  
  # Slicing high-speed arrays into steady 32,768 sample blocks
  chunk = tx_signal[i * buffer_size : (i + 1) * buffer_size]
  sdr.tx(chunk)
  time.sleep(chunk_duration * 0.95)  # 5% safety guard band to prevent underflow/overflow
  
By forcing the runtime loop to sleep for exactly 95% of the block's physical broadcast duration, the software injection cycle dynamically calibrated to the physical DAC drain cycle, establishing an uninterrupted looping transmission.  

3.2. WSL2 Virtual Network Isolation (TimeoutError / No Device Found)Symptom: The Windows-guest WSL2 terminal failed to discover the physical PlutoSDR over USB, raising OSError: [Errno 110] Connection timed out.  Root Cause: Core virtualization layers isolate the underlying Windows host hardware buses from the virtualized Ubuntu guest kernel interface. NAT configurations enforced by recent usbipd-win update engines altered local network interface routing, causing the automated scanning backends (usb:0.0.0) to drop device discovery across the container boundary[cite: 1].  Engineering Solution: Hardcoded explicit IP network sockets within the hardware instantiation handle:  Pythonsdr = adi.Pluto("ip:192.168.2.1")


By targeting the fixed TCP/IP gateway bridge layout directly, the script successfully initiated safe socket mapping over the usbipd virtualization tunnel, clearing the guest OS discovery constraint completely.  📐 4. End-to-End System ArchitectureThe conceptual diagram below illustrates the cross-platform signal flow, tracking the multimedia baseband conversions down through the virtualized network interface layer into physical electromagnetic waves[cite: 1, 2]:

Plaintext  +-----------------------------------+             +-----------------------------------+
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


5. Low-Level Environment Diagnostics & Hardware Verification
5.1. Isolated Environment InitializationTo isolate hardware drivers and dependency packages from system-wide libraries, run the following workspace initialization steps inside the host terminal[cite: 1]:Bash# Workspace

setup and package installation sequence
mkdir -p ~/pluto_V2
cd ~/pluto_V2
sudo apt update && sudo apt install python3-venv python3-full -y
python3 -m venv sdr_env
source sdr_env/bin/activate
pip install pyadi-iio numpy scipy sounddevice

5.2. Pre-Execution Network Ping CheckBefore triggering python abstraction layers, run an ICMP echo verification test to confirm low-latency hardware routing transparency over the default interface gateway[cite: 1]:Bashping -c 4 192.168.2.1
Expected Diagnostic Output Profile:PlaintextPING 192.168.2.1 (192.168.2.1) 56(84) bytes of data.
64 bytes from 192.168.2.1: icmp_seq=1 ttl=64 time=0.499 ms
64 bytes from 192.168.2.1: icmp_seq=2 ttl=64 time=0.231 ms
64 bytes from 192.168.2.1: icmp_seq=3 ttl=64 time=0.229 ms
64 bytes from 192.168.2.1: icmp_seq=4 ttl=64 time=0.244 ms

--- 192.168.2.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3064ms
rtt min/avg/max/mdev = 0.229/0.300/0.499/0.114 ms
Achieving an average round-trip latency ($\text{rtt}_{\text{avg}}$) of $0.300\text{ ms}$ with 0% packet drop rates verifies physical USB data-link integrity before runtime executions[cite: 1].
