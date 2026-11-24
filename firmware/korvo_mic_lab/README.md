# FirmwareMine · Korvo-2 V3.1 microphone + C features

By FirmwareMine · https://firmwaremine.com

Target: Espressif ESP32-S3-Korvo-2 V3.1. This is real target firmware, successfully cross-built for ESP32-S3, but NOT yet run on a physical board. The next test is your board's serial log. It extracts features, not words/classes. No networking, raw recording, speaker playback, camera, display, SD access or battery work.

## Versions and dependencies

- ESP-IDF v5.4.4, exact project constraint. This is a tested pin, not a claim that it is the newest release.
- espressif/esp_codec_dev 1.6.2, downloaded by IDF Component Manager. dependencies.lock included.
- Application/feature code is original C11-style C. Codec code is Espressif's Apache-2.0 C dependency, attributed in THIRD_PARTY.md. SDK uses its normal mixed-language build environment. No C++ model engine is used; the SDK's final C++ linker driver does not change our source language.
- Windows, Linux or macOS can use the IDF environment. The verified build was on Linux x86-64 with the official Xtensa ESP GCC toolchain installed by IDF. No target board is attached here.

## Before flashing

Flashing replaces the board application and partition layout at the standard offsets. Keep any firmware/data you need first. Do not run erase-flash. No eFuse/security changes are required. This project leaves PSRAM unused and requests 8 MB flash, as an explicit build setting. Before flashing, perform the VS Code flash-capacity check below and verify at least 8 MB is detected. If less is detected, stop and report the module label/result; do not use these binaries or force the write. Do not attach a battery for this first lab. Leave speaker disconnected and audio output disabled. Camera/LCD daughterboards can remain mechanically present but this app does not initialize them.

Choose the connector path for the board configuration. Stock boards use CP2102N. Boards modified for native USB Serial/JTAG use the separate native-USB profile. Confirm the physical routing before selecting a profile; software configuration alone does not change the USB wiring.

Use two Micro-B USB cables as the board guide describes. Data cable: computer to the data connector J6. On stock boards it enumerates CP2102N; on a board modified for native USB routing it enumerates Espressif USB Serial/JTAG. Power cable: board's dedicated USB power connector to a stable regulated 5 V USB supply; the official guide recommends at least 2 A. Read the connector labels rather than assuming left/right from an illustration. Switch power ON. No breadboard wires or external microphone are needed. Do not feed 5 V into GPIO pins.

The two stock USB ports are NOT interchangeable native-JTAG ports. One is UART, the other power. See DEBUGGING.md before considering step debugging.

## VS Code setup and project opening

Use Visual Studio Code with Espressif's ESP-IDF extension. In Extensions, install **ESP-IDF** by **Espressif Systems**, identifier `espressif.esp-idf-extension`, version **2.3.0**. In the extension gear menu choose **Install Another Version...** and select 2.3.0 if needed, then disable auto-update for this extension to retain the pin. Verify the identifier and version in its Installation panel. The extension version is separate from ESP-IDF framework version 5.4.4. Open **View > Command Palette** and select **ESP-IDF: Open ESP-IDF Installation Manager**. Install ESP-IDF **5.4.4** and its ESP32-S3 tools. Select **ESP-IDF: Select Current ESP-IDF Version** and choose that exact installation. Record the extension version as well as the IDF version. Do not install ADF for this project.

Extract the complete companion project and use **File > Open Folder** to open `korvo_mic_lab`. Trust only the extracted project whose source has been reviewed. The supplied `.vscode/settings.json` selects the native-USB `build-usb` profile. Use this profile only after verifying the native USB hardware path. For an unmodified stock board, replace those settings with the stock profile below before the first build.

Use **ESP-IDF: Set Espressif Device Target**, selecting **esp32s3**. This is a build-target choice, not a wiring change. Use **ESP-IDF: Build your Project**. Component Manager downloads codec driver 1.6.2 and uses the supplied lock file. Build output should report completion and create the matching ELF and BIN in the selected build directory. These files passed an actual cross-build; the VS Code UI workflow itself has not been executed for this edition.

### Two independent configurations

Use **Preferences: Open Workspace Settings (JSON)** to inspect the project settings. Native USB is the supplied default:

```json
{
  "idf.buildPath": "${workspaceFolder}/build-usb",
  "idf.sdkconfigFilePath": "${workspaceFolder}/sdkconfig.usb",
  "idf.sdkconfigDefaults": ["sdkconfig.usb.defaults"],
  "idf.openOcdConfigs": ["board/esp32s3-builtin.cfg"],
  "idf.flashType": "UART",
  "idf.flashBaudRate": "460800"
}
```

For stock CP2102N/UART, use `build` as the build directory, `sdkconfig` as the configuration file, and `["sdkconfig.defaults"]` as defaults. Do not reuse an existing generated configuration from a different profile. Defaults initialize a new configuration; they do not reliably overwrite a previously generated file. If a stale configuration exists, archive it through VS Code Explorer and remove only that generated configuration/build directory before rebuilding. Never remove source or the pinned lock file.

The flash method name UART refers to the serial bootloader transport used by the extension; the native USB Serial/JTAG serial interface also supports serial flashing. It does not select the application's logging channel. That comes from the chosen sdkconfig defaults.

## Board modification and native USB console profile

