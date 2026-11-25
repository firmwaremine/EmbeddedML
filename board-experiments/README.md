# Korvo board experiments

Three experiments and one measurement worksheet for the **ESP32-S3-Korvo-2 V3.1** (native-USB modification), written in pure C on ESP-IDF 5.3.6 (the version installed on the target workstation). They go with the book *From Firmware to Machine Learning*.

**Status: cross-built, not yet run on a board.** Every number below comes from a computer or a compiler. No board speed, accuracy, camera or power result exists until you run these and send back the logs.

**Start here: [STEP_BY_STEP.md](STEP_BY_STEP.md).** Numbered steps for setup, each run, expected output, what to save and when to stop. A shorter PDF version is in [docs/Korvo_Board_Run_Guide.pdf](docs/Korvo_Board_Run_Guide.pdf).

## The four folders

| Order | Folder | Open in VS Code | What it does | Gate you must see |
| --- | --- | --- | --- | --- |
| 1 | [1-speech](1-speech/) | `1-speech/korvo_kws` | Microphone to a four-word event: go, no, stop, yes | `REPLAY ... PASS=1` in the boot log |
| 2 | [2-photo-cnn](2-photo-cnn/) | `2-photo-cnn/korvo_vision` | Runs a stored flower photo through a pure C CNN, three times. No camera | `PSRAM_BYTES`, three `TRIAL` lines, `PASS` |
| 3 | [3-camera-health](3-camera-health/) | `3-camera-health/korvo_camera_health` | Reads the camera sensor ID and saves a real frame | `SENSOR_PID=0x3660`, then `capture.jpg` opens |
| 4 | [4-power-measurement](4-power-measurement/) | not firmware | Worksheet for a USB power meter (UNI-T UT658DUAL) | Do after 1 to 3 pass |

Open the project folder itself as the VS Code workspace, never its `main` subfolder.

## What you need

- ESP32-S3-Korvo-2 V3.1 with the native-USB modification described in the earlier lab. No battery, no speaker, no new wiring.
- VS Code with the official **Espressif ESP-IDF** extension 2.3.0, and ESP-IDF **5.3.6**.
- At least 8 MB flash and octal PSRAM. Check with the extension's `esptool flash-id` before flashing. Stop if it is below 8 MB or the PSRAM type is unclear.
- For the camera: the supplied OV3660-class flex camera (marking JQ-V360-F100 V3), installed with all power disconnected, in its original orientation, in the 24-contact camera connector (not the 20-contact LCD one).
- Python 3 for `extract_frame.py`.

## Run order

1. **Prepare.** Check the board revision, flash and PSRAM. Save anything you need from the current firmware: every flash replaces the application and partition table. Do not erase the whole flash. Do not touch eFuses.
2. **Speech.** In `korvo_kws`: Set Espressif Device Target (ESP32-S3), Select Port (native USB Serial/JTAG), Build, Flash, Monitor. Save the full log as `run-01.txt`. Check the REPLAY line first, then capture health, then run the 20-per-word trial using `measurements/trials.csv`.
3. **Photo CNN.** In `korvo_vision`: Build, Flash, Monitor. Save the full log. PASS needs the expected class and a final-logit error below 0.01.
4. **Camera.** In `korvo_camera_health`: Build, Flash, Monitor with logging on. Save the full log as `monitor.log`, then run `extract_frame.py` on it. It checks length, CRC32 and JPEG markers before it writes `capture.jpg`. Open the image.
5. **Power.** Follow [4-power-measurement/MEASUREMENT_GUIDE.md](4-power-measurement/MEASUREMENT_GUIDE.md).

Each project has its own `RUN_ON_BOARD.md` with the detailed steps and stop conditions.

## Stop conditions

Stop and keep the full log if any of these happen. Do not work around them.

- Flash below 8 MB or PSRAM unclear.
- Build error.
- `PASS=0` in the speech REPLAY or the CNN replay.
- Repeated overflow during the speech run.
- Camera PID is not `0x3660`.
- You are not sure how the camera flex is oriented.

## What to send back

| Stage | Files |
| --- | --- |
| Prep | flash-id output, board revision, USB port, photo of the connection |
| Speech | `run-01.txt`, completed `trials.csv`, negative-exposure duration, gain, distance, speaker count |
| Photo CNN | full boot log and module label |
| Camera | `monitor.log` and `capture.jpg` |
| Power | meter model, start and end photos, routing photo, filled `power_runs.csv`, only if measured |

Partial runs and failures are useful. A successful flash or a photo of the board is not a measurement.

