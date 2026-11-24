# Korvo debugging: distinguish UART from JTAG

The ESP32-S3 chip includes USB Serial/JTAG. That does NOT mean every board's USB connector is wired to it. Stock Korvo-2 V3.1 has a CP2102N USB-to-UART path plus dedicated USB power. The V3.1.2 schematic shows J6 USB data through R181/R182 to CP2102N, while alternate R394/R395 paths to the S3 USB nets are marked not fitted. Native USB signals are GPIO19 D- and GPIO20 D+; the board guide marks these reserved.

Do not connect a second USB cable expecting stock UART to provide OpenOCD single-stepping. Review the linked modification video and revision-specific schematic before any resistor rework. Do not solder a breakout or wire an external debug probe until access points and conflicts are reviewed. This package supplies no unverified physical debug wiring. External GPIO JTAG is not assumed spare either: camera-related pins can conflict.

## Practical debug lab A: exact feature replay, no board needed

Open the project in a separate VS Code Linux/WSL window with the Microsoft C/C++ extension and host GCC/GDB installed. Run **Terminal > Run Task > FirmwareMine: feature host tests**. In **Run and Debug**, select the supplied **FirmwareMine host feature fixture** configuration. Set a source breakpoint in `mic_extract`, press F5, inspect `p`, `n`, `channels` and `selected`, and step through the deterministic fixture. This is host stepping, not hardware stepping.

## Practical debug lab B: UART fault diagnosis on the board

1. Keep default panic/backtrace behavior in the first capture build.
2. Flash/monitor via CP2102N, save complete panic text if any. IDF Monitor uses the matching ELF to decode addresses; keep build/korvo_mic_lab.elf from the exact flashed build.
3. Use counters to isolate I2C probe failures, capture timeouts, DMA overflow or feature self-test failures before changing ML code.
4. Optional post-mortem GDB: use ESP-IDF: SDK Configuration Editor in a separate build configuration, include the esp_gdbstub component, and select Component config > ESP System Settings > Panic handler > GDBStub. Rebuild/flash. On a fatal error IDF Monitor can enter GDB to inspect registers/stack. In this pinned IDF panic-stub mode it is read-only/post-mortem, NOT normal breakpoint/continue/single-step debugging. No deliberate-crash firmware is included in lab1.

## Conditional hardware stepping, not yet physically verified

Once a safe native GPIO19/20 USB access route is established on YOUR board, the S3's built-in JTAG can support full OpenOCD/GDB debugging without a separate JTAG probe. Use the matching IDF OpenOCD target configuration and driver setup. That access may require hardware work on Korvo; it is not an instruction to use its stock power/UART connectors as native USB. No eFuse change is required by this lab.

Official references:
https://docs.espressif.com/projects/esp-idf/en/v5.4.4/esp32s3/api-guides/jtag-debugging/configure-builtin-jtag.html
https://docs.espressif.com/projects/esp-idf/en/v5.4.4/esp32s3/api-guides/fatal-errors.html
https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-Korvo-2_V3.1.2_20240116.pdf

## Modified-board native USB/JTAG: full step-debug lab

Follow the [FirmwareMine board-modification video guide](https://www.youtube.com/watch?v=GXsBVtyfmGY) for the native USB/JTAG hardware procedure. Read the modification precautions in the preceding setup section. Stock boards do not provide this routing at J6. Use this lab only after the physical native USB path has been verified. The video uses IDF4.4/ADF; the firmware in this book uses IDF5.4.4 without ADF.

1. In VS Code keep the `build-usb` profile. Open **ESP-IDF: SDK Configuration Editor**, choose compiler optimization **Debug (-Og)** and save. Use **ESP-IDF: Build your Project**, then flash the matching binary. Do not use a stale ELF from a release build.
2. Run **ESP-IDF: Select Port to Use (COM, tty, usbserial)**. Use **ESP-IDF: Select OpenOCD Board Configuration** and select the ESP32-S3 built-in USB JTAG configuration (`board/esp32s3-builtin.cfg`). Install the documented USB JTAG driver/permissions for the operating system. A serial port alone is not proof that the JTAG interface is accessible.
3. The supplied `.vscode/launch.json` includes **FirmwareMine ESP32-S3 native USB** with the matching `build-usb/korvo_mic_lab.elf`. In Run and Debug select that configuration. Set source breakpoints in `app_main`, `mic_features_selftest` and `mic_extract`; choose **Run > Start Debugging** or F5.
4. Inspect the alternating half-scale fixture before microphone capture. Use Step Over/Step Into and Variables/Watch in VS Code. See **View > Output > ESP-IDF** for OpenOCD messages and **Debug Console** for GDB. The book does not claim a physical IDE session has passed.
5. Halting capture can cause overflow, stale buffers or watchdog resets. Stop debugging and restart without breakpoints before the 60-second acceptance run. Do not report single-stepped timings as performance measurements. Close other debugger/monitor sessions before retrying.

Evidence to retain: a breakpoint/variable view from the physical board, the exact ELF and build configuration, and a clean uninterrupted acceptance log. Cross-build results alone do not verify hardware debugging or capture performance.

Verified command reference: https://docs.espressif.com/projects/esp-idf/en/v5.4.4/esp32s3/api-guides/jtag-debugging/using-debugger.html

VS Code references:
https://docs.espressif.com/projects/vscode-esp-idf-extension/en/latest/installation.html
https://docs.espressif.com/projects/vscode-esp-idf-extension/en/latest/debugproject.html
https://docs.espressif.com/projects/vscode-esp-idf-extension/en/latest/settings.html
https://docs.espressif.com/projects/vscode-esp-idf-extension/en/latest/additionalfeatures/project-configuration.html