For the board-modification procedure and IDE demonstration, use the FirmwareMine video guide: [ESP32-S3-Korvo-2 native USB/JTAG modification](https://www.youtube.com/watch?v=GXsBVtyfmGY). Review the full procedure before attempting rework. Disconnect all power, USB cables and batteries before soldering; confirm the board revision and schematic, and use qualified rework support if necessary. The V3.1.2 schematic identifies the stock J6 path through R181/R182 to CP2102N and the alternate R394/R395 path to native USB. Do not infer resistor placement or soldering steps from the conceptual connection illustration in this chapter. Verify the completed routing and inspect for shorts before applying power. If native USB routing is already present, do not repeat the modification.

The video demonstrates IDF4.4/ADF. Use it for the hardware modification and debugging concepts, not this lab's software dependency versions. This project requires IDF5.4.4 without ADF. The stock profile uses UART0 logs; after verifying native USB routing, use the separate native-USB console configuration below:

After confirming the native USB modification, keep the supplied `build-usb` settings. For a stock board choose the stock settings instead. In **ESP-IDF: Select Port to Use (COM, tty, usbserial)**, select the actual device entry. Native USB uses the Espressif USB Serial/JTAG serial interface; stock uses CP2102N. Unplug/reconnect the data cable to identify the changing entry. Close other serial applications. A missing entry requires driver, permission, cable and routing checks, not repeated soldering.

### Check flash capacity before writing

This project's explicit flash configuration is 8 MB. In Workspace Settings (JSON), set `idf.customTask` to `python -m esptool --chip esp32s3 -p PORT flash_id`, replacing `PORT` with the selected real serial-port name. Then choose **ESP-IDF: Execute Custom Task**. This is a read-only identification operation launched by VS Code; do not type it into a separate terminal. Confirm that the detected flash capacity is at least 8 MB. Stop if it is smaller or cannot be established. Do not change write sizes or force flashing to bypass this check.

### Flash, monitor and retain evidence

Select **ESP-IDF: Flash Your Project**, using the serial/UART method, then **ESP-IDF: Monitor Device**. The extension output identifies the build directory and port; verify both before allowing a write. Flashing replaces the prior app/partition layout. No erase-flash or eFuse operation is needed. If transfer fails, set Flash Baud Rate to 115200 and retry. For manual download mode, hold BOOT, press/release RESET, then release BOOT. Do not bridge pins. Stop the monitor using its VS Code terminal stop control before opening another connection.

## What must happen, and what is not predetermined

At startup, `SELFTEST PASS` confirms an exact built-in alternating half-scale fixture. It does not validate the microphone. Then the app probes ES7210 at 7-bit I2C address 0x40, configures its MIC1/MIC2 inputs and stereo 16-bit 16 kHz capture, sets input gain 24 dB and discards the first sixteen 256-frame blocks (nominal 0.256 s).

Each block is 256 stereo frames, 1,024 bytes, nominally 16 ms. Every 64 accepted blocks it prints cumulative block/error/overflow counters, elapsed time, maximum feature-compute time and free/minimum internal heap. It also prints the latest block's six outputs for each slot: normalized mean, total RMS, mean-removed RMS, peak, mean absolute adjacent change, and count of samples equal to signed-int16 endpoints. Output values depend on the room and hardware, so no fabricated numeric “expected microphone log” is supplied.

Speak near the board at normal volume, then pause. Both slots should show changes correlated with sound. Avoid shouting or tapping the microphones. Do not assume channel0 is physical left until you test it. Endpoint counts are a digital clipping clue, not proof of absence of analog clipping. The app is not an SPL meter. Features are normalized digital full-scale units, not pascals or calibrated dB SPL.

Errors/short reads discard that incomplete block, with no feature decision emitted for it. Each feature block is independent. The overflow ISR increments a counter; nonzero/increasing overflow means data continuity is not established even if some blocks arrive. The app does not repair missing samples. Elapsed time versus nominal sample count is only a coarse sanity check, not a sample-clock calibration. Report persistent faults before attaching an ML classifier.

## Acceptance run, first board session

1. Photograph the board revision/module label and connection labels. Keep private surroundings out of frame.
2. Save the complete boot-to-60-second serial text, including self-test, codec setup and counters.
3. Record 10 seconds of room quiet, 10 seconds of normal speech, then quiet again. Note their approximate log times. No raw audio is retained by this app.
4. Check for increasing blocks, zero read/overflow faults, reasonable sound-correlated feature changes and no repeated resets.
5. Record observed feature max time and heap values as BOARD MEASUREMENTS only after running. No such numbers are claimed yet.
6. Share the log and any error text, with your actual OS/port/board revision. That evidence decides the next code change.

## Host tests in VS Code

These tests are independent of the ESP-IDF compiler. On a Linux host with GCC installed, choose **Terminal > Run Task > FirmwareMine: feature host tests**. The supplied task builds the feature fixture with the host compiler and runs it. It does not flash hardware. Native Windows users should use a separate VS Code WSL window with a Linux GCC installation for this host-only task, not mix that task with their Windows IDF environment. The previously recorded ordinary and sanitizer test results are build evidence, not a claim that the UI task was physically exercised.

## Practical extensions after capture passes

Measure the effect of input gain, channel choice and background noise while retaining exact settings. Add a ring buffer and capture-quality contract before streaming spectrograms. Do not feed these microphone features into the earlier synthetic machine-motion model and call the output a sound label. Real acoustic training requires its own recordings, labels, normalization and held-out evaluation.

## Prebuilt profiles

This source repository does not include prebuilt firmware. Build and flash the selected profile in VS Code so the firmware and debugging ELF match. A successful build does not replace the flash-capacity/module check or hardware acceptance run.

Extension version source: https://github.com/espressif/vscode-esp-idf-extension/tree/v2.3.0