## What has been verified, and where

| Claim | Where it was checked |
| --- | --- |
| Speech model: 82.93% clip accuracy on 1,377 held-out clips, speaker-disjoint split (5,384 / 1,239 / 1,377). Pure C matches the training code on 1,377 of 1,377 labels | Computer |
| Speech event policy found 55 of 80 targets in a constructed 160-clip stream, with 25 misses and 27 unmatched events. It influenced the design, so it is a development check, not a final benchmark | Computer |
| CNN: 80.90% on 555 held-out flower photos. All 156 graph nodes match PyTorch on all 555 images. Max output error 0.0000465 | Computer |
| CNN memory: 405,504-byte arena, 3,719,572-byte float weights, 4,023,984-byte app | Build output |
| Camera diagnostic cross-builds, app 228,208 bytes. Frame-extraction tests pass on generated JPEGs | Computer |
| Anything on the board: latency, accuracy, camera frames, power | **Not measured yet** |

## Limits

- The speech model has four target words. The fifth label, `other`, holds down, left, right, up and declared synthetic noise. It does not prove rejection of arbitrary speech, music or noise. This is not a reliable voice controller.
- The CNN replay disables the task watchdog on purpose, because the float reference is slow. That is a diagnostic choice, not a production setting.
- The CNN does not read the camera yet. Host and target image preprocessing parity is still to do. After that: CNN integration, then a live-scene test.
- The three-inference CNN replay is not a timed idle-versus-work benchmark. Extend it with logged timed phases before any energy comparison.
- Camera sensor: the kit camera is expected to be OV3660 from Espressif's board support. The flex marking alone does not name the sensor. The runtime PID check decides.

## SDK version: ESP-IDF 5.3.6

All three apps were rebuilt and checked against ESP-IDF **5.3.6** (tag `v5.3.6`), the version installed on the target workstation. Three changes were needed compared with the earlier 5.4.4 build:

| Project | Change for 5.3.6 |
| --- | --- |
| korvo_kws | `main/idf_component.yml` now pins `idf: "==5.3.6"` (it pinned 5.4.4) and `dependencies.lock` was regenerated. The audio codec component stays at `esp_codec_dev` 1.6.2. |
| korvo_vision | `main/main.c` relaxes `-Wpedantic` only around the `driver/gpio.h` include, because 5.3.6 ships an empty struct in `esp_etm.h`. The project code stays under `-Wall -Wextra -Werror -Wpedantic`. |
| korvo_camera_health | The camera driver uses its legacy SCCB driver `sccb.c`. The newer `sccb-ng.c` needs ESP-IDF 5.4. This changes the camera's I2C control path, and it has not run on hardware. |

Do not mix SDK versions between projects. If you install another ESP-IDF, select 5.3.6 with **ESP-IDF: Select Current ESP-IDF Version** before building.

## Prebuilt binaries

`prebuilt/` folders hold the cross-built binaries as evidence, with `SHA256SUMS`. Rebuild and flash through the ESP-IDF extension so configuration and flash offsets stay together. Do not flash a bare `.bin` to a guessed address.

| Project | App size | SHA-256 |
| --- | --- | --- |
| korvo_kws (native USB) | 623,984 bytes | `81885532ef02852a68b912cf9c49fad5af5244ee06a98f4457d1a4ce4e3580ba` |
| korvo_vision | 4,023,984 bytes | `8fcbd304058e078c4f024873c5845b4ac0279c8575b3d65af476f0161e4aa6b3` |
| korvo_camera_health | 228,208 bytes | `d9e8a58538da808d616066b24d34d95c87d9d5922ae85b356efad3840f9f1fce` |

## Data and licenses

- The full training data is in [../realdata](../realdata/) (3,670 flower photos, 8,000 speech WAVs, hashes, split manifests, scripts). The `2-photo-cnn` folder does not duplicate the photos.
- Original FirmwareMine code: MIT, see the repository `LICENSE`.
- Third-party material keeps its own terms: Speech Commands (CC BY 4.0), flower photos (CC BY 2.0 per-image credits), MobileNetV3-Small pretrained values via torchvision (BSD notice), the Espressif `esp32-camera` driver (Apache 2.0, pinned to `f5257073e2a41c945eb618570a76063b8e4eed18`). See `THIRD_PARTY.md`, `FLOWER_ATTRIBUTION.txt`, `TORCHVISION_LICENSE.txt` and `../realdata/README.md`.
- The MobileNetV3-Small weights are pretrained third-party values plus a newly trained head. They are not trained from scratch.
