# EmbeddedML

Embedded machine-learning teaching code from FirmwareMine for ESP32-S3-Korvo-2 V3.1.

## Choose a VS Code workspace

- Open `examples/` for the C11/Python development-workstation experiments. Its README maps all 70 files, documents Linux/WSL prerequisites and names the chapter tasks. These are host teaching experiments, not flashable firmware.
- Open `firmware/korvo_mic_lab/` for the ESP-IDF microphone-capture project. Use ESP-IDF 5.4.4 with the official Espressif ESP-IDF extension `espressif.esp-idf-extension` 2.3.0. Native USB routing requires the documented board modification; stock and modified console configurations differ. Read the project's README and DEBUGGING guide before connecting or flashing.

## Evidence and limits

The host package passes ordinary Linux C builds, CTests and the listed parity/fixture checks. The Korvo source passes ESP32-S3 cross-compilation for stock UART and native-USB console profiles. Physical capture, hardware-debug performance, latency and power are not verified. Synthetic scores are not field accuracy. The capture project extracts features, not speech labels. No networking, raw recording, display/camera/SD initialization or battery work is included in that lab.

Saved synthetic data, JSON models, generated C headers and known-answer reports are included for inspection and reproducibility. Training/export/report tasks may overwrite them. The examples manifest identifies delivered bytes, not outputs after regeneration. No SDK checkout, managed dependencies, build directories, prebuilt firmware or private credentials belong in this repository.

The book and website reader are distributed separately. No hosted book URL is asserted here until deployment is verified.

## License

Original code in this repository is licensed under the MIT License. See LICENSE. Third-party dependency licenses and notices remain applicable; see `firmware/korvo_mic_lab/THIRD_PARTY.md`. Book text, product photography and branding are not included in this source repository and are not licensed by this code license.
