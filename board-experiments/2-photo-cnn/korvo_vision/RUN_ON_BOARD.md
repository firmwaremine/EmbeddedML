# Replay before camera

This is a slow float diagnostic for the modified native-USB ESP32-S3-Korvo-2 V3.1. It replaces your existing application and partition table. Keep any firmware/data you need before flashing. Do not erase flash or change eFuses. Do not connect new camera wiring, a battery or a speaker for this test.

1. In VS Code install/select Espressif ESP-IDF extension 2.3.0 and ESP-IDF 5.4.4. Open this korvo_vision folder as the project, then select your native-USB serial port.
2. Verify your module has at least 8MB flash and octal PSRAM. The stock Korvo product page says 16MB flash +8MB PSRAM, but your modified hardware must be checked. Use the extension's ESP-IDF terminal and its esptool flash-id command, or provide the module label/result for review. Stop if flash is below8MB or PSRAM type is uncertain. Do not force a binary write. Flash capacity is intentionally capped at8MB in this experiment.
3. Choose ESP-IDF: Build your project. The partition is a single7MiB factory app, without OTA. It is a diagnostic layout, not an update system.
4. When ready to replace the old application, choose ESP-IDF: Flash your project, using the selected native-USB port and UART flashing method. Choose ESP-IDF: Monitor your device. Do not interpret the generic SDK C++ linker driver as a C++ inference engine. All project inference/application source is C; the tiny assembly file only embeds aligned read-only float blobs.
5. Save the complete boot log. Confirm PSRAM initializes and the replay prints PSRAM_BYTES, three TRIAL lines, five logits, duration_us, free internal/PSRAM heap and stack watermark. PASS requires the expected class and final-logit absolute error below0.01. A successful build is not this result.
6. This intentionally slow synchronous reference disables the task watchdog. The interrupt watchdog is not disabled. Do not reuse that choice in production. The boot note states this limitation. Camera/microphone/display/radio are not initialized. GPIO48 keeps the speaker amplifier disabled.
7. If replay passes, return the complete log and module label before adding a camera. If memory/init fails or numerical parity fails, stop at that earliest boundary. No target speed or accuracy claim should be entered in the book before reviewing actual results.

The prebuilt folder contains the app/bootloader/partition binaries as evidence. Rebuild and flash through the extension so the selected SDK configuration and flashing offsets remain together. Do not flash a bare app binary to a guessed address.

## Camera gate

The supplied photo shows JQ-V360-F100 V3 on a bare flex camera. Its sensor/contact map is not established from that face. Obtain contact-side/socket evidence or the supplier pinout. Korvo's documented DVP bus uses GPIO13/47/14/3/12/42/41/39 for data0..7, GPIO21 VSYNC, GPIO38 HREF, GPIO11 PCLK, GPIO40 XCLK, and GPIO17/18 SCCB. This is a board-side reference, not proof that an arbitrary camera flex matches it. Check reset/power-down and the board IO expander too. A supported sensor ID probe and a saved captured frame come before CNN output.

Once compatible: inspect color order/orientation/stride, preserve an actual frame, compare its preprocessing on host and target, then run inference. Current C inference accepts normalized96x96 NCHW float input only. Pillow currently performs the flower crop/resize. A camera preprocessing implementation still needs exact parity, including antialiasing on downsampling. Do not substitute an unverified bilinear resize and claim end-to-end equivalence.
