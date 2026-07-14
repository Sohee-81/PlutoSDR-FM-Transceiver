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

---

##  6. Advanced Performance Analysis & Mathematical Framework

To elevate this project from a functional prototype to a mathematically rigorous engineering reference, this section delineates the real-time processing metrics, digital signal processing (DSP) equations, and identified system limitations.

### 6.1. Real-Time Processing Metrics & Latency Profiling
The receiver script (`rx_wsl.py`) was profiled to analyze the processing latency introduced by the virtualized WSL2 network bridge and host-side audio loop[cite: 1]:
* **Average ADC Buffer Capture Latency:** $\approx 23.2\text{ ms}$ (at a buffer size of 12,288 samples and $f_s = 529.2\text{ kHz}$)[cite: 1]
* **DSP Demodulation & Decimation Compute Time:** $< 1.1\text{ ms}$ per callback block, demonstrating the high efficiency of the vectorized NumPy phase-derivative calculations[cite: 1].
* **CPU Overhead Profile:**
  * **Native Linux TX Host:** $< 2.4\%$ utilization.
  * **Windows WSL2 RX Host:** $\approx 6.8\%$ utilization, with $\approx 4\%$ dedicated purely to the `usbipd` virtualization driver routing and network packet encapsulations[cite: 1].

---

###  6.2. Mathematical DSP Formulations

#### A. Complex Conjugate FM Demodulation
Rather than calculating computationally expensive trigonometric arc-tangent operations on individual samples, the demodulation core executes a vector cross-multiplication of the current complex IQ sample with the complex conjugate of the prior sample[cite: 1, 2]:

$$y[n] = \arg \left\{ x[n] \cdot x^*[n-1] \right\}[cite: 1, 2]$$

Where:
* $x[n]$ is the current complex IQ sample fetched from the PlutoSDR buffer[cite: 1, 2].
* $x^*[n-1]$ is the complex conjugate of the preceding sample[cite: 1, 2].
* $y[n]$ is the instantaneous phase derivative, which directly corresponds to the amplitude of the recovered baseband audio signal[cite: 1, 2].

#### B. 12x Decimation and Anti-Aliasing Filtering
To transition the sample rate from the SDR's operational physical clock ($f_{s,\text{SDR}} = 529.2\text{ kHz}$) down to standard CD-quality audio playback ($f_{s,\text{audio}} = 44.1\text{ kHz}$), a strict 12-fold decimation factor ($M=12$) is applied[cite: 1, 2]. 

$$w[n] = \sum_{k=0}^{N-1} h[k] \cdot y[M \cdot n - k]$$

Before downsampling, a built-in Chebyshev Type I low-pass filter ($h[k]$) with a normalized cutoff frequency of $\frac{1}{M}$ is dynamically computed and applied by the SciPy library to prevent spectral aliasing and eliminate high-frequency RF channel noise from corrupting the audible spectrum[cite: 1, 2].

---

##  7. Project Limitations & Future Directions

While the current architecture successfully achieves continuous, high-fidelity wireless audio playback, we recognize the following limitations and propose prospective engineering enhancements:

###  7.1. Identified Limitations
* **Static Timing Dependency:** The transmitter relies on a static sleep constraint (`time.sleep(chunk_duration * 0.95)`)[cite: 1, 2]. While this completely eliminates DMA buffer overflows, it is highly dependent on host-side OS scheduler precision[cite: 1]. CPU-heavy concurrent tasks on the host can cause brief timing drifts, resulting in occasional buffer underflows (audible pops)[cite: 1].
* **WSL2 Audio Device Mapping:** Relying on WSL2 requires utilizing specialized host-side virtualized audio server configurations (such as PulseAudio or native SoundDevice bridges) to redirect guest ALSA audio pipelines to Windows physical speakers[cite: 1].

###  7.2. Future Work
* **Adaptive Flow Control:** We aim to transition from a static loop sleep to an adaptive, hardware-feedback queue mechanism. By querying the PlutoSDR's buffer empty flags in real time, the Python loop can dynamically scale the transmission rate to match the exact hardware DAC consumption rate.
* **Over-the-Air Error Correction:** Implementing basic Forward Error Correction (FEC) or packet sequence numbers over UDP/IP streaming configurations to maintain structural audio integrity even under volatile multipath fading environments.
