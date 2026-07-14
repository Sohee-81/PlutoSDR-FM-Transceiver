# PlutoSDR Wideband FM Transceiver & File Transmission Project

This repository contains Python scripts for software-defined radio (SDR) communication using **PlutoSDR** hardware. The project encompasses two major experimental setups: real-time FM audio streaming and cross-platform file transmission.

---

## Hardware Setup & RF Environment

To maintain a controlled laboratory environment and prevent over-the-air interference with licensed spectrums, all experiments were conducted via a **conducted RF link** using coaxial cables and an RF splitter, bypassing antennas.


[ TX Laptop ] ──> [ Tx PlutoSDR ] ──(Coaxial Cable)──> [ RF Splitter / Divider ]
                                                              │
                                     ┌────────────────────────┴────────────────────────┐
                                     ▼                                                 ▼
                         [ Spectrum Analyzer ]                                   [ Rx PlutoSDR ] ──> [ RX Laptop ]
                       (Real-time Signal Monitoring)                              (Signal Demodulation)

* **Center Frequency ($f_c$):** 350.0 MHz
* **SDR Sample Rate ($f_s$):** 1.0 MHz
* **Frequency Deviation ($\Delta f$):** 75 kHz (Standard Wideband FM)

---

## Experimental Overviews

### Experiment 1: Real-Time FM Audio Modulation & Live Streaming
* **Concept:** Transmitting a continuous audio baseline from a Linux host and demodulating it on the fly.
* **TX (Linux):** Imports a \`music.wav\` file, executes DSP normalization, scales the baseband registers for the 12-bit DAC, and streams the wideband FM signal continuously using a cyclic buffer.
* **RX (Linux/WSL):** Captures raw IQ complex data via DMA streams, recovers the instantaneous phase using a complex differentiator algorithm, filters high-frequency noise with a 6th-order Butterworth LPF (15 kHz cutoff), and pipes the downsampled audio directly to local laptop speakers using \`sounddevice\`.

### Experiment 2: Cross-Platform Wireless Audio File Transmission
* **Concept:** End-to-end file transfer over an RF communication link between different operating systems.
* **TX (Linux):** Modulates and transmits the target music audio file from a Linux environment over the 350 MHz RF carrier.
* **RX (Windows):** Captures the transmitted RF signal using a Windows-hosted PlutoSDR setup, performs software demodulation, and reconstructs the data back into a physical WAV file (\`recovered_music.wav\`) stored locally on the Windows machine.

---

## Dependencies

Ensure your Python virtual environment (\`sdr_env\`) has the system bindings and hardware drivers configured properly:

* **libiio / adi:** Analog Devices PlutoSDR hardware abstraction layer bindings
* **numpy & scipy:** Vectorized matrix operations, complex differentiation, and filter design
* **matplotlib:** Local software DSP visualization (Time/Frequency domain)
* **sounddevice:** Real-time audio hardware ring-buffer streaming (Required for Experiment 1)

---

## How to Run

### Experiment 1: Real-Time Streaming
1. Run the transmitter script on the TX laptop:
   \`\`\`bash
   python3 pluto_music_0_tx.py
   \`\`\`
   *Close the generated Matplotlib figure window to release the execution flow and initialize hardware Tx.*
2. Run the real-time receiver script on the RX laptop:
   \`\`\`bash
   python3 pluto_realtime_rx.py
   \`\`\`

### Experiment 2: File Transmission (Linux to Windows)
1. Initiate the transmission script on the **Linux TX Laptop**.
2. Run the recording/demodulation script on the **Windows RX Laptop** to capture the stream for the designated duration.
3. Once the capture completes, the recovered audio file will be generated in your project directory as \`recovered_music.wav\`.

---

## Results & Observations
* **Spectrum Verification:** The Rigol RSA5032N Spectrum Analyzer verified a clean, symmetrical Wideband FM spectral flare centered at 350 MHz with an optimal peak power of approximately -20 dBm, ensuring a high Signal-to-Noise Ratio (SNR) for both experiments.
* **Audio Fidelity:** The complex differentiation combined with decimation successfully eliminated cross-platform buffer discrepancies, yielding clear audio reconstruction without phase discontinuities or clicking artifacts.
EOF
