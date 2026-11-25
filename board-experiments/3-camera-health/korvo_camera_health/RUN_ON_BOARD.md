# Korvo kit camera: identify, capture, inspect

This is a separate ESP-IDF5.4.4 C capture diagnostic for ESP32-S3-Korvo-2 V3.1 with the native-USB modification. It is not the CNN replay application and does not run inference. Its job is to replace uncertainty about the camera with a detected sensor ID and a real saved frame.

## Camera basis

The owner confirms this JQ-V360-F100 V3 flex camera came with his Korvo board. Espressif's Korvo BSP identifies OV3660 as the supported camera. We therefore target the kit OV3660 and confirm PID0x3660 at runtime. The flex marking itself is not a verified sensor datasheet.

The native connector is the board's24-contact DVP FPC camera connector, not the20-contact LCD cable. With all power disconnected, install only the supplied camera into its intended camera socket, in its original documented contact orientation. Do not force, hot-plug, trim, reverse or rewire the flex. If its correct insertion orientation is not known, stop and provide a socket/contact photo. Do not infer orientation from this guide. No external camera supply or GPIO jumpers are needed.

Board data0..7 are GPIO13,47,14,3,12,42,41,39. VSYNC21, HREF38, PCLK11, XCLK40 at20MHz. SCCB17/18. Reset/power-down use-1 in this driver configuration, matching the board support's no-GPIO-reset path; no IO-expander outputs are changed. GPIO48 keeps the speaker amplifier off. This is a Korvo map, not a generic ESP32-CAM map.

## VS Code

1. Use official Espressif ESP-IDF extension2.3.0 with SDK5.4.4. Open this project as a separate VS Code folder. The profile enables octal PSRAM80MHz and caps flash at8MB. Check the actual module has at least8MB flash and octal PSRAM first. Stop on a mismatch.
2. Before flashing, save any existing firmware/data you need. Flashing replaces the current application and partition table. Do not use erase-flash or change eFuses. This uses a single7MiB factory partition with no OTA, matching the separate replay diagnostic layout.
3. Choose ESP-IDF: Build your project, select the native-USB serial port, then ESP-IDF: Flash your project when ready to replace the application. This project is cross-built, not physically run yet.
4. Configure monitor log saving in the extension/ESP-IDF monitor, then reset the board. Save the complete output, including all FM_JPEG_BEGIN/FM_HEX/FM_JPEG_END lines. Terminal scrollback alone may truncate the image. The hex transfer is intentionally slow and consumes more serial bytes than JPEG. Do not use its transfer time as capture latency.
5. Look for PSRAM initialization, SENSOR_PID=0x3660 and three FRAME records. The app discards five warmup frames, captures320x240 sensor-JPEG, logs byte count/CRC/capture_us/heap, then sends the first JPEG as hex while retaining ownership of its buffer. Driver JPEG output is not a C++ JPEG encoder. No JPEG decoding or RGB conversion is compiled here.
6. Open a Python-capable VS Code terminal and run the included extract_frame.py with the saved log path and desired image path. Alternatively place your saved log at monitor.log and choose Terminal > Run Task > FirmwareMine: extract captured JPEG. It checks payload length, CRC32 and JPEG markers before writing capture.jpg. Open that actual image. CRC is accidental-corruption detection, not authentication.
7. Return the complete log and capture.jpg. Inspect color, focus, orientation and scene framing. A sensor-ID pass without a viewable frame is not successful capture. If init fails or PID differs, stop and return the full log. Do not change wires/pin maps to make the probe pass.

Task watchdog remains enabled in this capture-only diagnostic. No microphone, speaker, display, radio, SD card or CNN is initialized. No target capture score or timing has been measured. Next is host/target preprocessing on the same captured bytes, then CNN integration, then independent live-scene evaluation.

## Sources and third-party driver

- https://github.com/espressif/esp-bsp/blob/master/bsp/esp32_s3_korvo_2/README.md
- https://github.com/espressif/esp-bsp/blob/master/bsp/esp32_s3_korvo_2/include/bsp/esp32_s3_korvo_2.h
- https://docs.espressif.com/projects/esp-adf/en/latest/multimedia-boards/dev-boards/user-guide-esp32-s3-korvo-2.html
- https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-Korvo-2_V3.1.2_20240116.pdf
- https://github.com/espressif/esp32-camera

The Espressif camera driver is third-party Apache2.0 code, not original FirmwareMine code. Its notices are preserved. Pinned revision f5257073e2a41c945eb618570a76063b8e4eed18. The project selects capture-only C sources and omits the original optional converter-header include from esp_camera.h, so JPEG encoders and C++ converters are neither built nor linked. The rest of the vendored upstream tree is preserved for provenance, including files not compiled. See components/camera_capture/CMakeLists.txt for the exact selection. No inference runtime is used.
